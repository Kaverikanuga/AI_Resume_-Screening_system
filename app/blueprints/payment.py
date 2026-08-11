"""
ResumeAI Pro - Razorpay Payment Blueprint

Razorpay TEST MODE payment flow.

IMPORTANT:
- Razorpay secret is NEVER sent to the browser.
- Payment amount is decided server-side.
- Payment signature is verified server-side.
"""

import os
import hmac
import hashlib
import uuid

import razorpay

from flask import (
    Blueprint,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
)

from flask_login import login_required, current_user

from ..extensions import db
from ..models import Payment, ActivityLog, Notification


# ============================================================
# BLUEPRINT
# ============================================================

payment_bp = Blueprint(
    "payment_bp",
    __name__,
    url_prefix="/payment",
)


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
            "Please check RAZORPAY_KEY_ID and "
            "RAZORPAY_KEY_SECRET in environment variables."
        )

    return razorpay.Client(
        auth=(key_id, key_secret)
    )


# ============================================================
# SERVER-SIDE PLAN PRICES
# ============================================================

PLAN_AMOUNTS = {
    # Amount is in paise.
    # 5900  = ₹59
    # 9900  = ₹99
    "pro": 5900,
    "business": 9900,
}


# ============================================================
# CREATE RAZORPAY ORDER
# ============================================================

