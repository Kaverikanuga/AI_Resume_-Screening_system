"""
Upload Blueprint
================
Resume upload, validation, and analysis initiation.
"""
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Resume, ActivityLog, Notification
from ..utils.helpers import allowed_file, save_uploaded_file, get_file_size
from ..ai.parser import extract_text_from_pdf
from ..services.analysis_service import analyze_resume

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload page and handler."""
    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or file.filename == '':
            flash('Please select a file to upload.', 'danger')
            return redirect(url_for('upload.upload'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF resume.', 'danger')
            return redirect(url_for('upload.upload'))

        try:
            filename, original_name = save_uploaded_file(file)
            if not filename:
                flash('Failed to save file.', 'danger')
                return redirect(url_for('upload.upload'))

            resume = Resume(
                user_id=current_user.id,
                filename=filename,
                original_name=original_name,
                file_size=get_file_size(filename),
                status='uploaded'
            )
            db.session.add(resume)
            db.session.commit()

            ActivityLog.log(
                current_user.id, 'Resume uploaded',
                description=f'Uploaded "{original_name}"', icon='fa-file-upload', color='success'
            )
            Notification.create(
                current_user.id, 'Resume Received',
                f'Your resume "{original_name}" has been uploaded. Analysis is in progress.',
                type='success', icon='fa-file-upload', link=url_for('dashboard.history')
            )

            # Run analysis
            try:
                analyze_resume(resume.id)
                Notification.create(
                    current_user.id, 'Analysis Complete',
                    'Your resume has been analyzed. View your ATS score and recommendations.',
                    type='info', icon='fa-check-circle', link=url_for('analysis.view', resume_id=resume.id)
                )
                return redirect(url_for('analysis.view', resume_id=resume.id))
            except Exception as e:
                resume.status = 'failed'
                db.session.commit()
                current_app.logger.error(f'Analysis failed for resume {resume.id}: {e}')
                flash('Analysis encountered an error. Please try again.', 'danger')
                return redirect(url_for('dashboard.history'))

        except Exception as e:
            current_app.logger.error(f'Upload error: {e}')
            flash('An error occurred during upload. Please try again.', 'danger')

    return render_template('upload/upload.html')


@upload_bp.route('/preview', methods=['POST'])
@login_required
def preview():
    """API endpoint to preview PDF file details."""
    file = request.files.get('resume')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    try:
        filename, original_name = save_uploaded_file(file)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        text, page_count = extract_text_from_pdf(filepath)
        size_kb = round(os.path.getsize(filepath) / 1024, 2)
        # Clean up preview file
        os.remove(filepath)
        return jsonify({
            'filename': original_name,
            'pages': page_count,
            'size': size_kb,
            'words': len(text.split()),
            'preview': text[:2000]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
