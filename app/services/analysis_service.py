"""
Analysis Service
================
Orchestrates the resume analysis pipeline: parse -> extract -> score -> persist.
"""
from ..ai.parser import extract_text_from_pdf, count_words, count_sentences
from ..ai.extractor import extract_all
from ..ai.grammar import analyze_grammar
from ..ai.scorer import calculate_all_scores
from ..models import Resume, AnalysisResult, ResumeHistory
from ..extensions import db


def analyze_resume(resume_id):
    """Run the full analysis pipeline on a resume and persist results."""
    resume = Resume.query.get_or_404(resume_id)

    # Extract text from PDF
    text, page_count = extract_text_from_pdf(
        os_join_resume_path(resume)
    )
    resume.raw_text = text
    resume.page_count = page_count
    resume.status = 'analyzing'
    db.session.commit()

    # Extract structured data
    extracted = extract_all(text)

    # Grammar analysis
    grammar = analyze_grammar(text)

    # Calculate all scores
    results = calculate_all_scores(text, extracted)

    # Update grammar score with detailed grammar analysis
    results['scores']['grammar_score'] = grammar['score']

    # Create or update AnalysisResult
    analysis = resume.analysis
    if analysis is None:
        analysis = AnalysisResult(resume_id=resume.id)
        db.session.add(analysis)

    # Populate contact info
    analysis.candidate_name = extracted.get('name', '')
    analysis.candidate_email = extracted.get('email', '')
    analysis.candidate_phone = extracted.get('phone', '')
    analysis.candidate_address = extracted.get('address', '')
    analysis.candidate_linkedin = extracted.get('linkedin', '')
    analysis.candidate_github = extracted.get('github', '')

    # Populate sections
    analysis.skills = extracted.get('skills', [])
    analysis.technical_skills = extracted.get('technical_skills', [])
    analysis.soft_skills = extracted.get('soft_skills', [])
    analysis.education = extracted.get('education', [])
    analysis.experience = extracted.get('experience', [])
    analysis.projects = extracted.get('projects', [])
    analysis.certifications = extracted.get('certifications', [])
    analysis.achievements = extracted.get('achievements', [])
    analysis.languages = extracted.get('languages', [])
    analysis.internships = extracted.get('internships', [])

    # Populate scores
    scores = results['scores']
    analysis.overall_score = scores.get('overall_score', 0)
    analysis.keyword_score = scores.get('keyword_score', 0)
    analysis.grammar_score = scores.get('grammar_score', 0)
    analysis.formatting_score = scores.get('formatting_score', 0)
    analysis.readability_score = scores.get('readability_score', 0)
    analysis.professional_score = scores.get('professional_score', 0)
    analysis.strength_score = scores.get('strength_score', 0)
    analysis.weakness_score = scores.get('weakness_score', 0)
    analysis.contact_score = scores.get('contact_score', 0)
    analysis.summary_score = scores.get('summary_score', 0)
    analysis.education_score = scores.get('education_score', 0)
    analysis.experience_score = scores.get('experience_score', 0)
    analysis.skills_score = scores.get('skills_score', 0)
    analysis.projects_score = scores.get('projects_score', 0)
    analysis.certifications_score = scores.get('certifications_score', 0)

    # Populate AI content
    analysis.strengths = results.get('strengths', [])
    analysis.weaknesses = results.get('weaknesses', [])
    analysis.suggestions = results.get('suggestions', [])
    analysis.missing_keywords = results.get('missing_keywords', [])
    analysis.formatting_issues = results.get('formatting_issues', [])
    analysis.action_verbs = extracted.get('action_verbs', [])
    analysis.missing_sections = results.get('missing_sections', [])

    # Health status
    analysis.health_status = results.get('health_status', 'average')
    analysis.word_count = results.get('word_count', count_words(text))
    analysis.sentence_count = results.get('sentence_count', count_sentences(text))

    # Mark resume complete
    resume.status = 'completed'
    db.session.commit()

    # Record history snapshot
    if resume.user_id:
        ResumeHistory.record(resume.user_id, resume, analysis)
        db.session.commit()

    return analysis


def os_join_resume_path(resume):
    """Return the absolute path to the resume file."""
    import os
    from flask import current_app
    return os.path.join(current_app.config['UPLOAD_FOLDER'], resume.filename)
