"""
ATS Scorer
==========
Comprehensive ATS scoring engine with weighted multi-dimensional analysis.
"""
import re
from .parser import count_words, count_sentences, detect_sections


# ============================================================
# Essential Keywords for ATS
# ============================================================

ESSENTIAL_ATS_KEYWORDS = {
    'skills', 'experience', 'education', 'projects', 'certifications',
    'summary', 'objective', 'achievements', 'responsibilities',
    'developed', 'managed', 'led', 'implemented', 'designed',
    'created', 'improved', 'optimized', 'collaborated', 'delivered',
    'python', 'java', 'javascript', 'sql', 'html', 'css',
    'team', 'leadership', 'communication', 'problem solving',
    'results', 'impact', 'performance', 'growth', 'revenue',
}

REQUIRED_SECTIONS = [
    'contact', 'summary', 'education', 'experience', 'skills', 'projects'
]


def calculate_keyword_score(text):
    """Score based on presence of essential ATS keywords."""
    if not text:
        return 0

    text_lower = text.lower()
    found = 0
    for keyword in ESSENTIAL_ATS_KEYWORDS:
        if keyword in text_lower:
            found += 1

    score = min(100, (found / len(ESSENTIAL_ATS_KEYWORDS)) * 130)
    return round(score, 1)


def calculate_formatting_score(text):
    """Score based on resume formatting quality."""
    score = 100
    issues = []

    word_count = count_words(text)

    # Check resume length
    if word_count < 150:
        score -= 25
        issues.append('Resume is too short. Aim for 300-700 words.')
    elif word_count > 1200:
        score -= 15
        issues.append('Resume is too long. Keep it under 2 pages (700 words).')
    elif word_count < 300:
        score -= 10
        issues.append('Resume could use more content. Aim for at least 300 words.')

    # Check for bullet points or structured content
    lines = text.split('\n')
    bullet_lines = sum(1 for l in lines if l.strip().startswith(('•', '-', '●', '○', '▪', '*', '►')))
    if bullet_lines < 3:
        score -= 15
        issues.append('Use more bullet points to structure your content.')

    # Check for consistent formatting
    empty_lines = sum(1 for l in lines if not l.strip())
    if empty_lines > len(lines) * 0.4:
        score -= 10
        issues.append('Too many empty lines. Reduce whitespace for a cleaner look.')

    # Check for sections
    sections = detect_sections(text)
    missing = []
    for req in REQUIRED_SECTIONS:
        if req not in sections:
            missing.append(req.capitalize())
            score -= 8

    if missing:
        issues.append(f'Missing sections: {", ".join(missing)}')

    # Check for ALL CAPS overuse
    caps_lines = sum(1 for l in lines if l.strip() and l.strip().isupper() and len(l.strip()) > 20)
    if caps_lines > 3:
        score -= 10
        issues.append('Avoid excessive use of ALL CAPS.')

    return max(0, round(score, 1)), issues, missing


def calculate_readability_score(text):
    """Score based on text readability."""
    if not text:
        return 0

    score = 80  # Start at good baseline

    sentences = count_sentences(text)
    words = count_words(text)

    if sentences == 0:
        return 30

    avg_sentence_length = words / sentences

    # Optimal sentence length: 15-25 words
    if 10 <= avg_sentence_length <= 25:
        score += 10
    elif avg_sentence_length > 35:
        score -= 15
    elif avg_sentence_length < 8:
        score -= 10

    # Check for complex words (3+ syllables approximation)
    complex_words = len([w for w in text.split() if len(w) > 12])
    if complex_words > words * 0.15:
        score -= 10

    # Check for passive voice
    passive_patterns = [
        r'\b(?:was|were|been|being|is|are|am)\s+\w+(?:ed|en)\b',
    ]
    passive_count = 0
    for pattern in passive_patterns:
        passive_count += len(re.findall(pattern, text, re.IGNORECASE))

    if passive_count > sentences * 0.3:
        score -= 10

    return max(0, min(100, round(score, 1)))


