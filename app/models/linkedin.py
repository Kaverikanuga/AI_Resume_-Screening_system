"""
LinkedIn Report Model
=====================
Stores LinkedIn profile optimization analysis.
"""
import json
from datetime import datetime
from ..extensions import db


class LinkedInReport(db.Model):
    """LinkedIn optimization report."""
    __tablename__ = 'linkedin_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    linkedin_score = db.Column(db.Float, default=0)
    visibility_score = db.Column(db.Float, default=0)
    recruiter_visibility = db.Column(db.Float, default=0)
    ssi_score = db.Column(db.Float, default=0)
    profile_completeness = db.Column(db.Float, default=0)

    headline_suggestion = db.Column(db.Text, default='')
    about_suggestion = db.Column(db.Text, default='')

    _skills_suggestions = db.Column('skills_suggestions', db.Text, default='[]')
    _networking_tips = db.Column('networking_tips', db.Text, default='[]')
    _improvement_tips = db.Column('improvement_tips', db.Text, default='[]')

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
    def skills_suggestions(self):
        return self._get_json(self._skills_suggestions)

    @skills_suggestions.setter
    def skills_suggestions(self, value):
        self._skills_suggestions = self._set_json(value)

    @property
    def networking_tips(self):
        return self._get_json(self._networking_tips)

    @networking_tips.setter
    def networking_tips(self, value):
        self._networking_tips = self._set_json(value)

    @property
    def improvement_tips(self):
        return self._get_json(self._improvement_tips)

    @improvement_tips.setter
    def improvement_tips(self, value):
        self._improvement_tips = self._set_json(value)

    def __repr__(self):
        return f'<LinkedInReport user_id={self.user_id} score={self.linkedin_score}>'
