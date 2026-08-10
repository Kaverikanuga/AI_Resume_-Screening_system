"""
Application Forms
=================
WTForms definitions for all forms across the SaaS platform.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, BooleanField,
    SelectField, SubmitField, IntegerField, FloatField, DateField,
    ValidationError
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, Regexp, NumberRange
)
from ..utils.validators import StrongPassword, SafeUsername
from ..models import User


# ============================================================
# Authentication Forms
# ============================================================

class RegisterForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(), SafeUsername()
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(message='Enter a valid email address.')
    ])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    password = PasswordField('Password', validators=[
        DataRequired(), StrongPassword()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    terms = BooleanField('I agree to the Terms of Service', validators=[
        DataRequired(message='You must accept the terms to continue.')
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken. Choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('An account with this email already exists.')


class LoginForm(FlaskForm):
    """User login form."""
    email = StringField('Email', validators=[
        DataRequired(), Email(message='Enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class ForgotPasswordForm(FlaskForm):
    """Forgot password request form."""
    email = StringField('Email', validators=[
        DataRequired(), Email(message='Enter a valid email address.')
    ])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """Password reset form."""
    password = PasswordField('New Password', validators=[
        DataRequired(), StrongPassword()
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')


class RequestVerificationForm(FlaskForm):
    """Request email verification link."""
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    submit = SubmitField('Send Verification Link')


# ============================================================
# Profile & Settings Forms
# ============================================================

class ProfileForm(FlaskForm):
    """User profile editing form."""
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    linkedin_url = StringField('LinkedIn URL', validators=[Optional(), Length(max=200)])
    github_url = StringField('GitHub URL', validators=[Optional(), Length(max=200)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Changes')


class AvatarForm(FlaskForm):
    """User avatar upload form."""
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only.')
    ])
    submit = SubmitField('Upload Avatar')


class SettingsForm(FlaskForm):
    """User settings form."""
    theme_preference = SelectField('Theme', choices=[
        ('dark', 'Dark'), ('light', 'Light')
    ])
    email_notifications = BooleanField('Email Notifications')
    submit = SubmitField('Save Settings')


class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), StrongPassword()
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')


# ============================================================
# Upload & Job Match Forms
# ============================================================

class UploadForm(FlaskForm):
    """Resume upload form."""
    resume = FileField('Resume (PDF)', validators=[
        DataRequired(), FileAllowed(['pdf'], 'PDF resumes only.')
    ])
    submit = SubmitField('Upload & Analyze')


class JobMatchForm(FlaskForm):
    """Job description matching form."""
    job_title = StringField('Job Title', validators=[Optional(), Length(max=200)])
    company_name = StringField('Company', validators=[Optional(), Length(max=200)])
    job_description = TextAreaField('Job Description', validators=[
        DataRequired(), Length(min=30, message='Job description must be at least 30 characters.')
    ])
    submit = SubmitField('Analyze Match')


class CareerQueryForm(FlaskForm):
    """Career assistant query form."""
    query = TextAreaField('Ask the AI Career Assistant', validators=[
        DataRequired(), Length(min=3, max=500)
    ])
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('roadmap', 'Career Roadmap'),
        ('skill', 'Next Skill'),
        ('cert', 'Next Certification'),
        ('project', 'Next Project'),
        ('internship', 'Next Internship'),
        ('interview', 'Interview Preparation'),
        ('placement', 'Placement Preparation'),
    ], default='general')
    submit = SubmitField('Ask Assistant')


# ============================================================
# Resume Builder & Editor Forms
# ============================================================

class ResumeBuilderForm(FlaskForm):
    """Resume builder form (personal + contact)."""
    template = SelectField('Template', choices=[
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('harvard', 'Harvard'),
        ('creative', 'Creative'),
        ('minimal', 'Minimal'),
    ], default='minimal')
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    job_title = StringField('Professional Title', validators=[Optional(), Length(max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    linkedin = StringField('LinkedIn URL', validators=[Optional(), Length(max=200)])
    github = StringField('GitHub URL', validators=[Optional(), Length(max=200)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    summary = TextAreaField('Professional Summary', validators=[Optional(), Length(max=1000)])
    skills = TextAreaField('Skills (comma separated)', validators=[Optional()])
    education = TextAreaField('Education (one per line)', validators=[Optional()])
    experience = TextAreaField('Experience (one entry per line)', validators=[Optional()])
    projects = TextAreaField('Projects (one per line)', validators=[Optional()])
    certifications = TextAreaField('Certifications (one per line)', validators=[Optional()])
    languages = TextAreaField('Languages (comma separated)', validators=[Optional()])
    submit = SubmitField('Generate Resume')


class ResumeEditorContentForm(FlaskForm):
    """Live resume editor content."""
    html_content = TextAreaField('Resume HTML', validators=[Optional()])
    submit = SubmitField('Save Resume')

