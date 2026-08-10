"""
Resume Builder Blueprint
========================
Build professional resumes with modern templates.
"""
import io
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
)
from flask_login import login_required, current_user
from ..forms.main import ResumeBuilderForm
from ..ai.builder import generate_resume_html
from ..utils.helpers import generate_report_filename
from ..extensions import db
from ..models import Resume, ActivityLog

builder_bp = Blueprint('builder', __name__)


@builder_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Resume builder form."""
    form = ResumeBuilderForm()
    if form.validate_on_submit():
        data = {
            'full_name': form.full_name.data,
            'job_title': form.job_title.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'address': form.address.data,
            'linkedin': form.linkedin.data,
            'github': form.github.data,
            'website': form.website.data,
            'summary': form.summary.data,
            'skills': form.skills.data,
            'languages': form.languages.data,
            'education': form.education.data,
            'experience': form.experience.data,
            'projects': form.projects.data,
            'certifications': form.certifications.data,
        }
        html_content = generate_resume_html(data, form.template.data)
        return render_template(
            'builder/preview.html',
            resume_html=html_content,
            template=form.template.data,
            full_name=form.full_name.data
        )
    return render_template('builder/index.html', form=form)


@builder_bp.route('/preview', methods=['POST'])
@login_required
def preview():
    """Generate preview from posted data."""
    template = request.form.get('template', 'minimal')
    data = {
        'full_name': request.form.get('full_name', ''),
        'job_title': request.form.get('job_title', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'address': request.form.get('address', ''),
        'linkedin': request.form.get('linkedin', ''),
        'github': request.form.get('github', ''),
        'website': request.form.get('website', ''),
        'summary': request.form.get('summary', ''),
        'skills': request.form.get('skills', ''),
        'languages': request.form.get('languages', ''),
        'education': request.form.get('education', ''),
        'experience': request.form.get('experience', ''),
        'projects': request.form.get('projects', ''),
        'certifications': request.form.get('certifications', ''),
    }
    html_content = generate_resume_html(data, template)
    return render_template(
        'builder/preview.html',
        resume_html=html_content,
        template=template,
        full_name=data['full_name']
    )


@builder_bp.route('/templates')
@login_required
def templates():
    """Template gallery."""
    templates = [
        {'name': 'minimal', 'label': 'Minimal', 'desc': 'Clean and simple'},
        {'name': 'google', 'label': 'Google', 'desc': 'Modern and bold'},
        {'name': 'microsoft', 'label': 'Microsoft', 'desc': 'Corporate style'},
        {'name': 'harvard', 'label': 'Harvard', 'desc': 'Academic classic'},
        {'name': 'creative', 'label': 'Creative', 'desc': 'Colorful and unique'},
    ]
    return render_template('builder/templates.html', templates=templates)
