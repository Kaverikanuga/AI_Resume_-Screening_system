"""
API Blueprint
=============
REST API endpoints for programmatic access.
"""
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from ..models import Resume, AnalysisResult, JobMatch, User
from ..services.analysis_service import analyze_resume
from ..ai.job_matcher import analyze_job_match
from ..extensions import db

api_bp = Blueprint('api', __name__)


@api_bp.route('/theme', methods=['POST'])
@login_required
def theme():
    """Update user theme preference."""
    data = request.get_json() or {}
    theme = data.get('theme', 'dark')
    if theme not in ('dark', 'light'):
        return jsonify({'error': 'Invalid theme'}), 400
    current_user.theme_preference = theme
    db.session.commit()
    return jsonify({'status': 'ok', 'theme': theme})


@api_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'ResumeAI Pro'})


@api_bp.route('/resumes')
@login_required
def resumes():
    """List user's resumes."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(
        Resume.created_at.desc()
    ).all()
    return jsonify({
        'resumes': [
            {
                'id': r.id,
                'filename': r.original_name,
                'status': r.status,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            }
            for r in resumes
        ]
    })


@api_bp.route('/resumes/<int:resume_id>')
@login_required
def resume_detail(resume_id):
    """Get resume analysis details."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    analysis = resume.analysis
    if not analysis:
        return jsonify({'error': 'Resume not analyzed'}), 404
    return jsonify({
        'id': resume.id,
        'filename': resume.original_name,
        'analysis': {
            'overall_score': analysis.overall_score,
            'keyword_score': analysis.keyword_score,
            'grammar_score': analysis.grammar_score,
            'formatting_score': analysis.formatting_score,
            'readability_score': analysis.readability_score,
            'professional_score': analysis.professional_score,
            'strengths': analysis.strengths,
            'weaknesses': analysis.weaknesses,
            'suggestions': analysis.suggestions,
            'skills': analysis.skills,
        }
    })


@api_bp.route('/resumes/<int:resume_id>/reanalyze', methods=['POST'])
@login_required
def reanalyze(resume_id):
    """Re-analyze a resume via API."""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    try:
        analysis = analyze_resume(resume.id)
        return jsonify({'status': 'success', 'overall_score': analysis.overall_score})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/job-match', methods=['POST'])
@login_required
def api_job_match():
    """Analyze job match via API."""
    data = request.get_json() or {}
    resume_id = data.get('resume_id')
    job_description = data.get('job_description', '')
    if not resume_id or not job_description:
        return jsonify({'error': 'resume_id and job_description required'}), 400

    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    if not resume.analysis:
        return jsonify({'error': 'Resume not analyzed'}), 400

    analysis = resume.analysis
    extracted = {
        'skills': analysis.skills,
        'experience': analysis.experience,
        'projects': analysis.projects,
        'certifications': analysis.certifications,
        'linkedin': analysis.candidate_linkedin,
        'summary': '',
    }
    result = analyze_job_match(
        extracted, job_description, data.get('job_title', ''), data.get('company_name', '')
    )
    return jsonify(result)
