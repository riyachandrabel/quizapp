from models import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)  # Ensure chapter_id is used
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(120), nullable=False)
    option_2 = db.Column(db.String(120), nullable=False)
    option_3 = db.Column(db.String(120), nullable=False)
    option_4 = db.Column(db.String(120), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class UserQuizProgress(db.Model):
    __tablename__ = 'user_quiz_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    completed_on = db.Column(db.DateTime, nullable=False)
    user_answers = db.Column(JSON, nullable=True)

