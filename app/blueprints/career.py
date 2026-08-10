"""
Career Blueprint
================
AI Career Assistant with chat-style interface.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import CareerSuggestion, Resume, ActivityLog
from ..ai.career import get_career_response
from ..extensions import db

career_bp = Blueprint('career', __name__)


@career_bp.route('/')
@login_required
def index():
    """Career assistant page."""
    history = CareerSuggestion.query.filter_by(user_id=current_user.id).order_by(
        CareerSuggestion.created_at.desc()
    ).limit(20).all()
    return render_template('career/index.html', history=history)


@career_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    """Handle career assistant query."""
    query = request.form.get('query', '').strip()
    category = request.form.get('category', 'general')
    if not query:
        flash('Please enter a question.', 'warning')
        return redirect(url_for('career.index'))

    # Build user profile from latest analyzed resume
    profile_data = {}
    latest_resume = Resume.query.filter_by(user_id=current_user.id, status='completed').order_by(
        Resume.created_at.desc()
    ).first()
    if latest_resume and latest_resume.analysis:
        analysis = latest_resume.analysis
        profile_data = {
            'skills': analysis.skills,
            'technical_skills': analysis.technical_skills,
            'experience': analysis.experience,
            'projects': analysis.projects,
            'certifications': analysis.certifications,
            'education': analysis.education,
        }

    response_text = get_career_response(query, category, profile_data)

    # Extract recommendations
    recommended_skills = []
    recommended_certs = []
    recommended_projects = []
    learning_resources = []
    interview_tips = []

    if category in ('skill', 'general'):
        recommended_skills = extract_list_items(response_text, '- ')
    if category in ('cert', 'general'):
        recommended_certs = extract_list_items(response_text, '- ')
    if category in ('project', 'general'):
        recommended_projects = extract_list_items(response_text, '- ')
    if category in ('placement', 'roadmap'):
        learning_resources = extract_list_items(response_text, '- ')
    if category == 'interview':
        interview_tips = extract_list_items(response_text, '- ')

    suggestion = CareerSuggestion(
        user_id=current_user.id,
        query=query,
        response=response_text,
        category=category,
        recommended_skills=recommended_skills,
        recommended_certs=recommended_certs,
        recommended_projects=recommended_projects,
        learning_resources=learning_resources,
        interview_tips=interview_tips,
    )
    db.session.add(suggestion)
    db.session.commit()

    ActivityLog.log(
        current_user.id, 'Career advice',
        description=f'Asked: {query[:50]}', icon='fa-robot', color='warning'
    )
    # Return JSON if requested via fetch API
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'response': response_text})
    return redirect(url_for('career.index'))


def extract_list_items(text, prefix):
    """Extract list items from response text."""
    items = []
    for line in text.split('\n'):
        line_stripped = line.strip()
        if line_stripped.startswith(prefix):
            item = line_stripped[len(prefix):].strip()
            if item:
                items.append(item)
    return items[:10]