@payment_bp.route("/create-order", methods=["POST"])
@login_required
def create_order():

    try:
        data = request.get_json(silent=True) or {}

        plan = str(
            data.get("plan", "")
        ).strip().lower()

        # ----------------------------------------------------
        # Validate plan
        # ----------------------------------------------------

        if plan not in PLAN_AMOUNTS:
            return jsonify({
                "success": False,
                "error": "Invalid plan selected."
            }), 400

        # ----------------------------------------------------
        # IMPORTANT:
        # Never trust amount coming from browser.
        # Amount is taken from PLAN_AMOUNTS above.
        # ----------------------------------------------------

        amount = int(
            PLAN_AMOUNTS[plan]
        )

        # ----------------------------------------------------
        # Get Razorpay client
        # ----------------------------------------------------

        client = get_razorpay_client()

        # ----------------------------------------------------
        # Razorpay order data
        # ----------------------------------------------------

        order_data = {
            "amount": amount,
            "currency": "INR",

            "receipt": (
                f"rcpt_{uuid.uuid4().hex[:12]}"
            ),

            "notes": {
                "plan": plan,
                "user_id": str(current_user.id),
                "email": current_user.email or "",
            }
        }

        # ----------------------------------------------------
        # Create Razorpay order
        # ----------------------------------------------------

        order = client.order.create(
            data=order_data
        )

        # ----------------------------------------------------
        # Return only public information
        # ----------------------------------------------------

        key_id = os.environ.get(
            "RAZORPAY_KEY_ID",
            ""
        ).strip()

        return jsonify({
            "success": True,

            "order_id": order["id"],

            "amount": amount,

            "currency": "INR",

            "key_id": key_id,

            "plan": plan,

        }), 200

    except Exception as e:

        current_app.logger.exception(
            "Razorpay order creation failed"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# VERIFY RAZORPAY PAYMENT
# ============================================================

@payment_bp.route("/verify", methods=["POST"])
@login_required
def verify_payment():

    try:

        data = request.get_json(silent=True) or {}

        razorpay_order_id = str(
            data.get("razorpay_order_id", "")
        ).strip()

        razorpay_payment_id = str(
            data.get("razorpay_payment_id", "")
        ).strip()

        razorpay_signature = str(
            data.get("razorpay_signature", "")
        ).strip()

        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        if not razorpay_order_id:
            return jsonify({
                "success": False,
                "error": "Missing Razorpay order ID."
            }), 400

        if not razorpay_payment_id:
            return jsonify({
                "success": False,
                "error": "Missing Razorpay payment ID."
            }), 400

        if not razorpay_signature:
            return jsonify({
                "success": False,
                "error": "Missing Razorpay signature."
            }), 400

        # ----------------------------------------------------
        # Get secret
        # ----------------------------------------------------

        key_secret = os.environ.get(
            "RAZORPAY_KEY_SECRET",
            ""
        ).strip()

        if not key_secret:
            raise RuntimeError(
                "RAZORPAY_KEY_SECRET is not configured."
            )

        # ----------------------------------------------------
        # Signature verification
        # ----------------------------------------------------

        generated_signature = hmac.new(
            key_secret.encode("utf-8"),

            (
                razorpay_order_id
                + "|"
                + razorpay_payment_id
            ).encode("utf-8"),

            hashlib.sha256
        ).hexdigest()

        # ----------------------------------------------------
        # Secure comparison
        # ----------------------------------------------------

        if not hmac.compare_digest(
            generated_signature,
            razorpay_signature
        ):

            current_app.logger.warning(
                "Invalid Razorpay signature for user %s",
                current_user.id
            )

            return jsonify({
                "success": False,
                "error": "Payment verification failed."
            }), 400

        # ----------------------------------------------------
        # Payment verified successfully
        # ----------------------------------------------------

        current_app.logger.info(
            "Razorpay payment verified: %s",
            razorpay_payment_id
        )

        # ----------------------------------------------------
        # Try to save payment information
        # ----------------------------------------------------

        try:

            payment = Payment()

            # Set fields only if your model supports them.
            if hasattr(payment, "user_id"):
                payment.user_id = current_user.id

            if hasattr(payment, "razorpay_order_id"):
                payment.razorpay_order_id = (
                    razorpay_order_id
                )

            if hasattr(payment, "razorpay_payment_id"):
                payment.razorpay_payment_id = (
                    razorpay_payment_id
                )

            if hasattr(payment, "razorpay_signature"):
                payment.razorpay_signature = (
                    razorpay_signature
                )

            if hasattr(payment, "status"):
                payment.status = "success"

            if hasattr(payment, "payment_status"):
                payment.payment_status = "success"

            db.session.add(payment)

            db.session.commit()

        except Exception:

            # Do not make a verified payment look failed
            # just because optional database fields differ.
            db.session.rollback()

            current_app.logger.exception(
                "Payment verified but database save failed."
            )

        # ----------------------------------------------------
        # Activity log
        # ----------------------------------------------------

        try:

            activity = ActivityLog()

            if hasattr(activity, "user_id"):
                activity.user_id = current_user.id

            if hasattr(activity, "action"):
                activity.action = (
                    "Razorpay payment successful"
                )

            if hasattr(activity, "description"):
                activity.description = (
                    f"Payment ID: "
                    f"{razorpay_payment_id}"
                )

            db.session.add(activity)
            db.session.commit()

        except Exception:

            db.session.rollback()

        # ----------------------------------------------------
        # Notification
        # ----------------------------------------------------

        try:

            notification = Notification()

            if hasattr(notification, "user_id"):
                notification.user_id = current_user.id

            if hasattr(notification, "title"):
                notification.title = (
                    "Payment Successful"
                )

            if hasattr(notification, "message"):
                notification.message = (
                    "Your Razorpay payment was "
                    "successfully completed."
                )

            db.session.add(notification)
            db.session.commit()

        except Exception:

            db.session.rollback()

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Payment verified successfully.",
            "payment_id": razorpay_payment_id,
            "order_id": razorpay_order_id,
        }), 200

    except Exception as e:

        current_app.logger.exception(
            "Razorpay payment verification error"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# PAYMENT SUCCESS PAGE
# ============================================================

@payment_bp.route("/success")
@login_required
def payment_success():

    return redirect(
        url_for("dashboard.dashboard")
    )


# ============================================================
# PAYMENT CANCEL PAGE
# ============================================================

@payment_bp.route("/cancel")
@login_required
def payment_cancel():

    flash(
        "Payment was cancelled.",
        "warning"
    )

    return redirect(
        url_for("dashboard.dashboard")
    )


# ============================================================
# RAZORPAY PUBLIC KEY
# ============================================================

@payment_bp.route("/config", methods=["GET"])
@login_required
def payment_config():

    key_id = os.environ.get(
        "RAZORPAY_KEY_ID",
        ""
    ).strip()

    if not key_id:

        return jsonify({
            "success": False,
            "error": "Razorpay key is not configured."
        }), 500

    return jsonify({
        "success": True,
        "key_id": key_id
    }), 200