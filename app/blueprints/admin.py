"""
Admin Blueprint
===============
Admin panel for system management and analytics.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from ..models import User, Resume, AnalysisResult, JobMatch
from ..utils.decorators import admin_required
from ..extensions import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@login_required
def require_admin():
    """Ensure only admins access admin routes."""
    if not current_user.is_admin:
        abort(403)


@admin_bp.route('/')
def index():
    """Admin dashboard."""
    total_users = User.query.count()
    total_resumes = Resume.query.count()
    analyzed_resumes = Resume.query.filter_by(status='completed').count()
    total_matches = JobMatch.query.count()

    # Top skills across all analyses
    top_skills = get_top_skills()

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    recent_resumes = Resume.query.order_by(Resume.created_at.desc()).limit(8).all()

    # Average scores
    avg_overall = db.session.query(func.avg(AnalysisResult.overall_score)).scalar() or 0
    avg_keyword = db.session.query(func.avg(AnalysisResult.keyword_score)).scalar() or 0

    return render_template(
        'admin/index.html',
        total_users=total_users,
        total_resumes=total_resumes,
        analyzed_resumes=analyzed_resumes,
        total_matches=total_matches,
        top_skills=top_skills,
        recent_users=recent_users,
        recent_resumes=recent_resumes,
        avg_overall=round(avg_overall, 1),
        avg_keyword=round(avg_keyword, 1)
    )


@admin_bp.route('/users')
def users():
    """Admin user management."""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    """Activate/deactivate a user."""
    if user_id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.username} {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    """Toggle admin status of a user."""
    if user_id == current_user.id:
        flash('You cannot change your own admin status.', 'warning')
        return redirect(url_for('admin.users'))
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Admin status for {user.username} {"granted" if user.is_admin else "revoked"}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/uploads')
def uploads():
    """Admin uploads view."""
    resumes = Resume.query.order_by(Resume.created_at.desc()).limit(50).all()
    return render_template('admin/uploads.html', resumes=resumes)


@admin_bp.route('/analytics')
def analytics():
    """Admin analytics."""
    return render_template('admin/analytics.html')


def get_top_skills():
    """Aggregate top skills across all analyses."""
    skill_counts = {}
    results = AnalysisResult.query.all()
    for r in results:
        for skill in r.skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    return [{'name': name, 'count': count} for name, count in top]
