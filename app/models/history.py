"""
Resume History Model
====================
Tracks resume versions and analysis history over time.
"""
import json
from datetime import datetime
from ..extensions import db


class ResumeHistory(db.Model):
    """Tracks a snapshot of resume analysis at a point in time."""
    __tablename__ = 'resume_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True, index=True)
    filename = db.Column(db.String(256), default='')
    version = db.Column(db.Integer, default=1)
    overall_score = db.Column(db.Float, default=0)
    keyword_score = db.Column(db.Float, default=0)
    grammar_score = db.Column(db.Float, default=0)
    formatting_score = db.Column(db.Float, default=0)
    readability_score = db.Column(db.Float, default=0)
    professional_score = db.Column(db.Float, default=0)
    health_status = db.Column(db.String(20), default='average')
    word_count = db.Column(db.Integer, default=0)

    _skills = db.Column('skills', db.Text, default='[]')
    _missing_keywords = db.Column('missing_keywords', db.Text, default='[]')
    _suggestions = db.Column('suggestions', db.Text, default='[]')
    _strengths = db.Column('strengths', db.Text, default='[]')
    _weaknesses = db.Column('weaknesses', db.Text, default='[]')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    @property
    def skills(self):
        return self._get_json(self._skills)

    @skills.setter
    def skills(self, value):
        self._skills = self._set_json(value)

    @property
    def missing_keywords(self):
        return self._get_json(self._missing_keywords)

    @missing_keywords.setter
    def missing_keywords(self, value):
        self._missing_keywords = self._set_json(value)

    @property
    def suggestions(self):
        return self._get_json(self._suggestions)

    @suggestions.setter
    def suggestions(self, value):
        self._suggestions = self._set_json(value)

    @property
    def strengths(self):
        return self._get_json(self._strengths)

    @strengths.setter
    def strengths(self, value):
        self._strengths = self._set_json(value)

    @property
    def weaknesses(self):
        return self._get_json(self._weaknesses)

    @weaknesses.setter
    def weaknesses(self, value):
        self._weaknesses = self._set_json(value)

    @staticmethod
    def record(user_id, resume, analysis):
        """Create a history snapshot from a resume and its analysis."""
        latest = ResumeHistory.query.filter_by(user_id=user_id, resume_id=resume.id).order_by(
            ResumeHistory.version.desc()
        ).first()
        version = (latest.version + 1) if latest else 1
        entry = ResumeHistory(
            user_id=user_id,
            resume_id=resume.id,
            filename=resume.original_name,
            version=version,
            overall_score=analysis.overall_score,
            keyword_score=analysis.keyword_score,
            grammar_score=analysis.grammar_score,
            formatting_score=analysis.formatting_score,
            readability_score=analysis.readability_score,
            professional_score=analysis.professional_score,
            health_status=analysis.health_status,
            word_count=analysis.word_count,
            skills=analysis.skills,
            missing_keywords=analysis.missing_keywords,
            suggestions=analysis.suggestions,
            strengths=analysis.strengths,
            weaknesses=analysis.weaknesses,
        )
        db.session.add(entry)
        return entry

    def __repr__(self):
        return f'<ResumeHistory id={self.id} version={self.version} score={self.overall_score}>'