def calculate_grammar_score(text):
    """Score based on grammar quality indicators."""
    if not text:
        return 0

    score = 85
    lines = text.split('\n')

    # Check for consistent tense
    past_tense = len(re.findall(r'\b\w+ed\b', text))
    present_tense = len(re.findall(r'\b(?:manage|develop|create|design|implement|build|lead|work)\b', text, re.IGNORECASE))

    if past_tense > 0 and present_tense > 0:
        ratio = min(past_tense, present_tense) / max(past_tense, present_tense)
        if ratio > 0.4:  # Mixed tenses
            score -= 10

    # Check for first person pronouns (not recommended in resumes)
    first_person = len(re.findall(r'\b(?:I|me|my|mine|myself)\b', text))
    if first_person > 5:
        score -= 10
    elif first_person > 2:
        score -= 5

    # Check for common typo patterns
    typo_patterns = [
        r'\b(teh|adn|taht|wiht|thier|recieve|seperate|occured|definately)\b',
    ]
    for pattern in typo_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score -= 5

    # Check for proper capitalization at line starts
    bad_caps = 0
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 5 and stripped[0].islower():
            if not stripped.startswith(('•', '-', '●', '○', '▪', '*')):
                bad_caps += 1
    if bad_caps > 3:
        score -= 5

    return max(0, min(100, round(score, 1)))


def calculate_professional_score(text, extracted_data):
    """Score based on professional quality indicators."""
    score = 50

    # Contact information completeness
    if extracted_data.get('email'):
        score += 8
    if extracted_data.get('phone'):
        score += 7
    if extracted_data.get('linkedin'):
        score += 8
    if extracted_data.get('github'):
        score += 5
    if extracted_data.get('name'):
        score += 5

    # Skills presence
    skills = extracted_data.get('skills', [])
    if len(skills) >= 10:
        score += 10
    elif len(skills) >= 5:
        score += 5

    # Education
    if extracted_data.get('education'):
        score += 5

    # Experience / Projects
    if extracted_data.get('experience'):
        score += 8
    if extracted_data.get('projects'):
        score += 7

    # Certifications
    if extracted_data.get('certifications'):
        score += 5

    # Action verbs
    verbs = extracted_data.get('action_verbs', [])
    if len(verbs) >= 8:
        score += 5
    elif len(verbs) >= 4:
        score += 3

    return max(0, min(100, round(score, 1)))


def calculate_section_scores(text, extracted_data):
    """Calculate individual section scores."""
    sections = {}

    # Contact Score
    contact_fields = ['name', 'email', 'phone', 'linkedin', 'github', 'address']
    contact_present = sum(1 for f in contact_fields if extracted_data.get(f))
    sections['contact_score'] = round(min(100, (contact_present / len(contact_fields)) * 120), 1)

    # Summary Score
    found_sections = detect_sections(text)
    sections['summary_score'] = 75.0 if 'summary' in found_sections else 20.0

    # Education Score
    edu = extracted_data.get('education', [])
    if len(edu) >= 2:
        sections['education_score'] = 90.0
    elif len(edu) == 1:
        sections['education_score'] = 70.0
    else:
        sections['education_score'] = 15.0

    # Experience Score
    exp = extracted_data.get('experience', [])
    if len(exp) >= 3:
        sections['experience_score'] = 90.0
    elif len(exp) >= 1:
        sections['experience_score'] = 65.0
    else:
        sections['experience_score'] = 20.0

    # Skills Score
    skills = extracted_data.get('skills', [])
    if len(skills) >= 12:
        sections['skills_score'] = 95.0
    elif len(skills) >= 6:
        sections['skills_score'] = 70.0
    elif len(skills) >= 3:
        sections['skills_score'] = 50.0
    else:
        sections['skills_score'] = 20.0

    # Projects Score
    projects = extracted_data.get('projects', [])
    if len(projects) >= 3:
        sections['projects_score'] = 90.0
    elif len(projects) >= 1:
        sections['projects_score'] = 60.0
    else:
        sections['projects_score'] = 15.0

    # Certifications Score
    certs = extracted_data.get('certifications', [])
    if len(certs) >= 3:
        sections['certifications_score'] = 90.0
    elif len(certs) >= 1:
        sections['certifications_score'] = 60.0
    else:
        sections['certifications_score'] = 25.0

    return sections


