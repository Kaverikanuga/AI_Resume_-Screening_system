"""
Analysis Blueprint
==================
View and download resume analysis reports.
"""
import os
import io
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    send_file, current_app, abort, request
)
from flask_login import login_required, current_user
from ..models import Resume, AnalysisResult, JobMatch
from ..ai.job_matcher import analyze_job_match
from ..ai.extractor import extract_all

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/<int:resume_id>')
@login_required
def view(resume_id):
    """View analysis report for a resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        flash('This resume has not been analyzed yet.', 'warning')
        return redirect(url_for('dashboard.history'))
    analysis = resume.analysis
    return render_template(
        'analysis/view.html',
        resume=resume,
        analysis=analysis,
        sections=[
            {'name': 'Contact', 'score': analysis.contact_score},
            {'name': 'Summary', 'score': analysis.summary_score},
            {'name': 'Education', 'score': analysis.education_score},
            {'name': 'Experience', 'score': analysis.experience_score},
            {'name': 'Skills', 'score': analysis.skills_score},
            {'name': 'Projects', 'score': analysis.projects_score},
            {'name': 'Certifications', 'score': analysis.certifications_score},
        ]
    )


@analysis_bp.route('/<int:resume_id>/job-match', methods=['GET', 'POST'])
@login_required
def job_match(resume_id):
    """Match a resume against a job description."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        flash('Please analyze the resume first.', 'warning')
        return redirect(url_for('analysis.view', resume_id=resume_id))

    from ..forms.main import JobMatchForm
    form = JobMatchForm()

    if form.validate_on_submit():
        analysis = resume.analysis
        extracted = {
            'skills': analysis.skills,
            'technical_skills': analysis.technical_skills,
            'experience': analysis.experience,
            'projects': analysis.projects,
            'certifications': analysis.certifications,
            'linkedin': analysis.candidate_linkedin,
            'summary': '',
        }
        result = analyze_job_match(
            extracted,
            form.job_description.data,
            form.job_title.data,
            form.company_name.data
        )
        match = JobMatch(
            user_id=current_user.id,
            resume_id=resume.id,
            job_title=form.job_title.data,
            company_name=form.company_name.data,
            job_description=form.job_description.data,
            match_percentage=result['match_percentage'],
            ats_compatibility=result['ats_compatibility'],
            job_readiness_score=result['job_readiness_score'],
            matching_skills=result['matching_skills'],
            missing_skills=result['missing_skills'],
            keyword_matches=result['keyword_matches'],
            skill_gaps=result['skill_gaps'],
            learning_suggestions=result['learning_suggestions'],
            interview_questions=result['interview_questions'],
            recruiter_suggestions=result['recruiter_suggestions'],
            salary_estimate=result['salary_estimate'],
        )
        from ..extensions import db
        db.session.add(match)
        db.session.commit()
        flash('Job match analysis complete!', 'success')
        return redirect(url_for('analysis.match_result', match_id=match.id))

    return render_template('analysis/job_match.html', form=form, resume=resume)


@analysis_bp.route('/match/<int:match_id>')
@login_required
def match_result(match_id):
    """View job match result."""
    match = JobMatch.query.filter_by(id=match_id, user_id=current_user.id).first_or_404()
    return render_template('analysis/match_result.html', match=match)


@analysis_bp.route('/<int:resume_id>/reanalyze', methods=['POST'])
@login_required
def reanalyze(resume_id):
    """Re-run analysis on a resume."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    from ..services.analysis_service import analyze_resume
    try:
        analyze_resume(resume.id)
        flash('Resume re-analyzed successfully.', 'success')
    except Exception:
        flash('Re-analysis failed. Please try again.', 'danger')
    return redirect(url_for('analysis.view', resume_id=resume.id))
