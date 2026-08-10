"""
Main Blueprint
==============
Landing page, pricing, features, and public pages.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from ..models import User, Resume, AnalysisResult

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('main/index.html')


@main_bp.route('/features')
def features():
    """Features page."""
    return render_template('main/features.html')


@main_bp.route('/pricing')
def pricing():
    """Pricing page."""
    return render_template('main/pricing.html')


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')


@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('main/contact.html')
