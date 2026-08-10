"""
Job Matching Engine
===================
Analyzes resume against a job description using NLP and sklearn.
"""
import re
from collections import Counter
from .extractor import TECHNICAL_SKILLS, SOFT_SKILLS


# Common programming/tech keywords for skill extraction
TECH_PATTERNS = [
    'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node',
    'django', 'flask', 'fastapi', 'spring', 'sql', 'mysql', 'postgresql', 'mongodb',
    'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'linux',
    'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'machine learning',
    'deep learning', 'nlp', 'data analysis', 'data science', 'tableau', 'power bi',
    'html', 'css', 'bootstrap', 'tailwind', 'rest api', 'graphql', 'microservices',
    'c', 'c++', 'c#', 'go', 'ruby', 'swift', 'kotlin', 'php', 'r'
]


def extract_job_skills(text):
    """Extract in-demand skills from a job description."""
    text_lower = text.lower()
    skills = []
    for skill in sorted(TECH_PATTERNS):
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills.append(skill.title())
    return skills


def extract_resume_skills(skills_list):
    """Normalize resume skills to lowercase for matching."""
    return [s.lower() for s in skills_list]


def keyword_match(text_a, text_b):
    """Compute simple keyword overlap ratio."""
    tokens_a = set(re.findall(r'[a-z0-9]+', text_a.lower()))
    tokens_b = set(re.findall(r'[a-z0-9]+', text_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    # Focus on meaningful words (length > 3)
    meaningful_a = {t for t in tokens_a if len(t) > 3}
    meaningful_b = {t for t in tokens_b if len(t) > 3}
    if not meaningful_a or not meaningful_b:
        return 0.0
    overlap = meaningful_a & meaningful_b
    score = len(overlap) / min(len(meaningful_a), len(meaningful_b))
    return round(min(1.0, score), 4)


def semantic_similarity(resume_text, job_text):
    """Compute TF-IDF cosine similarity between resume and job text."""
    # Import sklearn lazily so heavy NumPy/OpenBLAS libraries are only loaded
    # when job matching is actually used, not at app startup (which avoids
    # duplicate heavy initialization during Flask's debug auto-reloader).
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
        corpus = [resume_text, job_text]
        matrix = vectorizer.fit_transform(corpus)
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(sim), 4)
    except Exception:
        return 0.0


def analyze_job_match(resume_data, job_description, job_title='', company_name=''):
    """
    Full job match analysis.

    resume_data: dict from extract_all() with keys including skills, experience, projects.
    """
    resume_text = ' '.join(resume_data.get('skills', []))
    resume_text += ' ' + ' '.join(resume_data.get('experience', []))
    resume_text += ' ' + ' '.join(resume_data.get('projects', []))
    resume_text += ' ' + ' '.join(resume_data.get('certifications', []))
    resume_text += ' ' + resume_data.get('summary', '') if resume_data.get('summary') else ''

    job_skills = extract_job_skills(job_description)
    resume_skills = extract_resume_skills(resume_data.get('skills', []))
    resume_skills_lower = set(resume_skills)

    matching_skills = []
    missing_skills = []
    for skill in job_skills:
        if skill.lower() in resume_skills_lower:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    kw_match = keyword_match(resume_text, job_description)
    sem_match = semantic_similarity(resume_text, job_description)

    # Weighted match percentage
    skill_score = len(matching_skills) / max(len(job_skills), 1)
    if not job_skills:
        skill_score = 0

    match_percentage = round(
        min(100, (skill_score * 0.45 + kw_match * 0.35 + sem_match * 0.20) * 100), 1
    )

    # ATS compatibility based on keyword coverage
    ats_compatibility = round(min(100, kw_match * 100 + skill_score * 30), 1)

    # Job readiness score
    job_readiness = round(min(100, (match_percentage * 0.6 + ats_compatibility * 0.4)), 1)

    # Skill gap analysis
    skill_gaps = []
    for skill in missing_skills:
        skill_gaps.append({
            'skill': skill,
            'importance': 'High' if skill in job_skills[:5] else 'Medium',
            'suggestion': f'Add {skill} to your resume or learn it to increase your match score.'
        })

    # Learning suggestions
    learning_suggestions = []
    for skill in missing_skills[:5]:
        learning_suggestions.append(
            f'Learn {skill} through online courses (Coursera, Udemy, freeCodeCamp) and build a project using it.'
        )

    # Interview questions
    interview_questions = generate_interview_questions(resume_data, job_description)

    # Salary estimate
    salary_estimate = estimate_salary(job_title, job_skills)

    # Recruiter suggestions
    recruiter_suggestions = generate_recruiter_suggestions(resume_data, missing_skills)

    return {
        'match_percentage': match_percentage,
        'ats_compatibility': min(100, round(ats_compatibility, 1)),
        'job_readiness_score': job_readiness,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'keyword_matches': [],
        'skill_gaps': skill_gaps,
        'learning_suggestions': learning_suggestions,
        'interview_questions': interview_questions,
        'recruiter_suggestions': recruiter_suggestions,
        'salary_estimate': salary_estimate,
    }


def generate_interview_questions(resume_data, job_description):
    """Generate role-specific interview questions."""
    questions = [
        'Tell me about yourself and your background.',
        'Describe your most challenging project and how you overcame obstacles.',
        'How do you stay updated with the latest industry trends?',
        'Describe a time you worked in a team to achieve a goal.',
        'Where do you see your career in the next 3-5 years?',
    ]
    skills = resume_data.get('skills', [])
    if skills:
        top = skills[:1]
        questions.append(f'Explain your experience with {top[0]} in detail.')
    return questions[:7]


def estimate_salary(job_title, skills):
    """Estimate salary range based on job title and skills."""
    title_lower = (job_title or '').lower()
    base = 50000
    premium_skills = ['ml', 'machine learning', 'deep learning', 'ai', 'data science',
                      'cloud', 'aws', 'docker', 'kubernetes', 'blockchain']
    bonus = sum(5000 for s in premium_skills if s in skills)
    if 'senior' in title_lower or 'lead' in title_lower or 'architect' in title_lower:
        base += 30000
    elif 'junior' in title_lower or 'intern' in title_lower:
        base -= 10000
    low = base + bonus
    high = low + 40000
    return f'${low:,} - ${high:,} per year'


def generate_recruiter_suggestions(resume_data, missing_skills):
    """Generate recruiter-focused improvement suggestions."""
    suggestions = []
    if missing_skills:
        suggestions.append(
            f'Include relevant keywords like {", ".join(missing_skills[:4])} to pass ATS filters.'
        )
    if not resume_data.get('linkedin'):
        suggestions.append('Add your LinkedIn URL to allow recruiters to view your full profile.')
    if len(resume_data.get('skills', [])) < 8:
        suggestions.append('List at least 8-10 relevant skills to match recruiter search filters.')
    if not resume_data.get('certifications'):
        suggestions.append('Add industry-recognized certifications to increase recruiter trust.')
    suggestions.append('Tailor your resume summary to the specific job description.')
    return suggestions[:6]
