"""
Resume Builder
==============
Generates HTML resume content from form data using modern templates.
"""
import html
import re


def generate_resume_html(form_data, template='minimal'):
    """Generate HTML resume from form data and template."""
    data = sanitize_builder_data(form_data)
    templates = {
        'google': render_google,
        'microsoft': render_microsoft,
        'harvard': render_harvard,
        'creative': render_creative,
        'minimal': render_minimal,
    }
    renderer = templates.get(template, render_minimal)
    return renderer(data)


def sanitize_builder_data(data):
    """Escape and structure builder form data."""
    def clean(value):
        if not value:
            return ''
        return html.escape(str(value).strip())

    skills = [clean(s.strip()) for s in data.get('skills', '').split(',') if clean(s.strip())]
    languages = [clean(l.strip()) for l in data.get('languages', '').split(',') if clean(l.strip())]
    education = [clean(e.strip()) for e in data.get('education', '').split('\n') if clean(e.strip())]
    experience = [clean(e.strip()) for e in data.get('experience', '').split('\n') if clean(e.strip())]
    projects = [clean(p.strip()) for p in data.get('projects', '').split('\n') if clean(p.strip())]
    certifications = [clean(c.strip()) for c in data.get('certifications', '').split('\n') if clean(c.strip())]

    return {
        'full_name': clean(data.get('full_name', '')),
        'job_title': clean(data.get('job_title', '')),
        'email': clean(data.get('email', '')),
        'phone': clean(data.get('phone', '')),
        'address': clean(data.get('address', '')),
        'linkedin': clean(data.get('linkedin', '')),
        'github': clean(data.get('github', '')),
        'website': clean(data.get('website', '')),
        'summary': clean(data.get('summary', '')),
        'skills': skills,
        'languages': languages,
        'education': education,
        'experience': experience,
        'projects': projects,
        'certifications': certifications,
    }


def _contact_line(data):
    """Build contact info line."""
    parts = []
    if data['email']:
        parts.append(data['email'])
    if data['phone']:
        parts.append(data['phone'])
    if data['address']:
        parts.append(data['address'])
    if data['linkedin']:
        parts.append(data['linkedin'])
    if data['github']:
        parts.append(data['github'])
    if data['website']:
        parts.append(data['website'])
    return ' | '.join(parts)


def _list_items(items, max_items=None):
    """Render list items."""
    if max_items:
        items = items[:max_items]
    return ''.join(f'<li>{item}</li>' for item in items)


def render_minimal(data):
    """Minimal clean template."""
    lines = []
    lines.append('<div class="resume-minimal resume-page">')
    lines.append('  <h1 class="resume-name">' + data['full_name'] + '</h1>')
    if data['job_title']:
        lines.append('  <p class="resume-title">' + data['job_title'] + '</p>')
    contact = _contact_line(data)
    if contact:
        lines.append('  <p class="resume-contact">' + contact + '</p>')
    if data['summary']:
        lines.append('  <h2>Professional Summary</h2>')
        lines.append('  <p>' + data['summary'] + '</p>')
    if data['skills']:
        lines.append('  <h2>Skills</h2>')
        lines.append('  <ul>' + _list_items(data['skills']) + '</ul>')
    if data['experience']:
        lines.append('  <h2>Work Experience</h2>')
        lines.append('  <ul>' + _list_items(data['experience']) + '</ul>')
    if data['projects']:
        lines.append('  <h2>Projects</h2>')
        lines.append('  <ul>' + _list_items(data['projects']) + '</ul>')
    if data['education']:
        lines.append('  <h2>Education</h2>')
        lines.append('  <ul>' + _list_items(data['education']) + '</ul>')
    if data['certifications']:
        lines.append('  <h2>Certifications</h2>')
        lines.append('  <ul>' + _list_items(data['certifications']) + '</ul>')
    if data['languages']:
        lines.append('  <h2>Languages</h2>')
        lines.append('  <p>' + ', '.join(data['languages']) + '</p>')
    lines.append('</div>')
    return '\n'.join(lines)


def render_google(data):
    """Google-inspired clean template."""
    lines = []
    lines.append('<div class="resume-google resume-page">')
    lines.append('  <div class="g-header">')
    lines.append('    <span class="g-letter">' + (data['full_name'][:1] if data['full_name'] else 'R') + '</span>')
    lines.append('    <div class="g-header-text">')
    lines.append('      <h1>' + data['full_name'] + '</h1>')
    lines.append('      <p>' + (data['job_title'] or 'Professional') + '</p>')
    lines.append('    </div>')
    lines.append('  </div>')
    contact = _contact_line(data)
    if contact:
        lines.append('  <p class="resume-contact">' + contact + '</p>')
    if data['summary']:
        lines.append('  <h2>Summary</h2><p>' + data['summary'] + '</p>')
    if data['skills']:
        lines.append('  <h2>Skills</h2><ul>' + _list_items(data['skills']) + '</ul>')
    if data['experience']:
        lines.append('  <h2>Experience</h2><ul>' + _list_items(data['experience']) + '</ul>')
    if data['projects']:
        lines.append('  <h2>Projects</h2><ul>' + _list_items(data['projects']) + '</ul>')
    if data['education']:
        lines.append('  <h2>Education</h2><ul>' + _list_items(data['education']) + '</ul>')
    if data['certifications']:
        lines.append('  <h2>Certifications</h2><ul>' + _list_items(data['certifications']) + '</ul>')
    lines.append('</div>')
    return '\n'.join(lines)


