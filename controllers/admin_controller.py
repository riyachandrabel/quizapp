from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db
from models.subject import Subject
from models.user import User
from models.quiz import Quiz, Question, UserQuizProgress
from models.chapter import Chapter  # Import Chapter model
from datetime import datetime

bp = Blueprint('admin', __name__)

# Admin Dashboard
@bp.route('/', methods=['GET'])
def dashboard():
    if session.get('admin_logged_in'):
        # Get the search query for users from the request
        search_query = request.args.get('search', '').strip()

        # Fetch users based on the search query
        if search_query:
            users = User.query.filter(User.full_name.ilike(f'%{search_query}%')).all()
        else:
            users = User.query.all()  # Fetch all users if no search query is provided

        # Fetch all subjects and their associated chapters
        subjects = Subject.query.all()
        for subject in subjects:
            subject.chapters = Chapter.query.filter_by(subject_id=subject.id).all()

        # Fetch user performance data for the graph
        user_performance_data = db.session.query(
            User.full_name,
            db.func.avg(UserQuizProgress.score).label('average_score')
        ).join(UserQuizProgress, User.id == UserQuizProgress.user_id)\
         .group_by(User.full_name).all()

        # Render the template with the user, subject, and performance data
        return render_template('admin/admin_dashboard.html', users=users, subjects=subjects, user_performance_data=user_performance_data)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Admin Login
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin/admin_login.html')

# Admin Logout
@bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('You have logged out as Admin.', 'success')
    return redirect(url_for('admin.login'))

