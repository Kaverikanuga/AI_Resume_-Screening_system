"""
AI Career Assistant
===================
Rule-based career guidance engine that generates recommendations based on
user profile and query category.
"""
import re


# Knowledge base of skills, certifications, and projects by domain
CAREER_PATHS = {
    'data science': {
        'skills': ['Python', 'Pandas', 'NumPy', 'SQL', 'Machine Learning', 'Data Visualization',
                   'Statistics', 'TensorFlow', 'Deep Learning', 'Tableau'],
        'certifications': ['Google Data Analytics', 'IBM Data Science', 'AWS Machine Learning'],
        'projects': ['Sales Forecasting Model', 'Customer Churn Prediction', 'Sentiment Analysis Dashboard'],
        'interview': ['Explain bias-variance tradeoff', 'Describe a data cleaning workflow',
                      'How do you handle missing data?'],
    },
    'machine learning': {
        'skills': ['Python', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Deep Learning', 'NLP',
                   'Computer Vision', 'MLOps', 'Pandas', 'Model Deployment'],
        'certifications': ['TensorFlow Developer', 'AWS ML Specialty', 'DeepLearning.AI Specialization'],
        'projects': ['Image Classification Model', 'Recommendation System', 'Chatbot with NLP'],
        'interview': ['Explain gradient descent', 'What is overfitting and how to prevent it?',
                      'Describe your ML project lifecycle'],
    },
    'web development': {
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'SQL', 'REST APIs',
                   'Git', 'Docker', 'AWS'],
        'certifications': ['Meta Front-End Developer', 'AWS Cloud Practitioner', 'freeCodeCamp Certifications'],
        'projects': ['E-commerce Website', 'Task Management App', 'Portfolio Website'],
        'interview': ['Explain the difference between var/let/const', 'What is closure in JS?',
                      'How does the event loop work?'],
    },
    'full stack': {
        'skills': ['React', 'Node.js', 'Express', 'MongoDB', 'SQL', 'REST APIs', 'Docker',
                   'Git', 'TypeScript', 'AWS'],
        'certifications': ['Meta Full-Stack Developer', 'IBM Full Stack Cloud Developer'],
        'projects': ['Social Media Platform', 'Real-time Chat Application', 'Inventory Management System'],
        'interview': ['How do you handle authentication?', 'Explain microservices architecture',
                      'How do you optimize database queries?'],
    },
    'backend': {
        'skills': ['Python', 'Java', 'Node.js', 'SQL', 'REST APIs', 'Microservices', 'Docker',
                   'Kubernetes', 'Redis', 'System Design'],
        'certifications': ['Meta Back-End Developer', 'IBM Back-End Development'],
        'projects': ['Payment Gateway API', 'Booking System Backend', 'Message Queue Processor'],
        'interview': ['Explain REST vs GraphQL', 'How do you design a scalable system?',
                      'Explain database indexing'],
    },
    'mobile': {
        'skills': ['Flutter', 'React Native', 'Kotlin', 'Swift', 'Firebase', 'REST APIs',
                   'UI/UX Design', 'Git'],
        'certifications': ['Meta Android Developer', 'Flutter & Dart Certification'],
        'projects': ['Fitness Tracking App', 'Food Delivery App', 'E-commerce Mobile App'],
        'interview': ['Explain state management in Flutter', 'How do you handle offline data?',
                      'Describe app deployment process'],
    },
    'devops': {
        'skills': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform', 'Ansible',
                   'Monitoring', 'Networking', 'Scripting'],
        'certifications': ['AWS DevOps Engineer', 'CKA (Kubernetes)', 'HashiCorp Terraform'],
        'projects': ['CI/CD Pipeline Setup', 'Kubernetes Cluster Deployment', 'Infrastructure as Code'],
        'interview': ['Explain CI/CD pipeline', 'What is containerization?', 'How do you monitor production?'],
    },
    'cloud': {
        'skills': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Serverless', 'Networking',
                   'Linux', 'Security', 'Terraform'],
        'certifications': ['AWS Solutions Architect', 'Azure Administrator', 'Google Cloud Engineer'],
        'projects': ['Serverless Application', 'Cloud Migration Project', 'Multi-region Deploy'],
        'interview': ['Explain AWS services', 'What is serverless computing?',
                      'How do you secure cloud resources?'],
    },
    'ai': {
        'skills': ['Python', 'TensorFlow', 'PyTorch', 'NLP', 'Deep Learning', 'Transformers',
                   'LLMs', 'RAG', 'Vector Databases', 'MLOps'],
        'certifications': ['DeepLearning.AI', 'Hugging Face', 'AWS AI Practitioner'],
        'projects': ['LLM Chat Application', 'RAG Document Assistant', 'AI Agent System'],
        'interview': ['Explain transformers', 'What is fine-tuning?', 'How do you evaluate LLMs?'],
    },
    'cybersecurity': {
        'skills': ['Network Security', 'Ethical Hacking', 'Penetration Testing', 'Linux',
                   'Cryptography', 'Security Tools', 'Python', 'Incident Response'],
        'certifications': ['CompTIA Security+', 'CEH', 'CISSP'],
        'projects': ['Vulnerability Scanner', 'Security Audit Report', 'Phishing Detection Model'],
        'interview': ['What is XSS?', 'Explain the CIA triad', 'How do you secure a network?'],
    },
}


