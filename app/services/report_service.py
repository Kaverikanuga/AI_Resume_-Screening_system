"""
Report Service
==============
Generates professional PDF reports using ReportLab.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def _create_styles():
    """Create report styles."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ReportTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#141e30'),
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='ReportSubtitle', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#555555'),
        spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#1a2980'),
        spaceBefore=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='Body', parent=styles['Normal'],
        fontSize=10, leading=14, spaceAfter=6
    ))
    return styles


def generate_analysis_report_pdf(resume, analysis, user):
    """Generate a professional ATS analysis report PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch
    )
    styles = _create_styles()
    story = []

    # Title
    story.append(Paragraph('ResumeAI Pro — ATS Analysis Report', styles['ReportTitle']))
    story.append(Paragraph(
        f'Generated for {user.full_name} on {datetime.utcnow().strftime("%B %d, %Y")}',
        styles['ReportSubtitle']
    ))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1a2980')))

    # Resume info
    story.append(Paragraph('Resume Details', styles['SectionHeader']))
    resume_data = [
        ['Candidate', analysis.candidate_name or 'N/A'],
        ['File', resume.original_name],
        ['Pages', str(resume.page_count)],
        ['Word Count', str(analysis.word_count)],
    ]
    t = Table(resume_data, colWidths=[1.5 * inch, 4.8 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4ff')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a2980')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f7f9fc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    # Scores
    story.append(Paragraph('ATS Score Overview', styles['SectionHeader']))
    score_data = [
        ['Metric', 'Score'],
        ['Overall ATS Score', f'{analysis.overall_score:.1f} / 100'],
        ['Keyword Score', f'{analysis.keyword_score:.1f}'],
        ['Formatting Score', f'{analysis.formatting_score:.1f}'],
        ['Readability Score', f'{analysis.readability_score:.1f}'],
        ['Grammar Score', f'{analysis.grammar_score:.1f}'],
        ['Professional Score', f'{analysis.professional_score:.1f}'],
        ['Health Status', analysis.health_status.upper()],
    ]
    t = Table(score_data, colWidths=[2.5 * inch, 3.8 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2980')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f9fc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    # Section Scores
    story.append(Paragraph('Section Analysis', styles['SectionHeader']))
    section_data = [
        ['Section', 'Score'],
        ['Contact', f'{analysis.contact_score:.1f}'],
        ['Summary', f'{analysis.summary_score:.1f}'],
        ['Education', f'{analysis.education_score:.1f}'],
        ['Experience', f'{analysis.experience_score:.1f}'],
        ['Skills', f'{analysis.skills_score:.1f}'],
        ['Projects', f'{analysis.projects_score:.1f}'],
        ['Certifications', f'{analysis.certifications_score:.1f}'],
    ]
    t = Table(section_data, colWidths=[2.5 * inch, 3.8 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#141e30')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f9fc')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)

    # Strengths
    story.append(Paragraph('Key Strengths', styles['SectionHeader']))
    for strength in analysis.strengths[:6]:
        story.append(Paragraph(f'• {strength}', styles['Body']))

    # Weaknesses
    story.append(Paragraph('Areas for Improvement', styles['SectionHeader']))
    for weakness in analysis.weaknesses[:6]:
        story.append(Paragraph(f'• {weakness}', styles['Body']))

    # Suggestions
    story.append(Paragraph('Recommendations', styles['SectionHeader']))
    for suggestion in analysis.suggestions[:8]:
        story.append(Paragraph(f'• {suggestion}', styles['Body']))

    # Footer
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#cccccc')))
    story.append(Paragraph(
        'Generated by ResumeAI Pro — AI Resume Screening System',
        styles['ReportSubtitle']
    ))

    doc.build(story)
    buf.seek(0)
    return buf


def export_resume_pdf(resume_text, user):
    """Export plain resume text as a simple PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch
    )
    styles = _create_styles()
    story = []
    story.append(Paragraph(f'Resume — {user.full_name}', styles['ReportTitle']))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1a2980')))
    story.append(Spacer(1, 0.15 * inch))

    for line in resume_text.split('\n'):
        if line.strip():
            story.append(Paragraph(line.strip(), styles['Body']))
        else:
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    buf.seek(0)
    return buf