# Create a New Subject
@bp.route('/create_subject', methods=['GET', 'POST'])
def create_subject():
    if session.get('admin_logged_in'):
        if request.method == 'POST':
            subject_name = request.form['name']
            subject_description = request.form['description']

            new_subject = Subject(name=subject_name, description=subject_description)
            db.session.add(new_subject)
            db.session.commit()

            flash('Subject created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

        return render_template('admin/create_subject.html')
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Edit Subject
@bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if session.get('admin_logged_in'):
        subject = Subject.query.get_or_404(subject_id)
        if request.method == 'POST':
            subject.name = request.form['name']
            subject.description = request.form['description']

            db.session.commit()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

        return render_template('admin/edit_subject.html', subject=subject)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Delete Subject
@bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if session.get('admin_logged_in'):
        subject = Subject.query.get_or_404(subject_id)

        # Delete all chapters related to the subject
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        for chapter in chapters:
            # Delete all quizzes related to each chapter
            quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
            for quiz in quizzes:
                # Delete all questions related to each quiz
                questions = Question.query.filter_by(quiz_id=quiz.id).all()
                for question in questions:
                    db.session.delete(question)
                db.session.delete(quiz)
            db.session.delete(chapter)

        # Delete the subject itself
        db.session.delete(subject)
        db.session.commit()

        flash('Subject and all associated chapters, quizzes, and questions deleted successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Create a New Quiz
@bp.route('/create_quiz/<int:chapter_id>', methods=['GET', 'POST'])
def create_quiz(chapter_id):
    if session.get('admin_logged_in'):
        if request.method == 'POST':
            title = request.form['title']
            date = request.form['date']
            duration = request.form['duration']

            # Create a new Quiz instance
            quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                date=datetime.strptime(date, '%Y-%m-%d').date(),
                duration=int(duration)
            )
            db.session.add(quiz)
            db.session.commit()

            flash('Quiz created successfully! Redirecting to add questions.', 'success')
            return redirect(url_for('admin.add_questions', quiz_id=quiz.id))  # Redirect to add_questions

        return render_template('admin/create_quiz.html', chapter_id=chapter_id)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Add Questions to a Quiz
@bp.route('/add_questions/<int:quiz_id>', methods=['GET', 'POST'])
def add_questions(quiz_id):
    if session.get('admin_logged_in'):
        quiz = Quiz.query.get_or_404(quiz_id)

        if request.method == 'POST':
            question_text = request.form['question_text']
            option_1 = request.form['option_1']
            option_2 = request.form['option_2']
            option_3 = request.form['option_3']
            option_4 = request.form['option_4']
            correct_option = int(request.form['correct_option'])

            # Add the question to the database
            question = Question(
                quiz_id=quiz_id,
                question_text=question_text,
                option_1=option_1,
                option_2=option_2,
                option_3=option_3,
                option_4=option_4,
                correct_option=correct_option
            )
            db.session.add(question)
            db.session.commit()

            flash('Question added successfully!', 'success')
            return redirect(url_for('admin.add_questions', quiz_id=quiz_id))

        # Retrieve all questions for the quiz to show them
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return render_template('admin/add_questions.html', quiz=quiz, questions=questions)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Edit Question
@bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if session.get('admin_logged_in'):
        question = Question.query.get_or_404(question_id)
        if request.method == 'POST':
            question.question_text = request.form['question_text']
            question.option_1 = request.form['option_1']
            question.option_2 = request.form['option_2']
            question.option_3 = request.form['option_3']
            question.option_4 = request.form['option_4']
            question.correct_option = int(request.form['correct_option'])

            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin.manage_quiz_questions', quiz_id=question.quiz_id))

        return render_template('admin/edit_question.html', question=question)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Delete Question
@bp.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if session.get('admin_logged_in'):
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()

        flash('Question deleted successfully!', 'success')
        return redirect(url_for('admin.manage_quiz_questions', quiz_id=question.quiz_id))
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Manage Quiz Questions
@bp.route('/manage_quiz_questions/<int:quiz_id>', methods=['GET', 'POST'])
def manage_quiz_questions(quiz_id):
    if session.get('admin_logged_in'):
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        return render_template('admin/manage_quiz_questions.html', quiz=quiz, questions=questions)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Delete Quiz
@bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if session.get('admin_logged_in'):
        quiz = Quiz.query.get_or_404(quiz_id)

        # Delete all questions related to the quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        for question in questions:
            db.session.delete(question)

        # Delete the quiz itself
        db.session.delete(quiz)
        db.session.commit()

        flash('Quiz and all associated questions deleted successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# User Progress
@bp.route('/user_progress', methods=['GET'])
def user_progress():
    if session.get('admin_logged_in'):
        # Fetch user progress data with subject name
        progress_data = db.session.query(
            User.full_name,
            Subject.name.label('subject_name'),
            Quiz.title,
            UserQuizProgress.score,
            UserQuizProgress.completed_on
        ).join(UserQuizProgress, User.id == UserQuizProgress.user_id)\
         .join(Quiz, Quiz.id == UserQuizProgress.quiz_id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id).all()

        return render_template('admin/user_progress.html', progress_data=progress_data)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# User Progress Data for Charting
@bp.route('/user_progress_data', methods=['GET'])
def user_progress_data():
    if session.get('admin_logged_in'):
        # Fetch user progress data for chart
        progress_data = db.session.query(
            User.full_name,
            Subject.name.label('subject_name'),
            Quiz.title,
            UserQuizProgress.score,
            UserQuizProgress.completed_on
        ).join(UserQuizProgress, User.id == UserQuizProgress.user_id)\
         .join(Quiz, Quiz.id == UserQuizProgress.quiz_id)\
         .join(Chapter, Quiz.chapter_id == Chapter.id)\
         .join(Subject, Chapter.subject_id == Subject.id).all()

        # Prepare data for the chart
        data = {
            "users": [p[0] for p in progress_data],
            "subjects": [p[1] for p in progress_data],
            "quizzes": [p[2] for p in progress_data],
            "scores": [p[3] for p in progress_data],
            "completion_dates": [p[4].strftime('%Y-%m-%d') for p in progress_data]
        }

        return jsonify(data)
    else:
        return jsonify({"error": "Unauthorized access"}), 403

# User Performance Data for Charting
@bp.route('/user_performance_data', methods=['GET'])
def user_performance_data():
    if session.get('admin_logged_in'):
        # Fetch user performance data for the chart
        performance_data = db.session.query(
            User.full_name,
            db.func.avg(UserQuizProgress.score).label('average_score')
        ).join(UserQuizProgress, User.id == UserQuizProgress.user_id)\
         .group_by(User.full_name).all()

        # Prepare data for the chart
        data = {
            "users": [p[0] for p in performance_data],
            "average_scores": [p[1] for p in performance_data]
        }

        return jsonify(data)
    else:
        return jsonify({"error": "Unauthorized access"}), 403

# Create a New Chapter
@bp.route('/create_chapter/<int:subject_id>', methods=['GET', 'POST'])
def create_chapter(subject_id):
    if session.get('admin_logged_in'):
        if request.method == 'POST':
            chapter_name = request.form['name']
            chapter_description = request.form['description']

            new_chapter = Chapter(name=chapter_name, description=chapter_description, subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()

            flash('Chapter created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

        return render_template('admin/create_chapter.html', subject_id=subject_id)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Edit Chapter
@bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if session.get('admin_logged_in'):
        chapter = Chapter.query.get_or_404(chapter_id)
        if request.method == 'POST':
            chapter.name = request.form['name']
            chapter.description = request.form['description']

            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))

        return render_template('admin/edit_chapter.html', chapter=chapter)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# Delete Chapter
@bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if session.get('admin_logged_in'):
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()

        flash('Chapter deleted successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))

# View Chapters
@bp.route('/view_chapters/<int:subject_id>', methods=['GET'])
def view_chapters(subject_id):
    if session.get('admin_logged_in'):
        subject = Subject.query.get_or_404(subject_id)
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return render_template('admin/view_chapters.html', subject=subject, chapters=chapters)
    else:
        flash('Please log in as Admin to access this page.', 'error')
        return redirect(url_for('admin.login'))
