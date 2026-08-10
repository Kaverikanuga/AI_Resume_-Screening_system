"""
Resume Parser
=============
Extracts text from PDF resumes using PyPDF2 and pdfplumber.
"""
import os
import re


def extract_text_from_pdf(filepath):
    """Extract text from a PDF file using multiple methods for best results."""
    text = ''

    # Method 1: Try pdfplumber (better for complex layouts)
    try:
        import pdfplumber
        page_count = 0
        with pdfplumber.open(filepath) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        if text.strip():
            return text.strip(), page_count
    except Exception:
        pass

    # Method 2: Fallback to PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        page_count = len(reader.pages)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
        if text.strip():
            return text.strip(), page_count
    except Exception:
        pass

    return text.strip(), 1


def detect_sections(text):
    """Detect resume sections from text."""
    section_patterns = {
        'summary': r'(?i)(?:professional\s+)?(?:summary|objective|profile|about\s+me)',
        'education': r'(?i)education(?:al)?\s*(?:background|qualifications?|details?)?',
        'experience': r'(?i)(?:work\s+)?experience|employment\s*(?:history)?|professional\s*experience|work\s*history',
        'skills': r'(?i)(?:technical\s+)?skills|competenc(?:ies|e)|expertise|technologies',
        'projects': r'(?i)projects?|portfolio|academic\s*projects?|personal\s*projects?',
        'certifications': r'(?i)certific(?:ations?|ates?)|licenses?|accreditations?',
        'achievements': r'(?i)achievements?|awards?|honors?|accomplishments?',
        'languages': r'(?i)languages?\s*(?:known|proficiency)?',
        'internships': r'(?i)internships?|training|industrial\s*training',
        'publications': r'(?i)publications?|papers?|research',
        'references': r'(?i)references?',
        'hobbies': r'(?i)hobbies|interests?|activities',
        'contact': r'(?i)contact\s*(?:info(?:rmation)?|details?)?'
    }

    found_sections = {}
    lines = text.split('\n')

    for i, line in enumerate(lines):
        clean_line = line.strip()
        if not clean_line or len(clean_line) > 60:
            continue
        for section_name, pattern in section_patterns.items():
            if re.search(pattern, clean_line):
                found_sections[section_name] = i
                break

    return found_sections


def get_section_text(text, section_name, sections_found):
    """Extract text belonging to a specific section."""
    lines = text.split('\n')
    if section_name not in sections_found:
        return ''

    start_line = sections_found[section_name] + 1
    section_keys = sorted(sections_found.items(), key=lambda x: x[1])

    end_line = len(lines)
    for i, (name, line_num) in enumerate(section_keys):
        if name == section_name and i + 1 < len(section_keys):
            end_line = section_keys[i + 1][1]
            break

    section_text = '\n'.join(lines[start_line:end_line])
    return section_text.strip()


def count_words(text):
    """Count words in text."""
    if not text:
        return 0
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def count_sentences(text):
    """Count sentences in text."""
    if not text:
        return 0
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])
