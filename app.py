from flask import Flask, redirect, url_for
from models import db
from controllers import admin_controller, user_controller, quiz_controller
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

# Define the user_loader callback
@login_manager.user_loader
def load_user(user_id):
    from models.user import User  # Import User model here to avoid circular import
    return User.query.get(int(user_id))  # Return the user object based on ID

# Initialize extensions
db.init_app(app)

# Import models after db initialization
with app.app_context():
    from models.user import User
    from models.subject import Subject
    from models.chapter import Chapter
    from models.quiz import Quiz, Question
    # Drop all tables and recreate them
    db.create_all()

# Register blueprints
app.register_blueprint(admin_controller.bp, url_prefix='/admin')
app.register_blueprint(user_controller.bp, url_prefix='/user')
app.register_blueprint(quiz_controller.bp, url_prefix='/quiz')

@app.route('/')
def index():
    return redirect(url_for('user.dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
