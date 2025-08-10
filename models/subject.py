from models import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)  # Keep the relationship with chapters
    # Remove the quizzes relationship
