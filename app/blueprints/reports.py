"""
Reports Blueprint
=================
Generate and download professional PDF reports.
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    send_file, current_app, request
)
from flask_login import login_required, current_user
from ..models import Resume, AnalysisResult, JobMatch
from ..services.report_service import generate_analysis_report_pdf
from ..extensions import db

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
def index():
    """Reports overview."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(
        Resume.created_at.desc()
    ).all()
    return render_template('reports/index.html', resumes=resumes)


@reports_bp.route('/analysis/<int:resume_id>')
@login_required
def analysis_report(resume_id):
    """View analysis report page."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        flash('No analysis available for this resume.', 'warning')
        return redirect(url_for('reports.index'))
    return render_template('reports/analysis.html', resume=resume, analysis=resume.analysis)


@reports_bp.route('/analysis/<int:resume_id>/download')
@login_required
def download_analysis(resume_id):
    """Download analysis report as PDF."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        flash('No analysis available.', 'warning')
        return redirect(url_for('reports.index'))
    try:
        pdf = generate_analysis_report_pdf(resume, resume.analysis, current_user)
        filename = f"ats_report_{resume.original_name.rsplit('.', 1)[0]}.pdf"
        return send_file(pdf, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        current_app.logger.error(f'Report generation error: {e}')
        flash('Failed to generate report PDF.', 'danger')
        return redirect(url_for('reports.analysis_report', resume_id=resume.id))
