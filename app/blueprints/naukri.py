"""
Naukri Blueprint
================
Naukri profile optimization reports.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Resume, NaukriReport, ActivityLog
from ..ai.naukri_optimizer import analyze_naukri
from ..extensions import db

naukri_bp = Blueprint('naukri', __name__)


@naukri_bp.route('/')
@login_required
def index():
    """Naukri optimizer page."""
    recent_reports = NaukriReport.query.filter_by(user_id=current_user.id).order_by(
        NaukriReport.created_at.desc()
    ).limit(5).all()
    analyzed_resumes = Resume.query.filter_by(user_id=current_user.id, status='completed').order_by(
        Resume.created_at.desc()
    ).all()
    return render_template('naukri/index.html', reports=recent_reports, resumes=analyzed_resumes)


@naukri_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Analyze Naukri profile based on latest resume."""
    resume_id = request.form.get('resume_id')
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume or not resume.analysis:
        flash('Please select an analyzed resume first.', 'warning')
        return redirect(url_for('naukri.index'))

    analysis = resume.analysis
    extracted = {
        'name': analysis.candidate_name,
        'skills': analysis.skills,
        'experience': analysis.experience,
        'certifications': analysis.certifications,
        'linkedin': analysis.candidate_linkedin,
    }

    result = analyze_naukri(extracted, resume.raw_text)
    report = NaukriReport(
        user_id=current_user.id,
        resume_score=result['resume_score'],
        keyword_density=result['keyword_density'],
        search_visibility=result['search_visibility'],
        recruiter_ranking=result['recruiter_ranking'],
        profile_completeness=result['profile_completeness'],
        missing_keywords=result['missing_keywords'],
        improvement_suggestions=result['improvement_suggestions'],
        top_skills=result['top_skills'],
    )
    db.session.add(report)
    db.session.commit()

    ActivityLog.log(
        current_user.id, 'Naukri analyzed',
        description='Generated Naukri optimization report', icon='fa-briefcase', color='info'
    )
    flash('Naukri optimization report generated!', 'success')
    return redirect(url_for('naukri.report', report_id=report.id))


@naukri_bp.route('/report/<int:report_id>')
@login_required
def report(report_id):
    """View Naukri report."""
    report = NaukriReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    return render_template('naukri/report.html', report=report)
