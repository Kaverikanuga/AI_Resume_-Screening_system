"""
AI Resume Screening System - App Factory
==========================================
Creates and configures the Flask application instance.
"""
import os
from flask import Flask, render_template
from .config import config
from .extensions import db, login_manager, csrf, migrate


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Ensure instance folder exists
    os.makedirs(os.path.join(os.path.dirname(app.root_path), 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Import models so SQLAlchemy knows about them
    from . import models  # noqa: F401

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register context processors
    _register_context_processors(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


def _register_blueprints(app):
    """Register all Flask blueprints."""
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.upload import upload_bp
    from .blueprints.analysis import analysis_bp
    from .blueprints.linkedin import linkedin_bp
    from .blueprints.naukri import naukri_bp
    from .blueprints.career import career_bp
    from .blueprints.builder import builder_bp
    from .blueprints.editor import editor_bp
    from .blueprints.reports import reports_bp
    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp
    from .blueprints.portfolio import portfolio_bp
    from .blueprints.payment import payment_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(linkedin_bp, url_prefix='/linkedin')
    app.register_blueprint(naukri_bp, url_prefix='/naukri')
    app.register_blueprint(career_bp, url_prefix='/career')
    app.register_blueprint(builder_bp, url_prefix='/builder')
    app.register_blueprint(editor_bp, url_prefix='/editor')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')


def _register_error_handlers(app):
    """Register custom error handlers."""

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def too_large(error):
        return render_template('errors/404.html', message='File too large. Maximum size is 16MB.'), 413


def _register_context_processors(app):
    """Register Jinja2 context processors."""

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from .models.activity import Notification
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {
            'app_name': 'ResumeAI Pro',
            'app_version': '2.0.0',
            'unread_notifications': unread_count,
            'current_year': 2026
        }
