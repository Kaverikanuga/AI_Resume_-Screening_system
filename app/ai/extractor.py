"""
Information Extractor
=====================
Extracts structured data from resume text using NER, regex, and keyword matching.
"""
import re


# ============================================================
# Skill Dictionaries
# ============================================================

TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'go', 'golang',
    'rust', 'swift', 'kotlin', 'scala', 'php', 'perl', 'r', 'matlab', 'dart', 'lua',
    'objective-c', 'shell', 'bash', 'powershell', 'assembly', 'haskell', 'elixir', 'clojure',
    'groovy', 'visual basic', 'vb.net', 'fortran', 'cobol',

    # Web Development
    'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'bootstrap', 'tailwind',
    'react', 'reactjs', 'react.js', 'angular', 'angularjs', 'vue', 'vuejs', 'vue.js',
    'svelte', 'next.js', 'nextjs', 'nuxt.js', 'gatsby', 'jquery', 'webpack', 'vite',
    'node.js', 'nodejs', 'express', 'express.js', 'django', 'flask', 'fastapi',
    'spring', 'spring boot', 'asp.net', '.net', 'laravel', 'rails', 'ruby on rails',

    # Databases
    'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch',
    'cassandra', 'dynamodb', 'firebase', 'supabase', 'oracle', 'sql server',
    'mariadb', 'neo4j', 'couchdb', 'influxdb',

    # Cloud & DevOps
    'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
    'jenkins', 'terraform', 'ansible', 'ci/cd', 'github actions', 'gitlab ci',
    'circleci', 'travis ci', 'nginx', 'apache', 'linux', 'unix',

    # Data Science & ML
    'machine learning', 'deep learning', 'artificial intelligence', 'ai', 'ml',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy',
    'scipy', 'matplotlib', 'seaborn', 'plotly', 'tableau', 'power bi',
    'natural language processing', 'nlp', 'computer vision', 'opencv',
    'data analysis', 'data science', 'data engineering', 'big data',
    'hadoop', 'spark', 'apache spark', 'kafka', 'airflow',

    # Mobile Development
    'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic',
    'swift ui', 'swiftui', 'jetpack compose', 'kotlin multiplatform',

    # Tools & Technologies
    'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'trello',
    'postman', 'swagger', 'rest api', 'restful', 'graphql', 'grpc',
    'microservices', 'api design', 'system design', 'design patterns',
    'agile', 'scrum', 'kanban', 'devops', 'sre', 'testing',
    'unit testing', 'selenium', 'cypress', 'jest', 'pytest', 'junit',
    'figma', 'adobe xd', 'sketch', 'photoshop', 'illustrator',
    'blockchain', 'solidity', 'web3', 'cybersecurity', 'networking',
    'embedded systems', 'iot', 'arduino', 'raspberry pi',

    # Certifications-related
    'aws certified', 'azure certified', 'google certified',
    'comptia', 'cissp', 'ccna', 'ccnp', 'pmp', 'scrum master',
}

SOFT_SKILLS = {
    'leadership', 'communication', 'teamwork', 'problem solving', 'problem-solving',
    'critical thinking', 'time management', 'project management', 'creativity',
    'adaptability', 'collaboration', 'analytical', 'decision making',
    'attention to detail', 'organizational', 'interpersonal', 'presentation',
    'negotiation', 'mentoring', 'coaching', 'strategic thinking',
    'conflict resolution', 'emotional intelligence', 'customer service',
    'public speaking', 'written communication', 'research', 'innovation',
    'work ethic', 'self-motivated', 'multitasking', 'flexibility',
    'planning', 'delegation', 'accountability', 'initiative',
}

ACTION_VERBS = {
    'achieved', 'administered', 'analyzed', 'architected', 'automated',
    'built', 'collaborated', 'conducted', 'configured', 'created',
    'debugged', 'delivered', 'deployed', 'designed', 'developed',
    'directed', 'documented', 'drove', 'engineered', 'established',
    'evaluated', 'executed', 'expanded', 'facilitated', 'formulated',
    'generated', 'guided', 'identified', 'implemented', 'improved',
    'increased', 'initiated', 'innovated', 'integrated', 'launched',
    'led', 'maintained', 'managed', 'mentored', 'migrated',
    'modernized', 'monitored', 'negotiated', 'optimized', 'orchestrated',
    'organized', 'oversaw', 'partnered', 'performed', 'pioneered',
    'planned', 'presented', 'programmed', 'published', 'redesigned',
    'reduced', 'refactored', 'resolved', 'restructured', 'revamped',
    'scaled', 'simplified', 'spearheaded', 'streamlined', 'supervised',
    'tested', 'trained', 'transformed', 'troubleshot', 'upgraded',
}


# ============================================================
# Contact Information Extraction
# ============================================================

