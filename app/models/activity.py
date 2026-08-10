"""
Activity & Notification Models
===============================
Tracks user actions and system notifications.
"""
from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    """User notification."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='info')  # info, success, warning, error
    icon = db.Column(db.String(50), default='fa-bell')
    link = db.Column(db.String(300), default='')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def create(user_id, title, message, type='info', icon='fa-bell', link=''):
        """Factory method to create a notification."""
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            icon=icon,
            link=link
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    def __repr__(self):
        return f'<Notification {self.title}>'


class ActivityLog(db.Model):
    """User activity log."""
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    icon = db.Column(db.String(50), default='fa-circle')
    color = db.Column(db.String(20), default='primary')
    ip_address = db.Column(db.String(50), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def log(user_id, action, description='', icon='fa-circle', color='primary'):
        """Factory method to create an activity log entry."""
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            icon=icon,
            color=color
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

    def __repr__(self):
        return f'<ActivityLog {self.action}>'
