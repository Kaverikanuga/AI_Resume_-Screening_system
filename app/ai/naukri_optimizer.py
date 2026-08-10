"""
Naukri Optimizer
================
Generates Naukri profile optimization analysis.
"""
import re
from collections import Counter


def analyze_naukri(resume_data, raw_text=''):
    """Analyze resume data to generate Naukri optimization report."""
    skills = resume_data.get('skills', [])
    experience = resume_data.get('experience', [])
    raw_text_lower = (raw_text or '').lower()

    # Base scores
    resume_score = 60
    keyword_density = 50
    search_visibility = 55
    recruiter_ranking = 50
    profile_completeness = 65

    # Calculate keyword density from raw text
    density_map = Counter(re.findall(r'[a-z]+', raw_text_lower))
    common_skills_density = {}
    for skill in skills[:10]:
        skill_lower = skill.lower()
        common_skills_density[skill] = density_map.get(skill_lower, 0)

    avg_density = sum(common_skills_density.values()) / max(len(common_skills_density), 1)
    if avg_density >= 3:
        keyword_density += 20
    elif avg_density >= 1:
        keyword_density += 10

    # Missing keywords
    missing_keywords = find_missing_naukri_keywords(raw_text_lower)

    # Improvement suggestions
    improvement_suggestions = []
    if missing_keywords:
        improvement_suggestions.append(
            f'Add missing keywords: {", ".join(missing_keywords[:5])} to improve recruiter search.'
        )
    if len(skills) < 10:
        improvement_suggestions.append('List at least 10 skills to match recruiter filters.')
        resume_score -= 5
    if len(experience) < 2:
        improvement_suggestions.append('Add detailed work experience with responsibilities and achievements.')
        resume_score -= 8
    if not resume_data.get('linkedin'):
        improvement_suggestions.append('Add your LinkedIn and other social profile links.')
        profile_completeness -= 8
    if not resume_data.get('certifications'):
        improvement_suggestions.append('Add certifications to increase recruiter ranking.')
        recruiter_ranking -= 5

    # Top skills
    top_skills = sorted(common_skills_density.items(), key=lambda x: x[1], reverse=True)[:8]
    top_skills = [s[0] for s in top_skills]

    # Adjust scores
    search_visibility += min(20, len(top_skills) * 2)
    recruiter_ranking += min(20, len(experience) * 4)
    profile_completeness += min(15, len(skills))
    resume_score += min(15, len(experience) * 3)

    scores = {
        'resume_score': max(0, min(100, round(resume_score, 1))),
        'keyword_density': max(0, min(100, round(keyword_density, 1))),
        'search_visibility': max(0, min(100, round(search_visibility, 1))),
        'recruiter_ranking': max(0, min(100, round(recruiter_ranking, 1))),
        'profile_completeness': max(0, min(100, round(profile_completeness, 1))),
        'missing_keywords': missing_keywords,
        'improvement_suggestions': improvement_suggestions,
        'top_skills': top_skills,
    }
    return scores


def find_missing_naukri_keywords(text_lower):
    """Find important Naukri search keywords missing from resume."""
    important = [
        'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node',
        'django', 'flask', 'mysql', 'mongodb', 'docker', 'aws', 'git', 'linux',
        'machine learning', 'data analysis', 'project management', 'communication',
        'leadership', 'teamwork', 'problem solving', 'analytical', 'certified',
    ]
    missing = []
    for kw in important:
        if kw not in text_lower:
            missing.append(kw.title())
    return missing[:12]
