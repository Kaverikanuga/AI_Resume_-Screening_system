"""
LinkedIn Optimizer
==================
Generates LinkedIn profile optimization analysis and suggestions.
"""
import re


def analyze_linkedin(resume_data):
    """Analyze resume data to generate LinkedIn optimization report."""
    skills = resume_data.get('skills', [])
    technical = resume_data.get('technical_skills', [])
    experience = resume_data.get('experience', [])
    projects = resume_data.get('projects', [])
    certifications = resume_data.get('certifications', [])
    education = resume_data.get('education', [])

    # Base scores
    linkedin_score = 55
    visibility_score = 60
    recruiter_visibility = 55
    ssi_score = 50
    profile_completeness = 60

    # Headline suggestion
    title = resume_data.get('summary', '')
    headline = build_headline(resume_data)

    # About suggestion
    about = build_about(resume_data)

    # Skills suggestions
    skills_suggestions = []
    if len(skills) < 10:
        skills_suggestions.append('Add at least 10 skills to match recruiter search filters.')
    for skill in skills[:5]:
        skills_suggestions.append(f'Endorse and get endorsements for: {skill}.')
    if not certifications:
        skills_suggestions.append('Add certifications to boost your profile credibility.')
    else:
        for cert in certifications[:3]:
            skills_suggestions.append(f'Add certification: {cert} to your Licenses section.')

    # Networking tips
    networking_tips = [
        'Connect with at least 20 recruiters in your target industry weekly.',
        'Engage with content in your field by commenting thoughtfully.',
        'Post or share industry insights 2-3 times per week to boost visibility.',
        'Join LinkedIn groups related to your profession and participate actively.',
        'Personalize every connection request with a short note.',
        'Update your profile photo and banner for a professional appearance.',
    ]

    # Improvement tips
    improvement_tips = []
    if not resume_data.get('linkedin'):
        improvement_tips.append('Add your LinkedIn URL to your resume and set up a complete profile.')
        linkedin_score -= 10
        recruiter_visibility -= 10
    if len(experience) < 2:
        improvement_tips.append('Add more work experience entries with quantified achievements.')
        linkedin_score -= 8
    if len(projects) < 2:
        improvement_tips.append('Add projects to the Featured section to showcase your work.')
        visibility_score -= 8
    if not certifications:
        improvement_tips.append('Complete and add relevant certifications to increase trust.')
        ssi_score -= 8
    if len(education) < 1:
        improvement_tips.append('Add your education details to complete your profile.')
        profile_completeness -= 10

    # Comfort scores
    linkedin_score = max(0, min(100, round(linkedin_score + len(skills) * 1.5, 1)))
    visibility_score = max(0, min(100, round(visibility_score + len(technical) * 1.2, 1)))
    recruiter_visibility = max(0, min(100, round(recruiter_visibility + len(experience) * 3, 1)))
    ssi_score = max(0, min(100, round(ssi_score + len(certifications) * 4, 1)))
    profile_completeness = max(0, min(100, round(profile_completeness + len(education) * 5, 1)))

    return {
        'linkedin_score': linkedin_score,
        'visibility_score': visibility_score,
        'recruiter_visibility': recruiter_visibility,
        'ssi_score': ssi_score,
        'profile_completeness': profile_completeness,
        'headline_suggestion': headline,
        'about_suggestion': about,
        'skills_suggestions': skills_suggestions,
        'networking_tips': networking_tips,
        'improvement_tips': improvement_tips,
    }


def build_headline(resume_data):
    """Generate an optimized LinkedIn headline."""
    title = resume_data.get('job_title', '')
    skills = resume_data.get('skills', [])
    top_skills = ', '.join(skills[:3]) if skills else 'Technology Professional'
    experience_years = len(resume_data.get('experience', [])) * 2

    if title:
        headline = f'{title} | {top_skills}'
    else:
        headline = f'Software Professional | {top_skills}'
    if experience_years >= 2:
        headline += f' | {experience_years}+ years experience'
    return headline


def build_about(resume_data):
    """Generate an optimized LinkedIn About section."""
    name = resume_data.get('name', '')
    skills = resume_data.get('skills', [])
    certifications = resume_data.get('certifications', [])
    summary = resume_data.get('summary', '')

    lines = []
    if summary:
        lines.append(summary)
    else:
        lines.append(f'I am a passionate technology professional with expertise in {", ".join(skills[:5]) if skills else "software development"}.')
    lines.append('')
    lines.append('Key Skills:')
    if skills:
        lines.append(', '.join(skills[:10]))
    if certifications:
        lines.append('')
        lines.append('Certifications:')
        lines.append(', '.join(certifications[:3]))
    lines.append('')
    lines.append('Open to exciting opportunities and collaborations. Let us connect!')
    return '\n'.join(lines)
