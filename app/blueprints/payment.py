"""
ResumeAI Pro - Razorpay Payment Blueprint

Razorpay TEST MODE payment flow.

IMPORTANT:
- Razorpay Key Secret is NEVER sent to the browser.
- Payment amounts are decided server-side.
- Payment signature is verified server-side.
"""

import os
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta

import razorpay

from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)

from flask_login import login_required, current_user

from ..extensions import db
from ..models import Payment, ActivityLog, Notification


payment_bp = Blueprint("payment", __name__)


# ============================================================
# RAZORPAY CLIENT
# ============================================================

def get_razorpay_client():
    """
    Create Razorpay client using TEST MODE credentials.

    Credentials are read from environment variables.
    The secret is NEVER returned to the browser.
    """

    key_id = os.environ.get("RAZORPAY_KEY_ID", "").strip()
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()

    if not key_id or not key_secret:
        raise RuntimeError(
            "Razorpay credentials are not configured. "
            "Please check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env"
        )

    return razorpay.Client(
        auth=(key_id, key_secret)
    )


# ============================================================
# SIGNATURE VERIFICATION
# ============================================================

def verify_razorpay_signature(
    order_id,
    payment_id,
    signature
):
    """
    Verify Razorpay payment signature using HMAC-SHA256.

    Razorpay signature is calculated using:

        order_id|payment_id

    and the Razorpay Key Secret.
    """

    key_secret = os.environ.get(
        "RAZORPAY_KEY_SECRET",
        ""
    ).strip()

    if not key_secret:
        current_app.logger.error(
            "RAZORPAY_KEY_SECRET is missing."
        )
        return False

    payload = (
        f"{order_id}|{payment_id}"
    ).encode("utf-8")

    expected_signature = hmac.new(
        key_secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature
    )


# ============================================================
# SELECT PLAN
# ============================================================

@payment_bp.route("/select-plan", methods=["POST"])
def select_plan():
    """
    Store selected paid plan in session.

    Used when a guest clicks Choose Pro before login/signup.
    """

    data = request.get_json(silent=True) or {}

    plan = str(
        data.get("plan", "")
    ).strip().lower()

    plan_amounts = current_app.config.get(
        "RAZORPAY_PLAN_AMOUNTS",
        {
            "pro": 5900,
            "business": 9900,
        }
    )

    if plan not in plan_amounts:
        return jsonify({
            "error": "Invalid plan selected."
        }), 400

    session["pending_plan"] = plan
    session.permanent = True

    return jsonify({
        "status": "ok",
        "plan": plan
    })


# ============================================================
# CLEAR PLAN
# ============================================================

@payment_bp.route("/clear-plan", methods=["POST"])
def clear_plan():
    """
    Get the pending plan and then remove it from session.

    IMPORTANT:
    We must read the value BEFORE removing it.
    """

    pending_plan = session.get("pending_plan")

    # Remove it after reading.
    session.pop("pending_plan", None)

    return jsonify({
        "status": "ok",
        "pending_plan": pending_plan
    })


# ============================================================
# CREATE RAZORPAY ORDER
# ============================================================

@payment_bp.route("/create-order", methods=["POST"])
@login_required
def create_order():
    """
    Create Razorpay TEST MODE order.

    The amount is determined SERVER-SIDE.
    Browser cannot decide the payment amount.
    """

    data = request.get_json(silent=True) or {}

    plan = str(
        data.get("plan", "")
    ).strip().lower()

    plan_amounts = current_app.config.get(
        "RAZORPAY_PLAN_AMOUNTS",
        {
            "pro": 5900,
            "business": 9900,
        }
    )

    if plan not in plan_amounts:
        return jsonify({
            "error": "Invalid plan selected."
        }), 400

    # Amount in paise.
    amount = int(plan_amounts[plan])

    try:
        client = get_razorpay_client()

        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"rcpt_{uuid.uuid4().hex[:12]}",
            "notes": {
                "plan": plan,
                "user_id": str(current_user.id),
                "email": current_user.email,
            }
        }

        # Create Razorpay order.
        order = client.order.create(
            data=order_data
        )

        # Save order in database.
        payment_record = Payment(
            user_id=current_user.id,
            plan=plan,
            amount=amount,
            currency="INR",
            razorpay_order_id=order["id"],
            status="created",
        )

        db.session.add(payment_record)
        db.session.commit()

        # Only Key ID goes to browser.
        # NEVER send Key Secret.
        key_id = os.environ.get(
            "RAZORPAY_KEY_ID",
            ""
        ).strip()

        return jsonify({
            "key_id": key_id,
            "order_id": order["id"],
            "amount": amount,
            "currency": "INR",
            "plan": plan,
            "name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone or "",
        })

    except Exception as e:

        # Roll back database transaction if needed.
        db.session.rollback()

        current_app.logger.exception(
            "Razorpay order creation failed."
        )

        error_text = str(e)

        if (
            "Authentication failed" in error_text
            or "BadRequestError" in error_text
            or "401" in error_text
        ):
            return jsonify({
                "error": (
                    "Razorpay TEST MODE authentication failed. "
                    "Please check your TEST API keys in .env."
                )
            }), 500

        return jsonify({
            "error": (
                "Unable to create payment order. "
                "Please try again."
            )
        }), 500


