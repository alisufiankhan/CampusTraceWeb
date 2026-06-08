from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.report import Report

admin_routes = Blueprint('admin_routes', __name__, url_prefix='/admin')

@admin_routes.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

@admin_routes.route('/dashboard')
def dashboard():
    from app.models.claim import Claim
    from app.models.item import Item
    from app.models.student import Student
    
    total_items = Item.query.count()
    pending_claims = Claim.query.filter_by(status="Pending").count()
    flagged_students = Student.query.filter_by(is_flagged=True).count()
    total_students = Student.query.count()
    pending_reports = Item.query.filter_by(status="PendingVerification").count()
    pending_accounts_count = Student.query.filter_by(is_approved=False).count()
    
    return render_template('admin/dashboard.html', 
                           total_items=total_items,
                           pending_claims=pending_claims,
                           flagged_students=flagged_students,
                           total_students=total_students,
                           pending_reports=pending_reports,
                           pending_accounts_count=pending_accounts_count)

@admin_routes.route('/reports')
def reports():
    report_obj = Report()
    report_data = report_obj.generate_report()
    return render_template('admin/reports.html', report=report_data)

@admin_routes.route('/flagged')
def flagged():
    flagged_students_list = Student.query.filter_by(is_flagged=True).all()
    return render_template('admin/flagged.html', students=flagged_students_list)

@admin_routes.route('/pending_accounts')
def pending_accounts():
    students = Student.query.filter_by(is_approved=False).all()
    return render_template('admin/pending_accounts.html', students=students)

@admin_routes.route('/approve_account/<int:student_id>', methods=['POST'])
def approve_account(student_id):
    from app import db
    student = Student.query.get_or_404(student_id)
    student.is_approved = True
    db.session.commit()
    flash(f"Account for {student.name} approved.", "success")
    return redirect(url_for('admin_routes.pending_accounts'))

@admin_routes.route('/reject_account/<int:student_id>', methods=['POST'])
def reject_account(student_id):
    from app import db
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f"Account for {student.name} rejected and deleted.", "info")
    return redirect(url_for('admin_routes.pending_accounts'))

@admin_routes.route('/all_students')
def all_students():
    students = Student.query.filter_by(is_approved=True).all()
    return render_template('admin/all_students.html', students=students)

@admin_routes.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    from app import db
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {student.name} has been deleted.", "info")
    return redirect(url_for('admin_routes.all_students'))

@admin_routes.route('/toggle_flag/<int:student_id>', methods=['POST'])
def toggle_flag(student_id):
    from app import db
    student = Student.query.get_or_404(student_id)
    student.is_flagged = not student.is_flagged
    db.session.commit()
    status = "flagged" if student.is_flagged else "unflagged"
    flash(f"Student {student.name} has been {status}.", "success")
    return redirect(url_for('admin_routes.all_students'))
