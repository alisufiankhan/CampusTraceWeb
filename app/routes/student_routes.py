from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

student_routes = Blueprint('student_routes', __name__, url_prefix='/student')

@student_routes.before_request
@login_required
def require_student():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))

@student_routes.route('/dashboard')
def dashboard():
    student = current_user
    claims_count = 0
    return render_template('student/dashboard.html', student=student, claims_count=claims_count)
