"""
LinkedIn Blueprint
==================
LinkedIn profile optimization reports.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Resume, LinkedInReport, ActivityLog
from ..ai.linkedin_optimizer import analyze_linkedin
from ..extensions import db

linkedin_bp = Blueprint('linkedin', __name__)


@linkedin_bp.route('/')
@login_required
def index():
    """LinkedIn optimizer page."""
    recent_reports = LinkedInReport.query.filter_by(user_id=current_user.id).order_by(
        LinkedInReport.created_at.desc()
    ).limit(5).all()
    analyzed_resumes = Resume.query.filter_by(user_id=current_user.id, status='completed').order_by(
        Resume.created_at.desc()
    ).all()
    return render_template('linkedin/index.html', reports=recent_reports, resumes=analyzed_resumes)


@linkedin_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Analyze LinkedIn profile based on latest resume."""
    resume_id = request.form.get('resume_id')
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
    if not resume or not resume.analysis:
        flash('Please select an analyzed resume first.', 'warning')
        return redirect(url_for('linkedin.index'))

    analysis = resume.analysis
    extracted = {
        'name': analysis.candidate_name,
        'linkedin': analysis.candidate_linkedin,
        'skills': analysis.skills,
        'technical_skills': analysis.technical_skills,
        'experience': analysis.experience,
        'projects': analysis.projects,
        'certifications': analysis.certifications,
        'education': analysis.education,
        'summary': '',
    }

    result = analyze_linkedin(extracted)
    report = LinkedInReport(
        user_id=current_user.id,
        linkedin_score=result['linkedin_score'],
        visibility_score=result['visibility_score'],
        recruiter_visibility=result['recruiter_visibility'],
        ssi_score=result['ssi_score'],
        profile_completeness=result['profile_completeness'],
        headline_suggestion=result['headline_suggestion'],
        about_suggestion=result['about_suggestion'],
        skills_suggestions=result['skills_suggestions'],
        networking_tips=result['networking_tips'],
        improvement_tips=result['improvement_tips'],
    )
    db.session.add(report)
    db.session.commit()

    ActivityLog.log(
        current_user.id, 'LinkedIn analyzed',
        description='Generated LinkedIn optimization report', icon='fa-linkedin', color='primary'
    )
    flash('LinkedIn optimization report generated!', 'success')
    return redirect(url_for('linkedin.report', report_id=report.id))


@linkedin_bp.route('/report/<int:report_id>')
@login_required
def report(report_id):
    """View LinkedIn report."""
    report = LinkedInReport.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    return render_template('linkedin/report.html', report=report)
