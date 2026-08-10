"""
Utility Helpers
===============
Common helper functions used across the application.
"""
import os
import uuid
import re
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file):
    """Save uploaded file and return the filename."""
    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        ext = original_name.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}_{int(datetime.utcnow().timestamp())}.{ext}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        return unique_name, original_name
    return None, None


def save_avatar(file, user_id):
    """Save user avatar image."""
    if file:
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
        if ext not in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            return None
        filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        avatars_dir = os.path.join(current_app.static_folder, 'img', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        filepath = os.path.join(avatars_dir, filename)
        file.save(filepath)
        return filename
    return None


def get_file_size(filename):
    """Get file size in KB."""
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return round(os.path.getsize(filepath) / 1024, 2)
    return 0


def format_date(dt):
    """Format datetime for display."""
    if dt is None:
        return 'N/A'
    now = datetime.utcnow()
    diff = now - dt
    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            if minutes == 0:
                return 'Just now'
            return f'{minutes}m ago'
        return f'{hours}h ago'
    elif diff.days == 1:
        return 'Yesterday'
    elif diff.days < 7:
        return f'{diff.days}d ago'
    else:
        return dt.strftime('%b %d, %Y')


def get_score_color(score):
    """Return color class based on score value."""
    if score >= 80:
        return 'excellent'
    elif score >= 60:
        return 'good'
    elif score >= 40:
        return 'average'
    else:
        return 'poor'


def get_score_label(score):
    """Return label based on score value."""
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    elif score >= 40:
        return 'Average'
    else:
        return 'Needs Improvement'


def sanitize_text(text):
    """Clean and sanitize text input."""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_report_filename(user_id, resume_name):
    """Generate unique report filename."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    safe_name = re.sub(r'[^\w\-_.]', '_', resume_name.rsplit('.', 1)[0])
    return f"report_{user_id}_{safe_name}_{timestamp}.pdf"


def truncate_text(text, length=100):
    """Truncate text to specified length with ellipsis."""
    if not text or len(text) <= length:
        return text or ''
    return text[:length].rsplit(' ', 1)[0] + '...'
