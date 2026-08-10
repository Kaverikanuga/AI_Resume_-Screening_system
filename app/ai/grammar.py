"""
Grammar Analyzer
================
Analyzes grammar quality, action verbs, passive voice, and writing style.
"""
import re


def analyze_grammar(text):
    """Comprehensive grammar analysis of resume text."""
    if not text:
        return {
            'score': 0,
            'passive_voice_count': 0,
            'first_person_count': 0,
            'action_verb_usage': 0,
            'avg_sentence_length': 0,
            'issues': ['No text to analyze'],
            'tips': [],
        }

    issues = []
    tips = []

    # Count passive voice instances
    passive_patterns = re.findall(
        r'\b(?:was|were|been|being|is|are|am)\s+\w+(?:ed|en)\b',
        text, re.IGNORECASE
    )
    passive_count = len(passive_patterns)

    # Count first person pronouns
    first_person = len(re.findall(r'\b(?:I|me|my|mine|myself)\b', text))

    # Count action verbs
    action_verbs = [
        'achieved', 'administered', 'analyzed', 'built', 'collaborated',
        'created', 'delivered', 'deployed', 'designed', 'developed',
        'directed', 'engineered', 'established', 'executed', 'generated',
        'implemented', 'improved', 'increased', 'initiated', 'integrated',
        'launched', 'led', 'managed', 'mentored', 'optimized',
        'organized', 'performed', 'pioneered', 'planned', 'programmed',
        'reduced', 'resolved', 'scaled', 'streamlined', 'transformed',
    ]
    action_count = 0
    text_lower = text.lower()
    for verb in action_verbs:
        action_count += len(re.findall(r'\b' + verb + r'\b', text_lower))

    # Calculate average sentence length
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    # Generate issues and tips
    if passive_count > 5:
        issues.append(f'High passive voice usage ({passive_count} instances). Use active voice instead.')
        tips.append('Replace "was developed" with "developed", "was managed" with "managed".')

    if first_person > 3:
        issues.append(f'Too many first-person pronouns ({first_person}). Resumes should avoid "I", "me", "my".')
        tips.append('Instead of "I developed a system", write "Developed a system".')

    if action_count < 3:
        issues.append('Very few action verbs detected. Use strong action verbs to describe achievements.')
        tips.append('Start bullet points with verbs like: Developed, Implemented, Designed, Built, Led.')

    if avg_length > 30:
        issues.append('Sentences are too long on average. Keep them under 25 words.')
        tips.append('Break long sentences into shorter, impactful bullet points.')

    if avg_length < 5 and len(sentences) > 5:
        issues.append('Sentences are very short. Add more detail to your descriptions.')

    # Check for quantified achievements
    numbers = re.findall(r'\b\d+%|\b\d+\+?\s*(?:users|customers|projects|team|members|clients)\b', text, re.IGNORECASE)
    if not numbers:
        tips.append('Add quantified achievements (e.g., "Improved performance by 40%", "Led a team of 5").')

    if not issues:
        tips.append('Good grammar quality! Consider having a peer review for final polish.')

    # Calculate score
    score = 85
    score -= min(20, passive_count * 3)
    score -= min(15, first_person * 3)
    if action_count < 3:
        score -= 10
    if avg_length > 30:
        score -= 10

    return {
        'score': max(0, min(100, round(score, 1))),
        'passive_voice_count': passive_count,
        'first_person_count': first_person,
        'action_verb_usage': action_count,
        'avg_sentence_length': round(avg_length, 1),
        'issues': issues,
        'tips': tips,
    }
