"""
Editor Blueprint
================
Live resume editor with auto-save and PDF export.
"""
import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
)
from flask_login import login_required, current_user
from ..models import Resume, ActivityLog
from ..extensions import db
from ..services.report_service import export_resume_pdf

editor_bp = Blueprint('editor', __name__)


@editor_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Live resume editor."""
    resume_text = request.form.get('resume_content', '')
    if request.method == 'POST' and resume_text:
        # Auto-save to an editable resume
        resume = Resume(
            user_id=current_user.id,
            filename='editor_resume.txt',
            original_name='Edited Resume',
            raw_text=resume_text,
            status='edited'
        )
        db.session.add(resume)
        db.session.commit()
        ActivityLog.log(
            current_user.id, 'Resume edited',
            description='Saved edited resume content', icon='fa-edit', color='info'
        )
        flash('Resume saved.', 'success')
        return render_template('editor/index.html', resume_text=resume_text)
    return render_template('editor/index.html', resume_text=resume_text)


@editor_bp.route('/export', methods=['POST'])
@login_required
def export():
    """Export edited resume as PDF."""
    resume_text = request.form.get('resume_content', '')
    if not resume_text:
        flash('Nothing to export.', 'warning')
        return redirect(url_for('editor.index'))
    try:
        pdf = export_resume_pdf(resume_text, current_user)
        return send_file(
            pdf,
            as_attachment=True,
            download_name='edited_resume.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f'PDF export error: {e}')
        flash('Failed to export PDF.', 'danger')
        return redirect(url_for('editor.index'))