def get_career_response(query, category='general', user_profile=None):
    """Generate a career assistant response based on query and category."""
    user_profile = user_profile or {}
    skills = [s.lower() for s in user_profile.get('skills', [])]
    aspirations = user_profile.get('aspirations', '')

    # Detect domain from query + skills
    domain = detect_domain(query, skills, aspirations)
    path = CAREER_PATHS.get(domain)

    if category == 'roadmap':
        return roadmap_response(domain, path)
    elif category == 'skill':
        return skill_response(domain, path)
    elif category == 'cert':
        return cert_response(domain, path)
    elif category == 'project':
        return project_response(domain, path)
    elif category == 'internship':
        return internship_response(domain)
    elif category == 'interview':
        return interview_response(domain, path)
    elif category == 'placement':
        return placement_response(domain, path)
    else:
        return general_response(query, domain, path)


def detect_domain(query, skills, aspirations=''):
    """Detect the user's target domain."""
    text = (query + ' ' + aspirations).lower()
    domain_map = {
        'data science': ['data science', 'data analyst', 'data analysis', 'analytics'],
        'machine learning': ['machine learning', 'ml', 'deep learning', 'model'],
        'web development': ['web development', 'frontend', 'front-end', 'html', 'css'],
        'full stack': ['full stack', 'full-stack', 'mern', 'mean'],
        'backend': ['backend', 'back-end', 'api', 'server'],
        'mobile': ['mobile', 'android', 'ios', 'flutter', 'react native'],
        'devops': ['devops', 'ci/cd', 'docker', 'kubernetes', 'infrastructure'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp'],
        'ai': ['artificial intelligence', 'llm', 'generative ai', 'chatbot', 'ai agent'],
        'cybersecurity': ['cyber', 'security', 'hacking', 'penetration'],
    }
    for domain, keywords in domain_map.items():
        for kw in keywords:
            if kw in text:
                return domain
    # Fallback to skills
    skill_map = {
        'python': 'data science', 'pandas': 'data science', 'tensorflow': 'machine learning',
        'react': 'full stack', 'node': 'backend', 'flutter': 'mobile', 'docker': 'devops',
        'aws': 'cloud', 'html': 'web development',
    }
    for skill in skills:
        if skill in skill_map:
            return skill_map[skill]
    return 'data science'


def roadmap_response(domain, path):
    """Generate career roadmap."""
    path = path or CAREER_PATHS['data science']
    lines = [
        f'Here is a 6-month career roadmap for **{domain.title()}**:',
        '',
        '**Month 1-2 — Foundations:**',
        f'- Master core skills: {", ".join(path["skills"][:4])}',
        '- Complete beginner courses and build 1-2 small projects',
        '',
        '**Month 3-4 — Intermediate:**',
        f'- Deepen skills: {", ".join(path["skills"][4:8])}',
        '- Build a portfolio project and start contributing to open source',
        '',
        '**Month 5-6 — Advanced & Job Ready:**',
        f'- Earn certifications: {", ".join(path["certifications"][:2])}',
        f'- Build capstone projects: {", ".join(path["projects"][:2])}',
        '- Prepare for interviews and apply to internships/jobs',
    ]
    return '\n'.join(lines)


def skill_response(domain, path):
    """Generate next-skills recommendations."""
    path = path or CAREER_PATHS['data science']
    return (
        f'To grow as a **{domain.title()}** professional, focus on learning these next:\n\n'
        f'**Recommended Skills:**\n- ' + '\n- '.join(path['skills'][:8]) + '\n\n'
        '**Priority:** Start with the most in-demand skills, then build projects to practice them.'
    )


def cert_response(domain, path):
    """Generate certification recommendations."""
    path = path or CAREER_PATHS['data science']
    return (
        f'These certifications will boost your **{domain.title()}** career:\n\n'
        f'**Top Certifications:**\n- ' + '\n- '.join(path['certifications'][:3]) + '\n\n'
        'Certifications add credibility and increase your recruiter ranking on ATS systems.'
    )


def project_response(domain, path):
    """Generate project recommendations."""
    path = path or CAREER_PATHS['data science']
    return (
        f'Build these **{domain.title()}** projects to strengthen your portfolio:\n\n'
        f'**Recommended Projects:**\n- ' + '\n- '.join(path['projects'][:3]) + '\n\n'
        'Host projects on GitHub and document them clearly to impress recruiters.'
    )


def internship_response(domain):
    """Generate internship recommendations."""
    companies = {
        'data science': 'data analytics startups, fintech companies, and research labs',
        'data science|machine learning': 'AI startups and tech companies',
    }
    return (
        f'To land a **{domain.title()}** internship:\n\n'
        '- Apply to internships at startups, product companies, and research labs\n'
        '- Build a strong GitHub portfolio with 2-3 solid projects\n'
        '- Network on LinkedIn and reach out to recruiters\n'
        '- Prepare for technical interviews with practice problems\n'
        '- Do 1-2 virtual internships (via Internshala, Forage) to gain experience'
    )


def interview_response(domain, path):
    """Generate interview preparation."""
    path = path or CAREER_PATHS['data science']
    return (
        f'Prepare for **{domain.title()}** interviews with these questions:\n\n'
        f'**Common Questions:**\n- ' + '\n- '.join(path['interview'][:3]) + '\n\n'
        '**Tips:** Practice on LeetCode/HackerRank, do mock interviews, and be ready to discuss your projects.'
    )


def placement_response(domain, path):
    """Generate placement preparation guidance."""
    path = path or CAREER_PATHS['data science']
    return (
        f'**Placement Preparation for {domain.title()}:**\n\n'
        '1. **Resume:** Tailor your resume with keywords from target job descriptions\n'
        '2. **Skills:** Ensure you are strong in ' + ', '.join(path['skills'][:4]) + '\n'
        '3. **Projects:** Showcase ' + ', '.join(path['projects'][:2]) + '\n'
        '4. **Aptitude:** Practice quantitative and logical reasoning daily\n'
        '5. **Mock Interviews:** Do at least 10 mock interviews before the real ones\n'
        '6. **Networking:** Connect with alumni and recruiters on LinkedIn'
    )


def general_response(query, domain, path):
    """Generate general career guidance response."""
    path = path or CAREER_PATHS['data science']
    return (
        f'Based on your query, I recommend focusing on **{domain.title()}** as your career path.\n\n'
        f'**Key skills to develop:** {", ".join(path["skills"][:6])}\n\n'
        f'**Start with:** {path["projects"][0]} to build practical experience.\n\n'
        'As you advance, earn certifications and build a strong portfolio. '
        'Would you like a detailed roadmap, skill recommendations, or interview prep?'
    )
