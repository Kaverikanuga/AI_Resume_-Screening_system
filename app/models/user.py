"""
User Model
==========
Handles user accounts, authentication, and profile data.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db, login_manager


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), default='')
    last_name = db.Column(db.String(50), default='')
    avatar = db.Column(db.String(256), default='default.png')
    bio = db.Column(db.Text, default='')
    phone = db.Column(db.String(20), default='')
    location = db.Column(db.String(100), default='')
    website = db.Column(db.String(200), default='')
    linkedin_url = db.Column(db.String(200), default='')
    github_url = db.Column(db.String(200), default='')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    plan = db.Column(db.String(20), default='free', index=True)  # free, pro, business
    plan_expires_at = db.Column(db.DateTime, nullable=True)
    theme_preference = db.Column(db.String(10), default='dark')
    email_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resumes = db.relationship('Resume', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    job_matches = db.relationship('JobMatch', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    linkedin_reports = db.relationship('LinkedInReport', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    naukri_reports = db.relationship('NaukriReport', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    career_suggestions = db.relationship('CareerSuggestion', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    resume_history = db.relationship('ResumeHistory', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return full name or username."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        return self.username

    @property
    def initials(self):
        """Return user initials for avatar fallback."""
        if self.first_name and self.last_name:
            return f'{self.first_name[0]}{self.last_name[0]}'.upper()
        return self.username[:2].upper()

    @property
    def resume_count(self):
        """Return total number of resumes uploaded."""
        return self.resumes.count()

    @property
    def avg_ats_score(self):
        """Return average ATS score across all analyzed resumes."""
        from .resume import AnalysisResult
        results = AnalysisResult.query.join(
            Resume, Resume.id == AnalysisResult.resume_id
        ).filter(Resume.user_id == self.id).all()
        if not results:
            return 0
        return round(sum(r.overall_score for r in results) / len(results), 1)

    def __repr__(self):
        return f'<User {self.username}>'


# Import Resume here to avoid circular imports in the property
from .resume import Resume  # noqa: E402


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))

