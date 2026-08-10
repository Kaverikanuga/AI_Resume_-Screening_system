"""
Auth Blueprint
==============
Registration, login, password reset, profile, and settings.
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, session, current_app, send_from_directory
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from ..extensions import db
from ..models import User, ActivityLog, Notification
from ..forms.main import (
    RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm,
    ProfileForm, AvatarForm, SettingsForm, ChangePasswordForm
)
from ..utils.helpers import save_avatar

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            first_name=form.first_name.data or '',
            last_name=form.last_name.data or ''
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        ActivityLog.log(
            user.id, 'Registered',
            description='New account created', icon='fa-user-plus', color='success'
        )
        Notification.create(
            user.id, 'Welcome to ResumeAI Pro!',
            'Your account has been created successfully. Upload your first resume to get an AI analysis.',
            type='success', icon='fa-rocket'
        )
        login_user(user, remember=True)
        flash('Account created successfully. Welcome to ResumeAI Pro!', 'success')
        # If the user was choosing a paid plan before signing up, resume checkout.
        if session.get('pending_plan'):
            return redirect(url_for('main.pricing'))
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user, remember=form.remember.data)
            user.last_login = db.func.now()
            db.session.commit()
            ActivityLog.log(
                user.id, 'Logged in',
                description='User signed in successfully', icon='fa-sign-in-alt', color='primary'
            )
            next_page = request.args.get('next')
            flash('Welcome back, ' + user.full_name + '!', 'success')
            # If the user was choosing a paid plan before login, resume checkout.
            if session.get('pending_plan'):
                return redirect(url_for('main.pricing'))
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    ActivityLog.log(
        current_user.id, 'Logged out',
        description='User signed out', icon='fa-sign-out-alt', color='secondary'
    )
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password request."""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # In production, send email with reset token
            flash('If an account exists with that email, a reset link has been sent.', 'info')
        else:
            flash('If an account exists with that email, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # In production, verify token and reset password
        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit profile."""
    form = ProfileForm(obj=current_user)
    avatar_form = AvatarForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.github_url = form.github_url.data
        current_user.bio = form.bio.data
        db.session.commit()
        ActivityLog.log(
            current_user.id, 'Profile updated',
            description='User updated their profile', icon='fa-user-edit', color='primary'
        )
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html', form=form, avatar_form=avatar_form)


@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings."""
    settings_form = SettingsForm(obj=current_user)
    password_form = ChangePasswordForm()
    if settings_form.validate_on_submit():
        current_user.theme_preference = settings_form.theme_preference.data
        current_user.email_notifications = settings_form.email_notifications.data
        db.session.commit()
        flash('Settings saved.', 'success')
        return redirect(url_for('auth.settings'))
    return render_template('auth/settings.html', settings_form=settings_form, password_form=password_form)


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully.', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    return redirect(url_for('auth.settings'))


@auth_bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar."""
    form = AvatarForm()
    if form.validate_on_submit():
        filename = save_avatar(form.avatar.data, current_user.id)
        if filename:
            current_user.avatar = filename
            db.session.commit()
            flash('Avatar updated.', 'success')
        else:
            flash('Invalid image file.', 'danger')
    return redirect(url_for('auth.profile'))
