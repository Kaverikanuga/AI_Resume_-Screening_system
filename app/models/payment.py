"""
Payment Model
=============
Stores Razorpay payment records for paid plans.
The Razorpay Key Secret is NEVER stored - it stays in the server environment.
"""
from datetime import datetime
from ..extensions import db


class Payment(db.Model):
    """Razorpay payment record."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan = db.Column(db.String(20), nullable=False)        # pro, business
    amount = db.Column(db.Integer, nullable=False)         # amount in paise (e.g. 5900)
    currency = db.Column(db.String(10), default='INR')
    razorpay_order_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # payment_id is only set after a successful payment. It must be nullable
    # (NOT a non-null default) so that multiple 'created' orders can coexist
    # without violating the UNIQUE constraint on this column.
    razorpay_payment_id = db.Column(db.String(100), unique=True, nullable=True, default=None)
    status = db.Column(db.String(20), default='created')   # created, paid, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payment order={self.razorpay_order_id} plan={self.plan} status={self.status}>'
