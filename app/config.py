"""
Application Configuration
=========================
Development and Production configuration classes.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present).
# override=True forces .env (the verified source of truth) to take precedence
# over any stale OS/shell environment variables that may override the keys.
load_dotenv(override=True)

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, '..'))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-resume-screening-super-secret-key-2024-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(project_root, 'uploads')
    REPORTS_FOLDER = os.path.join(project_root, 'reports')
    ALLOWED_EXTENSIONS = {'pdf'}
    ITEMS_PER_PAGE = 10

    # Razorpay (TEST MODE) - credentials read from environment variables only
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
    # Plan amount mapping in paise (currency smallest unit)
    RAZORPAY_PLAN_AMOUNTS = {
        'pro': 5900,      # ₹59 = 5900 paise
        'business': 9900, # ₹99 = 9900 paise
    }

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
        avatars_dir = os.path.join(app.static_folder, 'img', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(project_root, 'instance', 'app.db')
    )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(project_root, 'instance', 'app.db')
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
