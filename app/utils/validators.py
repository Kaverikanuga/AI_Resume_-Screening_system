"""
Form Validators
===============
Custom WTForms validators for the application.
"""
import re
from wtforms.validators import ValidationError


class StrongPassword:
    """Validate password strength."""
    def __init__(self, message=None):
        self.message = message or 'Password must be at least 8 characters with uppercase, lowercase, and a number.'

    def __call__(self, form, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError(self.message)
        if not re.search(r'[A-Z]', password):
            raise ValidationError(self.message)
        if not re.search(r'[a-z]', password):
            raise ValidationError(self.message)
        if not re.search(r'[0-9]', password):
            raise ValidationError(self.message)


class SafeUsername:
    """Validate username format."""
    def __init__(self, message=None):
        self.message = message or 'Username must be 3-30 characters, letters, numbers, and underscores only.'

    def __call__(self, form, field):
        username = field.data
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            raise ValidationError(self.message)