def generate_strengths(extracted_data, scores):
    """Generate list of resume strengths."""
    strengths = []

    if scores.get('overall_score', 0) >= 70:
        strengths.append('Strong overall ATS compatibility score')
    if len(extracted_data.get('skills', [])) >= 8:
        strengths.append(f'Good skill variety with {len(extracted_data["skills"])} skills identified')
    if extracted_data.get('linkedin'):
        strengths.append('LinkedIn profile included for professional networking')
    if extracted_data.get('github'):
        strengths.append('GitHub profile showcases coding projects')
    if len(extracted_data.get('experience', [])) >= 2:
        strengths.append('Multiple work experience entries demonstrate career growth')
    if len(extracted_data.get('projects', [])) >= 2:
        strengths.append('Multiple projects showcase practical skills')
    if len(extracted_data.get('certifications', [])) >= 1:
        strengths.append('Professional certifications add credibility')
    if len(extracted_data.get('action_verbs', [])) >= 5:
        strengths.append('Good use of action verbs for impact-driven descriptions')
    if scores.get('grammar_score', 0) >= 75:
        strengths.append('Well-written with good grammar quality')
    if len(extracted_data.get('education', [])) >= 1:
        strengths.append('Educational qualifications are clearly listed')
    if extracted_data.get('email') and extracted_data.get('phone'):
        strengths.append('Complete contact information provided')

    if not strengths:
        strengths.append('Resume has been submitted for analysis')

    return strengths[:8]


def generate_weaknesses(extracted_data, scores, formatting_issues, missing_sections):
    """Generate list of resume weaknesses."""
    weaknesses = []

    if scores.get('overall_score', 0) < 50:
        weaknesses.append('Low ATS compatibility — resume may get filtered by automated systems')
    if not extracted_data.get('linkedin'):
        weaknesses.append('No LinkedIn profile URL found — add it for recruiter visibility')
    if not extracted_data.get('github') and any(s.lower() in ['python', 'javascript', 'java'] for s in extracted_data.get('skills', [])):
        weaknesses.append('No GitHub profile — consider adding it to showcase your code')
    if len(extracted_data.get('skills', [])) < 5:
        weaknesses.append('Too few skills listed — aim for at least 8-10 relevant skills')
    if len(extracted_data.get('action_verbs', [])) < 3:
        weaknesses.append('Weak action verbs — use strong verbs like "Developed", "Implemented", "Achieved"')
    if not extracted_data.get('experience') and not extracted_data.get('internships'):
        weaknesses.append('No work experience or internships listed')

    for issue in formatting_issues[:3]:
        weaknesses.append(issue)

    for section in missing_sections[:3]:
        weaknesses.append(f'{section} section is missing from your resume')

    if not weaknesses:
        weaknesses.append('Consider getting feedback from industry professionals')

    return weaknesses[:8]


