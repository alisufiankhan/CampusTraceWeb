from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.person import Person
from app.models.student import Student
from app import db

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
@auth.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_routes.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_routes.dashboard'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        role = request.form.get('role').lower()

        person = Person.query.filter_by(user_id=user_id, role=role).first()
        if not person:
            flash("Invalid ID or role", "error")
        elif not person.check_password(password):
            flash("Wrong password", "error")
        else:
            if role == "student" and not getattr(person, 'is_approved', True):
                flash("Your account is pending admin approval.", "warning")
            else:
                login_user(person)
                if role == "admin":
                    return redirect(url_for('admin_routes.dashboard'))
                if role == "student":
                    return redirect(url_for('student_routes.dashboard'))
                
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        dept = request.form.get('dept')
        password = request.form.get('password')
        
        # Check if user already exists
        existing = Person.query.filter_by(user_id=roll_number).first()
        if existing:
            flash("Registration number already exists.", "error")
        else:
            new_student = Student(
                name=name,
                user_id=roll_number,
                roll_number=roll_number,
                dept=dept,
                role="student",
                is_approved=False
            )
            new_student.set_password(password)
            db.session.add(new_student)
            db.session.commit()
            flash("Account created! Please wait for admin approval before logging in.", "success")
            return redirect(url_for('auth.login'))
            
    return render_template('auth/signup.html')
