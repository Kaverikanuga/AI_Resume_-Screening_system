"""
Job Match Model
===============
Stores job description matching results.
"""
import json
from datetime import datetime
from ..extensions import db


class JobMatch(db.Model):
    """Job description match analysis."""
    __tablename__ = 'job_matches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    job_title = db.Column(db.String(200), default='')
    company_name = db.Column(db.String(200), default='')
    job_description = db.Column(db.Text, nullable=False)
    match_percentage = db.Column(db.Float, default=0)
    ats_compatibility = db.Column(db.Float, default=0)
    job_readiness_score = db.Column(db.Float, default=0)

    _matching_skills = db.Column('matching_skills', db.Text, default='[]')
    _missing_skills = db.Column('missing_skills', db.Text, default='[]')
    _keyword_matches = db.Column('keyword_matches', db.Text, default='[]')
    _skill_gaps = db.Column('skill_gaps', db.Text, default='[]')
    _learning_suggestions = db.Column('learning_suggestions', db.Text, default='[]')
    _interview_questions = db.Column('interview_questions', db.Text, default='[]')
    _recruiter_suggestions = db.Column('recruiter_suggestions', db.Text, default='[]')

    salary_estimate = db.Column(db.String(100), default='')
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
    def matching_skills(self):
        return self._get_json(self._matching_skills)

    @matching_skills.setter
    def matching_skills(self, value):
        self._matching_skills = self._set_json(value)

    @property
    def missing_skills(self):
        return self._get_json(self._missing_skills)

    @missing_skills.setter
    def missing_skills(self, value):
        self._missing_skills = self._set_json(value)

    @property
    def keyword_matches(self):
        return self._get_json(self._keyword_matches)

    @keyword_matches.setter
    def keyword_matches(self, value):
        self._keyword_matches = self._set_json(value)

    @property
    def skill_gaps(self):
        return self._get_json(self._skill_gaps)

    @skill_gaps.setter
    def skill_gaps(self, value):
        self._skill_gaps = self._set_json(value)

    @property
    def learning_suggestions(self):
        return self._get_json(self._learning_suggestions)

    @learning_suggestions.setter
    def learning_suggestions(self, value):
        self._learning_suggestions = self._set_json(value)

    @property
    def interview_questions(self):
        return self._get_json(self._interview_questions)

    @interview_questions.setter
    def interview_questions(self, value):
        self._interview_questions = self._set_json(value)

    @property
    def recruiter_suggestions(self):
        return self._get_json(self._recruiter_suggestions)

    @recruiter_suggestions.setter
    def recruiter_suggestions(self, value):
        self._recruiter_suggestions = self._set_json(value)

    def __repr__(self):
        return f'<JobMatch {self.job_title} match={self.match_percentage}%>'
