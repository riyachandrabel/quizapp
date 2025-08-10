from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from models.subject import Subject
from models.chapter import Chapter

from models.quiz import Quiz, Question,UserQuizProgress
from datetime import datetime

bp = Blueprint('user', __name__)

# Initialize LoginManager
login_manager = LoginManager()

from sqlalchemy.orm import Session

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Use session.get for SQLAlchemy 2.0+



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']

        # Convert dob (string) to a datetime.date object
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('user.register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('user.register'))

        # Use a valid hash method for the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create and save the new user
        new_user = User(
            username=username,
            password=hashed_password,
            full_name=full_name,
            qualification=qualification,
            dob=dob_date,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@bp.route('/')
@login_required
def dashboard():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    for chapter in chapters:
        chapter.quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
        for quiz in chapter.quizzes:
            progress = UserQuizProgress.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
            if progress:
                quiz.score = progress.score
                quiz.completed = True
            else:
                quiz.score = None
                quiz.completed = False
    return render_template('user_dashboard.html', subjects=subjects, name=current_user.full_name, user_id=current_user.id)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('user.login'))

@bp.route('/start_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f"question_{question.id}")
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
    

        # Handle user progress (optional)
        flash(f'You scored {score}/{len(questions)} in the quiz.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('start_quiz.html', quiz=quiz, questions=questions)




# @bp.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
# @login_required
# def submit_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     questions = Question.query.filter_by(quiz_id=quiz_id).all()

#     # Fetch user answers from the form
#     user_answers = {}
#     for question in questions:
#         answer = request.form.get(f'question_{question.id}')
#         if answer:
#             user_answers[question.id] = int(answer)  # Convert to integer
#         else:
#             user_answers[question.id] = None  # Explicitly set None for unanswered questions

#     # Validate answers
#     if None in user_answers.values():  # Check if any question was left unanswered
#         flash('Please answer all questions before submitting the quiz.', 'error')
#         return redirect(url_for('user.start_quiz', quiz_id=quiz_id))

#     # Calculate the score
#     score = 0
#     for question in questions:
#         if user_answers[question.id] == question.correct_option:
#             score += 1

#     # Save the score and answers in the database
#     user_progress = UserQuizProgress.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
#     if not user_progress:
#         user_progress = UserQuizProgress(
#             user_id=current_user.id,
#             quiz_id=quiz_id,
#             score=score/len(questions)*100,
#             completed_on=datetime.now(),
#             user_answers=user_answers  # Save user answers
#         )
#         db.session.add(user_progress)
#     else:
#         user_progress.score = score
#         user_progress.completed_on = datetime.now()
#         user_progress.user_answers = user_answers  # Update user answers

#     db.session.commit()

#     flash('Quiz submitted successfully! Your score has been updated.', 'success')
#     return redirect(url_for('user.dashboard'))

@bp.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Fetch user answers from the form
    user_answers = {}
    for question in questions:
        answer = request.form.get(f'question_{question.id}')
        if answer:
            user_answers[question.id] = int(answer)  # Convert to integer
        else:
            user_answers[question.id] = None  # Unanswered questions are marked as None

    # Calculate the score (treat unanswered questions as incorrect)
    score = 0
    for question in questions:
        user_answer = user_answers[question.id]
        if user_answer and user_answer == question.correct_option:
            score += 1

    # Save the score and answers in the database
    user_progress = UserQuizProgress.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if not user_progress:
        user_progress = UserQuizProgress(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=(score / len(questions)) * 100 if questions else 0,  # Handle empty quiz case
            completed_on=datetime.now(),
            user_answers=user_answers  # Save user answers
        )
        db.session.add(user_progress)
    else:
        user_progress.score = (score / len(questions)) * 100 if questions else 0
        user_progress.completed_on = datetime.now()
        user_progress.user_answers = user_answers  # Update user answers

    db.session.commit()

    flash('Quiz submitted successfully! Your score has been updated.', 'success')
    return redirect(url_for('user.dashboard'))


@bp.route('/view_quiz/<int:quiz_id>', methods=['GET'])
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    # Fetch progress data
    progress = UserQuizProgress.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if not progress:
        flash('You have not completed this quiz yet.', 'error')
        return redirect(url_for('user.dashboard'))

    # Parse user_answers from progress (JSON field)
    user_answers = progress.user_answers or {}

    # Process each question to include text, user answer, and correct answer
    processed_questions = []
    for question in questions:
        user_answer_id = int(user_answers.get(str(question.id), 0))  # Convert user answer ID to int
        user_answer_text = getattr(question, f"option_{user_answer_id}", "Not Answered")  # Retrieve user answer text
        correct_answer_text = getattr(question, f"option_{question.correct_option}")  # Retrieve correct answer text

        processed_questions.append({
            "text": question.question_text,
            "user_answer": user_answer_text,
            "correct_answer": correct_answer_text,
        })

    # Render the template with processed questions
    return render_template('view_quiz.html', quiz=quiz, processed_questions=processed_questions, progress=progress)

# @bp.route('/user_summary')
# @login_required
# def user_summary():
#     user_id = current_user.id
#     subjects = Subject.query.all()
#     summary_data = []
#     for subject in subjects:
#         subject_data = {
#             'subject_name': subject.name,
#             'quizzes': []
#         }
#         for chapter in subject.chapters:
#             quizzes = Quiz.query.join(UserQuizProgress, Quiz.id == UserQuizProgress.quiz_id).filter(UserQuizProgress.user_id == user_id, Quiz.chapter_id == chapter.id).all()
#             for quiz in quizzes:
#                 progress = UserQuizProgress.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
#                 subject_data['quizzes'].append({
#                     'quiz_title': quiz.title,
#                     'score': progress.score if progress else 0
#                 })
#         summary_data.append(subject_data)
#     return {'summary_data': summary_data}
from sqlalchemy.orm import load_only

# @bp.route('/user_summary')
# @login_required
# def user_summary():
#     user_id = current_user.id
#     subjects = Subject.query.options(load_only('id', 'name', 'chapters')).all()
#     summary_data = []
#     for subject in subjects:
#         subject_data = {
#             'subject_name': subject.name,
#             'quizzes': []
#         }
#         # Ensure chapters are loaded
#         for chapter in subject.chapters:
#             quizzes = Quiz.query.join(UserQuizProgress, Quiz.id == UserQuizProgress.quiz_id).filter(
#                 UserQuizProgress.user_id == user_id, Quiz.chapter_id == chapter.id
#             ).all()
#             for quiz in quizzes:
#                 progress = UserQuizProgress.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
#                 subject_data['quizzes'].append({
#                     'quiz_title': quiz.title,
#                     'score': progress.score if progress else 0
#                 })
#         # Include subjects even if no quizzes exist
#         if not subject_data['quizzes']:
#             subject_data['quizzes'].append({'quiz_title': 'No Quizzes', 'score': 0})
#         summary_data.append(subject_data)
#     return {'summary_data': summary_data}

from sqlalchemy.orm import joinedload
import logging
from flask import jsonify

# Configure logging to see errors in the terminal
logging.basicConfig(level=logging.DEBUG)

@bp.route('/user_summary')
@login_required
def user_summary():
    try:
        user_id = current_user.id
        # Use joinedload to eagerly load the chapters relationship
        subjects = Subject.query.options(joinedload(Subject.chapters)).all()
        summary_data = []
        for subject in subjects:
            subject_data = {
                'subject_name': subject.name,
                'quizzes': []
            }
            # Loop through chapters (now properly loaded)
            for chapter in subject.chapters:
                # Fetch quizzes with progress for this user and chapter
                quizzes = Quiz.query.join(UserQuizProgress, Quiz.id == UserQuizProgress.quiz_id).filter(
                    UserQuizProgress.user_id == user_id, Quiz.chapter_id == chapter.id
                ).all()
                for quiz in quizzes:
                    progress = UserQuizProgress.query.filter_by(user_id=user_id, quiz_id=quiz.id).first()
                    subject_data['quizzes'].append({
                        'quiz_title': quiz.title,
                        'score': progress.score if progress else 0
                    })
            # Include subjects even if no quizzes exist
            if not subject_data['quizzes']:
                subject_data['quizzes'].append({'quiz_title': 'No Quizzes', 'score': 0})
            summary_data.append(subject_data)
        return {'summary_data': summary_data}
    except Exception as e:
        logging.error(f"Error in user_summary: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to load summary data'}), 500