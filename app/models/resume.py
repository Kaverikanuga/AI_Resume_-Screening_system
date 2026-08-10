"""
Resume & Analysis Models
========================
Stores uploaded resumes and their AI analysis results.
"""
import json
from datetime import datetime
from ..extensions import db


class Resume(db.Model):
    """Uploaded resume model."""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.Float, default=0)
    page_count = db.Column(db.Integer, default=1)
    raw_text = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='uploaded')  # uploaded, analyzing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis = db.relationship('AnalysisResult', backref='resume', uselist=False, cascade='all, delete-orphan')
    job_matches = db.relationship('JobMatch', backref='resume', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_analyzed(self):
        return self.status == 'completed' and self.analysis is not None

    def __repr__(self):
        return f'<Resume {self.original_name}>'


class AnalysisResult(db.Model):
    """AI analysis result for a resume."""
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, unique=True, index=True)

    # Extracted Contact Info
    candidate_name = db.Column(db.String(200), default='')
    candidate_email = db.Column(db.String(200), default='')
    candidate_phone = db.Column(db.String(50), default='')
    candidate_address = db.Column(db.String(300), default='')
    candidate_linkedin = db.Column(db.String(300), default='')
    candidate_github = db.Column(db.String(300), default='')

    # Extracted Sections (stored as JSON strings)
    _skills = db.Column('skills', db.Text, default='[]')
    _technical_skills = db.Column('technical_skills', db.Text, default='[]')
    _soft_skills = db.Column('soft_skills', db.Text, default='[]')
    _education = db.Column('education', db.Text, default='[]')
    _experience = db.Column('experience', db.Text, default='[]')
    _projects = db.Column('projects', db.Text, default='[]')
    _certifications = db.Column('certifications', db.Text, default='[]')
    _achievements = db.Column('achievements', db.Text, default='[]')
    _languages = db.Column('languages', db.Text, default='[]')
    _internships = db.Column('internships', db.Text, default='[]')

    # ATS Scores (0-100)
    overall_score = db.Column(db.Float, default=0)
    keyword_score = db.Column(db.Float, default=0)
    grammar_score = db.Column(db.Float, default=0)
    formatting_score = db.Column(db.Float, default=0)
    readability_score = db.Column(db.Float, default=0)
    professional_score = db.Column(db.Float, default=0)
    strength_score = db.Column(db.Float, default=0)
    weakness_score = db.Column(db.Float, default=0)

    # Section Scores
    contact_score = db.Column(db.Float, default=0)
    summary_score = db.Column(db.Float, default=0)
    education_score = db.Column(db.Float, default=0)
    experience_score = db.Column(db.Float, default=0)
    skills_score = db.Column(db.Float, default=0)
    projects_score = db.Column(db.Float, default=0)
    certifications_score = db.Column(db.Float, default=0)

    # AI Generated Content (stored as JSON strings)
    _strengths = db.Column('strengths', db.Text, default='[]')
    _weaknesses = db.Column('weaknesses', db.Text, default='[]')
    _suggestions = db.Column('suggestions', db.Text, default='[]')
    _missing_keywords = db.Column('missing_keywords', db.Text, default='[]')
    _formatting_issues = db.Column('formatting_issues', db.Text, default='[]')
    _action_verbs = db.Column('action_verbs', db.Text, default='[]')
    _missing_sections = db.Column('missing_sections', db.Text, default='[]')

    # Resume Health
    health_status = db.Column(db.String(20), default='average')  # excellent, good, average, poor
    word_count = db.Column(db.Integer, default=0)
    sentence_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # JSON property helpers
    @staticmethod
    def _get_json(value):
        try:
            return json.loads(value) if value else []
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def _set_json(value):
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value or '[]'

    # Skills
    @property
    def skills(self):
        return self._get_json(self._skills)

    @skills.setter
    def skills(self, value):
        self._skills = self._set_json(value)

    # Technical Skills
    @property
    def technical_skills(self):
        return self._get_json(self._technical_skills)

    @technical_skills.setter
    def technical_skills(self, value):
        self._technical_skills = self._set_json(value)

    # Soft Skills
    @property
    def soft_skills(self):
        return self._get_json(self._soft_skills)

    @soft_skills.setter
    def soft_skills(self, value):
        self._soft_skills = self._set_json(value)

    # Education
    @property
    def education(self):
        return self._get_json(self._education)

    @education.setter
    def education(self, value):
        self._education = self._set_json(value)

    # Experience
    @property
    def experience(self):
        return self._get_json(self._experience)

    @experience.setter
    def experience(self, value):
        self._experience = self._set_json(value)

    # Projects
    @property
    def projects(self):
        return self._get_json(self._projects)

    @projects.setter
    def projects(self, value):
        self._projects = self._set_json(value)

    # Certifications
    @property
    def certifications(self):
        return self._get_json(self._certifications)

    @certifications.setter
    def certifications(self, value):
        self._certifications = self._set_json(value)

    # Achievements
    @property
    def achievements(self):
        return self._get_json(self._achievements)

    @achievements.setter
    def achievements(self, value):
        self._achievements = self._set_json(value)

    # Languages
    @property
    def languages(self):
        return self._get_json(self._languages)

    @languages.setter
    def languages(self, value):
        self._languages = self._set_json(value)

    # Internships
    @property
    def internships(self):
        return self._get_json(self._internships)

    @internships.setter
    def internships(self, value):
        self._internships = self._set_json(value)

    # Strengths
    @property
    def strengths(self):
        return self._get_json(self._strengths)

    @strengths.setter
    def strengths(self, value):
        self._strengths = self._set_json(value)

    # Weaknesses
    @property
    def weaknesses(self):
        return self._get_json(self._weaknesses)

    @weaknesses.setter
    def weaknesses(self, value):
        self._weaknesses = self._set_json(value)

    # Suggestions
    @property
    def suggestions(self):
        return self._get_json(self._suggestions)

    @suggestions.setter
    def suggestions(self, value):
        self._suggestions = self._set_json(value)

    # Missing Keywords
    @property
    def missing_keywords(self):
        return self._get_json(self._missing_keywords)

    @missing_keywords.setter
    def missing_keywords(self, value):
        self._missing_keywords = self._set_json(value)

    # Formatting Issues
    @property
    def formatting_issues(self):
        return self._get_json(self._formatting_issues)

    @formatting_issues.setter
    def formatting_issues(self, value):
        self._formatting_issues = self._set_json(value)

    # Action Verbs
    @property
    def action_verbs(self):
        return self._get_json(self._action_verbs)

    @action_verbs.setter
    def action_verbs(self, value):
        self._action_verbs = self._set_json(value)

    # Missing Sections
    @property
    def missing_sections(self):
        return self._get_json(self._missing_sections)

    @missing_sections.setter
    def missing_sections(self, value):
        self._missing_sections = self._set_json(value)

    def __repr__(self):
        return f'<AnalysisResult resume_id={self.resume_id} score={self.overall_score}>'
