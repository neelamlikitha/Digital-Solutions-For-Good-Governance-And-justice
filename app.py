# app.py (Main Flask Application)
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# MongoDB Connection
client = MongoClient(os.environ["MONGO_URI"])
db = client.governance_db

# User Model
class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({"username": user_id})
    if user:
        return User(user['username'], user.get('role', 'user'))
    return None

# Home Route
@app.route('/')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)

#about-route
@app.route('/about')
def about():
    return render_template('about.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = "user"
        db.users.insert_one({'username': username, 'password': password, 'role': role})
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            login_user(User(user['username'], user['role']))
            flash("Successfully logged in!", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid username or password.", "danger")
    
    return render_template('login.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# User Dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        flash("Access Denied!", "danger")
        return redirect(url_for('home'))
    return render_template('user_dashboard.html', username=current_user.id)

# Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access Denied!", "danger")
        return redirect(url_for('home'))
    complaints = db.complaints.find()
    return render_template('admin_dashboard.html', complaints=complaints)

# Submit Complaint
@app.route('/complaint', methods=['GET', 'POST'])
@login_required
def complaint_page():
    if request.method == 'POST':
        complaint_text = request.form['complaint']
        db.complaints.insert_one({'user': current_user.id, 'complaint': complaint_text})
        flash("Complaint submitted successfully!", "success")
    return render_template('complaints.html')

# Queries & Chatbot
@app.route('/queries')
def queries():
    return render_template('queries.html')

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        feedback_text = request.form['feedback']
        db.feedbacks.insert_one({'user': current_user.id, 'feedback': feedback_text})
        flash("Feedback submitted successfully!", "success")

    feedback_list = list(db.feedbacks.find())  # Fetch all feedbacks
    return render_template('feedback.html', feedback_list=feedback_list)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)