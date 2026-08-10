"""
Portfolio Blueprint
===================
Developer portfolio and project documentation.
"""
from flask import Blueprint, render_template
from flask_login import login_required

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/')
def index():
    """Developer portfolio."""
    return render_template('portfolio/index.html')


@portfolio_bp.route('/architecture')
def architecture():
    """Architecture documentation."""
    return render_template('portfolio/architecture.html')


@portfolio_bp.route('/docs')
def docs():
    """Project documentation."""
    return render_template('portfolio/docs.html')