def generate_suggestions(extracted_data, scores, missing_sections):
    """Generate actionable improvement suggestions."""
    suggestions = []

    if scores.get('keyword_score', 0) < 60:
        suggestions.append('Add more industry-relevant keywords to pass ATS filters. Research job descriptions in your target role.')
    if scores.get('formatting_score', 0) < 60:
        suggestions.append('Improve formatting by using clear section headers, bullet points, and consistent spacing.')
    if 'summary' in missing_sections:
        suggestions.append('Add a Professional Summary at the top of your resume — 2-3 sentences highlighting your key strengths.')
    if len(extracted_data.get('skills', [])) < 8:
        suggestions.append('Expand your skills section with both technical and soft skills relevant to your target role.')
    if not extracted_data.get('certifications'):
        suggestions.append('Consider adding relevant certifications to stand out (AWS, Google, Microsoft, etc.).')
    if len(extracted_data.get('projects', [])) < 2:
        suggestions.append('Add more projects with clear descriptions of technologies used and outcomes achieved.')
    if scores.get('readability_score', 0) < 60:
        suggestions.append('Improve readability by using shorter sentences and simpler language.')
    if scores.get('grammar_score', 0) < 70:
        suggestions.append('Review grammar and spelling. Use past tense for previous roles and present for current.')
    if not extracted_data.get('achievements'):
        suggestions.append('Add an Achievements section to highlight awards, recognitions, or quantified results.')

    suggestions.append('Tailor your resume for each job application by matching keywords from the job description.')
    suggestions.append('Keep your resume to 1-2 pages for optimal ATS compatibility.')

    return suggestions[:10]


def determine_health_status(overall_score):
    """Determine resume health status based on overall score."""
    if overall_score >= 80:
        return 'excellent'
    elif overall_score >= 60:
        return 'good'
    elif overall_score >= 40:
        return 'average'
    else:
        return 'poor'


def find_missing_keywords(text):
    """Find important ATS keywords missing from the resume."""
    text_lower = text.lower()
    missing = []

    important_keywords = [
        'leadership', 'teamwork', 'communication', 'problem solving',
        'results', 'impact', 'achievement', 'certified', 'managed',
        'developed', 'implemented', 'designed', 'optimized', 'delivered',
        'collaborated', 'analytical', 'strategic', 'innovation',
    ]

    for keyword in important_keywords:
        if keyword not in text_lower:
            missing.append(keyword.capitalize())

    return missing[:15]


# ============================================================
# Main Scoring Pipeline
# ============================================================

def calculate_all_scores(text, extracted_data):
    """Run the complete scoring pipeline."""
    keyword_score = calculate_keyword_score(text)
    formatting_score, formatting_issues, missing_sections = calculate_formatting_score(text)
    readability_score = calculate_readability_score(text)
    grammar_score = calculate_grammar_score(text)
    professional_score = calculate_professional_score(text, extracted_data)
    section_scores = calculate_section_scores(text, extracted_data)

    # Weighted overall score
    overall_score = (
        keyword_score * 0.20 +
        formatting_score * 0.15 +
        readability_score * 0.10 +
        grammar_score * 0.10 +
        professional_score * 0.25 +
        (sum(section_scores.values()) / len(section_scores)) * 0.20
    )
    overall_score = round(min(100, overall_score), 1)

    # Strength and weakness scores
    strength_score = min(100, round((overall_score + professional_score) / 2, 1))
    weakness_score = round(100 - overall_score, 1)

    scores = {
        'overall_score': overall_score,
        'keyword_score': keyword_score,
        'grammar_score': grammar_score,
        'formatting_score': formatting_score,
        'readability_score': readability_score,
        'professional_score': professional_score,
        'strength_score': strength_score,
        'weakness_score': weakness_score,
        **section_scores,
    }

    # Generate AI content
    strengths = generate_strengths(extracted_data, scores)
    weaknesses = generate_weaknesses(extracted_data, scores, formatting_issues, missing_sections)
    suggestions = generate_suggestions(extracted_data, scores, missing_sections)
    missing_keywords = find_missing_keywords(text)
    health_status = determine_health_status(overall_score)

    return {
        'scores': scores,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions,
        'missing_keywords': missing_keywords,
        'formatting_issues': formatting_issues,
        'missing_sections': missing_sections,
        'health_status': health_status,
        'word_count': count_words(text),
        'sentence_count': count_sentences(text),
    }