def render_microsoft(data):
    """Microsoft corporate template."""
    lines = []
    lines.append('<div class="resume-microsoft resume-page">')
    lines.append('  <div class="ms-header">')
    lines.append('    <h1>' + data['full_name'] + '</h1>')
    lines.append('    <p>' + (data['job_title'] or 'Professional') + '</p>')
    lines.append('  </div>')
    contact = _contact_line(data)
    if contact:
        lines.append('  <p class="resume-contact">' + contact + '</p>')
    if data['summary']:
        lines.append('  <h2>Professional Summary</h2><p>' + data['summary'] + '</p>')
    if data['experience']:
        lines.append('  <h2>Experience</h2><ul>' + _list_items(data['experience']) + '</ul>')
    if data['projects']:
        lines.append('  <h2>Projects</h2><ul>' + _list_items(data['projects']) + '</ul>')
    if data['education']:
        lines.append('  <h2>Education</h2><ul>' + _list_items(data['education']) + '</ul>')
    if data['skills']:
        lines.append('  <h2>Skills</h2><ul>' + _list_items(data['skills']) + '</ul>')
    if data['certifications']:
        lines.append('  <h2>Certifications</h2><ul>' + _list_items(data['certifications']) + '</ul>')
    lines.append('</div>')
    return '\n'.join(lines)


def render_harvard(data):
    """Harvard academic template."""
    lines = []
    lines.append('<div class="resume-harvard resume-page">')
    lines.append('  <div class="hv-header">')
    lines.append('    <h1>' + data['full_name'] + '</h1>')
    lines.append('    <p class="hv-title">' + (data['job_title'] or '') + '</p>')
    contact = _contact_line(data)
    if contact:
        lines.append('    <p class="resume-contact">' + contact + '</p>')
    lines.append('  </div>')
    if data['summary']:
        lines.append('  <h2>Summary</h2><p>' + data['summary'] + '</p>')
    if data['education']:
        lines.append('  <h2>Education</h2><ul>' + _list_items(data['education']) + '</ul>')
    if data['experience']:
        lines.append('  <h2>Experience</h2><ul>' + _list_items(data['experience']) + '</ul>')
    if data['projects']:
        lines.append('  <h2>Projects</h2><ul>' + _list_items(data['projects']) + '</ul>')
    if data['skills']:
        lines.append('  <h2>Skills</h2><ul>' + _list_items(data['skills']) + '</ul>')
    if data['certifications']:
        lines.append('  <h2>Certifications</h2><ul>' + _list_items(data['certifications']) + '</ul>')
    lines.append('</div>')
    return '\n'.join(lines)


def render_creative(data):
    """Creative color-accented template."""
    lines = []
    lines.append('<div class="resume-creative resume-page">')
    lines.append('  <div class="cr-header">')
    lines.append('    <h1>' + data['full_name'] + '</h1>')
    lines.append('    <p>' + (data['job_title'] or 'Professional') + '</p>')
    lines.append('  </div>')
    contact = _contact_line(data)
    if contact:
        lines.append('  <p class="resume-contact">' + contact + '</p>')
    if data['summary']:
        lines.append('  <h2>About</h2><p>' + data['summary'] + '</p>')
    if data['skills']:
        lines.append('  <div class="cr-grid"><h2>Skills</h2><ul>' + _list_items(data['skills']) + '</ul></div>')
    if data['projects']:
        lines.append('  <h2>Projects</h2><ul>' + _list_items(data['projects']) + '</ul>')
    if data['experience']:
        lines.append('  <h2>Experience</h2><ul>' + _list_items(data['experience']) + '</ul>')
    if data['education']:
        lines.append('  <h2>Education</h2><ul>' + _list_items(data['education']) + '</ul>')
    if data['certifications']:
        lines.append('  <h2>Certifications</h2><ul>' + _list_items(data['certifications']) + '</ul>')
    if data['languages']:
        lines.append('  <h2>Languages</h2><p>' + ', '.join(data['languages']) + '</p>')
    lines.append('</div>')
    return '\n'.join(lines)
