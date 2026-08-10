"""
Career Suggestion Model
=======================
Stores AI career assistant conversations and recommendations.
"""
import json
from datetime import datetime
from ..extensions import db


class CareerSuggestion(db.Model):
    """Career assistant conversation and recommendations."""
    __tablename__ = 'career_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')  # roadmap, skill, cert, project, interview, placement

    _recommended_skills = db.Column('recommended_skills', db.Text, default='[]')
    _recommended_certs = db.Column('recommended_certs', db.Text, default='[]')
    _recommended_projects = db.Column('recommended_projects', db.Text, default='[]')
    _learning_resources = db.Column('learning_resources', db.Text, default='[]')
    _interview_tips = db.Column('interview_tips', db.Text, default='[]')

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
    def recommended_skills(self):
        return self._get_json(self._recommended_skills)

    @recommended_skills.setter
    def recommended_skills(self, value):
        self._recommended_skills = self._set_json(value)

    @property
    def recommended_certs(self):
        return self._get_json(self._recommended_certs)

    @recommended_certs.setter
    def recommended_certs(self, value):
        self._recommended_certs = self._set_json(value)

    @property
    def recommended_projects(self):
        return self._get_json(self._recommended_projects)

    @recommended_projects.setter
    def recommended_projects(self, value):
        self._recommended_projects = self._set_json(value)

    @property
    def learning_resources(self):
        return self._get_json(self._learning_resources)

    @learning_resources.setter
    def learning_resources(self, value):
        self._learning_resources = self._set_json(value)

    @property
    def interview_tips(self):
        return self._get_json(self._interview_tips)

    @interview_tips.setter
    def interview_tips(self, value):
        self._interview_tips = self._set_json(value)

    def __repr__(self):
        return f'<CareerSuggestion user_id={self.user_id} category={self.category}>'
