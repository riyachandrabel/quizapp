from flask import Blueprint, render_template
from models import db
from models.quiz import Quiz  # Import only the Quiz model

bp = Blueprint('quiz', __name__)

@bp.route('/')
def quiz_home():
    return "Welcome to the Quiz Section"
