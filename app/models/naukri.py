"""
Naukri Report Model
===================
Stores Naukri profile optimization analysis.
"""
import json
from datetime import datetime
from ..extensions import db


class NaukriReport(db.Model):
    """Naukri optimization report."""
    __tablename__ = 'naukri_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    resume_score = db.Column(db.Float, default=0)
    keyword_density = db.Column(db.Float, default=0)
    search_visibility = db.Column(db.Float, default=0)
    recruiter_ranking = db.Column(db.Float, default=0)
    profile_completeness = db.Column(db.Float, default=0)

    _missing_keywords = db.Column('missing_keywords', db.Text, default='[]')
    _improvement_suggestions = db.Column('improvement_suggestions', db.Text, default='[]')
    _top_skills = db.Column('top_skills', db.Text, default='[]')

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
    def missing_keywords(self):
        return self._get_json(self._missing_keywords)

    @missing_keywords.setter
    def missing_keywords(self, value):
        self._missing_keywords = self._set_json(value)

    @property
    def improvement_suggestions(self):
        return self._get_json(self._improvement_suggestions)

    @improvement_suggestions.setter
    def improvement_suggestions(self, value):
        self._improvement_suggestions = self._set_json(value)

    @property
    def top_skills(self):
        return self._get_json(self._top_skills)

    @top_skills.setter
    def top_skills(self, value):
        self._top_skills = self._set_json(value)

    def __repr__(self):
        return f'<NaukriReport user_id={self.user_id} score={self.resume_score}>'
