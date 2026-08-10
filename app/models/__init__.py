"""
Database Models Package
=======================
Import all models for SQLAlchemy discovery.
"""
from .user import User
from .resume import Resume, AnalysisResult
from .job import JobMatch
from .linkedin import LinkedInReport
from .naukri import NaukriReport
from .career import CareerSuggestion
from .activity import Notification, ActivityLog
from .history import ResumeHistory
from .payment import Payment

__all__ = [
    'User', 'Resume', 'AnalysisResult', 'JobMatch',
    'LinkedInReport', 'NaukriReport', 'CareerSuggestion',
    'Notification', 'ActivityLog', 'ResumeHistory', 'Payment'
]