# ============================================================
# VERIFY PAYMENT
# ============================================================

@payment_bp.route("/verify", methods=["POST"])
@login_required
def verify():
    """
    Verify Razorpay payment on server.

    Plan is activated ONLY after successful signature verification.
    """

    data = request.get_json(silent=True) or {}

    razorpay_payment_id = str(
        data.get("razorpay_payment_id", "")
    ).strip()

    razorpay_order_id = str(
        data.get("razorpay_order_id", "")
    ).strip()

    razorpay_signature = str(
        data.get("razorpay_signature", "")
    ).strip()

    plan = str(
        data.get("plan", "")
    ).strip().lower()

    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    if (
        not razorpay_payment_id
        or not razorpay_order_id
        or not razorpay_signature
    ):
        return jsonify({
            "error": "Missing payment details."
        }), 400

    # --------------------------------------------------------
    # Validate plan
    # --------------------------------------------------------

    if plan not in ("pro", "business"):
        return jsonify({
            "error": "Invalid plan."
        }), 400

    # --------------------------------------------------------
    # Find payment order
    # --------------------------------------------------------

    payment_record = Payment.query.filter_by(
        razorpay_order_id=razorpay_order_id,
        user_id=current_user.id
    ).first()

    if not payment_record:
        return jsonify({
            "error": "Payment order not found."
        }), 404

    # --------------------------------------------------------
    # Make sure submitted plan matches database
    # --------------------------------------------------------

    if payment_record.plan != plan:
        current_app.logger.warning(
            "Payment plan mismatch: order=%s database=%s submitted=%s",
            razorpay_order_id,
            payment_record.plan,
            plan
        )

        return jsonify({
            "error": "Payment plan mismatch."
        }), 400

    # --------------------------------------------------------
    # Prevent duplicate payment activation
    # --------------------------------------------------------

    if payment_record.status == "paid":

        return jsonify({
            "status": "already_paid",
            "message": "This payment has already been processed.",
            "redirect": url_for("dashboard.index")
        })

    # --------------------------------------------------------
    # Verify Razorpay signature
    # --------------------------------------------------------

    valid = verify_razorpay_signature(
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    )

    if not valid:

        payment_record.status = "failed"

        db.session.commit()

        current_app.logger.warning(
            "Invalid Razorpay signature for order %s",
            razorpay_order_id
        )

        return jsonify({
            "error": "Payment signature verification failed."
        }), 400

    # --------------------------------------------------------
    # Mark payment as paid
    # --------------------------------------------------------

    payment_record.razorpay_payment_id = (
        razorpay_payment_id
    )

    payment_record.status = "paid"

    db.session.commit()

    # --------------------------------------------------------
    # Activate plan
    # --------------------------------------------------------

    now = datetime.utcnow()

    expires_at = now + timedelta(
        days=30
    )

    current_user.plan = plan
    current_user.plan_expires_at = expires_at

    # Clear pending plan.
    session.pop(
        "pending_plan",
        None
    )

    db.session.commit()

    # --------------------------------------------------------
    # Activity log
    # --------------------------------------------------------

    ActivityLog.log(
        current_user.id,
        "Plan upgraded",
        description=(
            f"Activated {plan.capitalize()} "
            f"plan (TEST MODE) for 30 days"
        ),
        icon="fa-crown",
        color="success"
    )

    # --------------------------------------------------------
    # Notification
    # --------------------------------------------------------

    Notification.create(
        current_user.id,
        "Plan Activated",
        (
            f"Your {plan.capitalize()} plan is now active "
            f"(TEST MODE) for 30 days, until "
            f"{expires_at.strftime('%d %b %Y')}."
        ),
        type="success",
        icon="fa-crown",
        link=url_for("dashboard.index")
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return jsonify({
        "status": "success",
        "message": (
            f"Your {plan.capitalize()} plan "
            "has been activated successfully!"
        ),
        "redirect": url_for("dashboard.index")
    })