def extract_email(text):
    """Extract email address from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ''


def extract_phone(text):
    """Extract phone number from text."""
    patterns = [
        r'(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}',
        r'(?:\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}',
        r'\+?\d{1,4}[\-\s]?\(?\d{1,4}\)?[\-\s]?\d{3,4}[\-\s]?\d{3,4}',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    return ''


def extract_linkedin(text):
    """Extract LinkedIn URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else ''


def extract_github(text):
    """Extract GitHub URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0] if matches else ''


def extract_name(text):
    """Extract candidate name from the first few lines of resume."""
    lines = text.strip().split('\n')
    for line in lines[:5]:
        clean = line.strip()
        if not clean or len(clean) < 2:
            continue
        # Skip lines that look like contact info
        if re.search(r'[@|phone|email|address|linkedin|github|http]', clean, re.IGNORECASE):
            continue
        if re.search(r'[0-9]{5,}', clean):
            continue
        # Skip common resume headers
        if re.match(r'(?i)^(resume|curriculum vitae|cv|profile|objective|summary)', clean):
            continue
        # Likely a name if it has 2-4 words of mostly letters
        words = clean.split()
        if 1 <= len(words) <= 5 and all(re.match(r'^[A-Za-z.\'-]+$', w) for w in words):
            return clean
    return ''


def extract_address(text):
    """Extract address from text."""
    lines = text.split('\n')[:10]
    for line in lines:
        clean = line.strip()
        # Look for patterns that suggest an address (city, state, zip)
        if re.search(r'(?i)\b(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr|blvd|city|state|zip|pin)\b', clean):
            return clean
        if re.search(r'\b\d{5,6}\b', clean) and len(clean) > 10 and ',' in clean:
            return clean
    return ''


# ============================================================
# Skills Extraction
# ============================================================

def extract_skills(text):
    """Extract all skills from resume text."""
    text_lower = text.lower()
    found_technical = set()
    found_soft = set()

    for skill in TECHNICAL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_technical.add(skill.title() if len(skill) > 3 else skill.upper())

    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_soft.add(skill.title())

    all_skills = sorted(found_technical | found_soft)
    return list(all_skills), sorted(found_technical), sorted(found_soft)


def extract_action_verbs(text):
    """Extract action verbs used in resume."""
    text_lower = text.lower()
    found = set()
    for verb in ACTION_VERBS:
        if re.search(r'\b' + verb + r'\b', text_lower):
            found.add(verb.capitalize())
    return sorted(found)


# ============================================================
# Section Extraction
# ============================================================

def extract_education(text):
    """Extract education entries from text."""
    entries = []
    education_keywords = [
        r'(?i)(?:bachelor|master|phd|doctorate|associate|diploma|b\.?tech|m\.?tech|b\.?e|m\.?e|'
        r'b\.?sc|m\.?sc|b\.?com|m\.?com|b\.?a|m\.?a|b\.?ca|m\.?ca|bba|mba|'
        r'high school|secondary|12th|10th|hsc|ssc|cbse|icse|igcse|ib|gcse|'
        r'b\.?s\.?|m\.?s\.?|ph\.?d)'
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines):
        clean = line.strip()
        if not clean:
            continue
        for pattern in education_keywords:
            if re.search(pattern, clean):
                # Gather context: current line + next 2 lines
                entry_lines = [clean]
                for j in range(1, 3):
                    if i + j < len(lines) and lines[i + j].strip():
                        entry_lines.append(lines[i + j].strip())
                entry = ' | '.join(entry_lines)
                if entry not in entries and len(entry) > 5:
                    entries.append(entry)
                break

    return entries[:5]  # Max 5 education entries


def extract_experience(text):
    """Extract work experience entries from text."""
    entries = []
    exp_patterns = [
        r'(?i)(?:software|senior|junior|lead|principal|staff|intern|associate|manager|director|vp|'
        r'engineer|developer|analyst|consultant|architect|designer|administrator|coordinator|'
        r'specialist|executive|officer|head|chief|president)\s',
        r'\b(?:20[0-2]\d|19\d{2})\b.*?(?:present|current|20[0-2]\d|19\d{2})',
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines):
        clean = line.strip()
        if not clean or len(clean) < 10:
            continue
        for pattern in exp_patterns:
            if re.search(pattern, clean):
                entry_lines = [clean]
                for j in range(1, 3):
                    if i + j < len(lines) and lines[i + j].strip():
                        next_line = lines[i + j].strip()
                        if len(next_line) > 5:
                            entry_lines.append(next_line)
                entry = ' | '.join(entry_lines)
                if entry not in entries and len(entry) > 10:
                    entries.append(entry)
                break

    return entries[:8]  # Max 8 experience entries


def extract_projects(text):
    """Extract project entries from text."""
    entries = []
    lines = text.split('\n')
    sections = detect_project_section(text)

    if sections:
        for line in sections.split('\n'):
            clean = line.strip()
            if clean and len(clean) > 10 and not re.match(r'(?i)^projects?\s*$', clean):
                entries.append(clean)
    else:
        project_indicators = [
            r'(?i)(?:developed|built|created|designed|implemented)\s+(?:a\s+)?(?:web|mobile|desktop|ai|ml)',
            r'(?i)(?:github\.com|project|application|system|tool|platform|website|app)\b',
        ]
        for i, line in enumerate(lines):
            clean = line.strip()
            if not clean:
                continue
            for pattern in project_indicators:
                if re.search(pattern, clean) and len(clean) > 15:
                    entries.append(clean)
                    break

    return entries[:6]  # Max 6 projects


def detect_project_section(text):
    """Find the projects section in text."""
    lines = text.split('\n')
    start = -1
    for i, line in enumerate(lines):
        if re.match(r'(?i)^\s*projects?\s*$', line.strip()):
            start = i + 1
            break

    if start == -1:
        return ''

    end = len(lines)
    section_headers = [
        r'(?i)^\s*(?:education|experience|skills|certifications?|achievements?|'
        r'languages?|hobbies|interests?|references?|contact|summary|objective)\s*$'
    ]
    for i in range(start, len(lines)):
        for header in section_headers:
            if re.match(header, lines[i].strip()):
                end = i
                break
        if end != len(lines):
            break

    return '\n'.join(lines[start:end])


def extract_certifications(text):
    """Extract certification entries."""
    entries = []
    cert_patterns = [
        r'(?i)(?:certified|certification|certificate|credential|accreditation|license)',
        r'(?i)(?:aws|azure|google|oracle|cisco|comptia|pmp|scrum|itil|prince2|'
        r'six sigma|salesforce|hubspot|meta|ibm|microsoft)',
    ]

    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if not clean or len(clean) < 5:
            continue
        for pattern in cert_patterns:
            if re.search(pattern, clean):
                if clean not in entries and len(clean) > 5:
                    entries.append(clean)
                break

    return entries[:10]


def extract_achievements(text):
    """Extract achievements and awards."""
    entries = []
    patterns = [
        r'(?i)(?:award|honor|prize|recognition|winner|finalist|'
        r'scholarship|distinction|dean|valedictorian|summa|magna|cum laude|'
        r'1st place|2nd place|3rd place|first place|gold medal|silver medal|rank)',
    ]

    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        for pattern in patterns:
            if re.search(pattern, clean):
                if clean not in entries:
                    entries.append(clean)
                break

    return entries[:8]


def extract_languages(text):
    """Extract spoken languages."""
    known_languages = [
        'english', 'hindi', 'spanish', 'french', 'german', 'chinese', 'mandarin',
        'japanese', 'korean', 'arabic', 'portuguese', 'russian', 'italian',
        'dutch', 'turkish', 'tamil', 'telugu', 'marathi', 'bengali', 'gujarati',
        'kannada', 'malayalam', 'punjabi', 'urdu', 'thai', 'vietnamese',
        'indonesian', 'malay', 'swedish', 'norwegian', 'danish', 'finnish',
        'polish', 'czech', 'greek', 'hebrew', 'persian', 'swahili',
    ]

    text_lower = text.lower()
    found = []
    for lang in known_languages:
        if re.search(r'\b' + lang + r'\b', text_lower):
            found.append(lang.capitalize())

    return found[:10]


def extract_internships(text):
    """Extract internship entries."""
    entries = []
    patterns = [
        r'(?i)intern(?:ship)?',
        r'(?i)(?:summer|winter|spring)\s+(?:intern|training|project)',
        r'(?i)industrial\s+training',
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines):
        clean = line.strip()
        if not clean:
            continue
        for pattern in patterns:
            if re.search(pattern, clean):
                entry_lines = [clean]
                for j in range(1, 3):
                    if i + j < len(lines) and lines[i + j].strip():
                        entry_lines.append(lines[i + j].strip())
                entry = ' | '.join(entry_lines)
                if entry not in entries:
                    entries.append(entry)
                break

    return entries[:5]


# ============================================================
# Full Extraction Pipeline
# ============================================================

def extract_all(text):
    """Run the complete extraction pipeline on resume text."""
    all_skills, technical_skills, soft_skills = extract_skills(text)

    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'address': extract_address(text),
        'linkedin': extract_linkedin(text),
        'github': extract_github(text),
        'skills': all_skills,
        'technical_skills': technical_skills,
        'soft_skills': soft_skills,
        'education': extract_education(text),
        'experience': extract_experience(text),
        'projects': extract_projects(text),
        'certifications': extract_certifications(text),
        'achievements': extract_achievements(text),
        'languages': extract_languages(text),
        'internships': extract_internships(text),
        'action_verbs': extract_action_verbs(text),
    }
