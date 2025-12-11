"""Main routes blueprint."""
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Render the home page.
    
    Returns:
        Rendered index template
    """
    return render_template('index.html')
