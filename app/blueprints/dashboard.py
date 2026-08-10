"""
Dashboard Blueprint
===================
User dashboard with analytics, charts, and activity feed.
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from ..models import Resume, AnalysisResult, JobMatch, Notification, ActivityLog
from ..models.linkedin import LinkedInReport
from ..models.naukri import NaukriReport

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard."""
    user = current_user

    # Resume stats
    total_resumes = Resume.query.filter_by(user_id=user.id).count()
    analyzed = Resume.query.filter_by(user_id=user.id, status='completed').count()

    # Latest analysis
    latest = AnalysisResult.query.join(
        Resume, Resume.id == AnalysisResult.resume_id
    ).filter(Resume.user_id == user.id).order_by(AnalysisResult.created_at.desc()).first()

    # Recent resumes
    recent_resumes = Resume.query.filter_by(user_id=user.id).order_by(
        Resume.created_at.desc()
    ).limit(5).all()

    # Recent job matches
    recent_jobs = JobMatch.query.filter_by(user_id=user.id).order_by(
        JobMatch.created_at.desc()
    ).limit(5).all()

    # Activity feed
    activities = ActivityLog.query.filter_by(user_id=user.id).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()

    # Notifications
    notifications = Notification.query.filter_by(user_id=user.id).order_by(
        Notification.created_at.desc()
    ).limit(10).all()

    # Skill distribution from latest analysis
    skill_distribution = []
    if latest:
        tech = latest.technical_skills
        soft = latest.soft_skills
        skill_distribution = [
            {'label': 'Technical', 'value': len(tech)},
            {'label': 'Soft', 'value': len(soft)},
        ]

    # Score comparison for radar chart
    radar_scores = []
    if latest:
        radar_scores = [
            {'label': 'Keyword', 'value': latest.keyword_score},
            {'label': 'Formatting', 'value': latest.formatting_score},
            {'label': 'Readability', 'value': latest.readability_score},
            {'label': 'Grammar', 'value': latest.grammar_score},
            {'label': 'Professional', 'value': latest.professional_score},
        ]

    # Timeline data
    timeline_data = []
    if latest:
        timeline_data = [
            {'label': 'Uploaded', 'value': 100, 'active': True},
            {'label': 'Parsed', 'value': 100, 'active': True},
            {'label': 'Analyzed', 'value': 100, 'active': True},
            {'label': 'Optimized', 'value': 100, 'active': True},
        ]

    # Stats cards
    avg_score = user.avg_ats_score
    job_matches = JobMatch.query.filter_by(user_id=user.id).count()
    linkedin_reports = LinkedInReport.query.filter_by(user_id=user.id).count()

    return render_template(
        'dashboard/index.html',
        total_resumes=total_resumes,
        analyzed=analyzed,
        avg_score=avg_score,
        latest=latest,
        recent_resumes=recent_resumes,
        recent_jobs=recent_jobs,
        activities=activities,
        notifications=notifications,
        skill_distribution=skill_distribution,
        radar_scores=radar_scores,
        timeline_data=timeline_data,
        job_matches=job_matches,
        linkedin_reports=linkedin_reports
    )


@dashboard_bp.route('/mark-notifications-read')
@login_required
def mark_notifications_read():
    """Mark all notifications as read."""
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {'is_read': True}
    )
    from ..extensions import db
    db.session.commit()
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/history')
@login_required
def history():
    """Resume analysis history."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(
        Resume.created_at.desc()
    ).all()
    return render_template('dashboard/history.html', resumes=resumes)
