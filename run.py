"""
AI Resume Screening System - Application Entry Point
=====================================================
Production-grade Flask application for AI-powered resume analysis.
"""
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
