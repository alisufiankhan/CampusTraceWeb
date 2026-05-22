from flask import Blueprint, render_template, redirect, url_for
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
    
    return render_template('admin/dashboard.html', 
                           total_items=total_items,
                           pending_claims=pending_claims,
                           flagged_students=flagged_students,
                           total_students=total_students,
                           pending_reports=pending_reports)

@admin_routes.route('/reports')
def reports():
    report_obj = Report()
    report_data = report_obj.generate_report()
    return render_template('admin/reports.html', report=report_data)

@admin_routes.route('/flagged')
def flagged():
    flagged_students_list = Student.query.filter_by(is_flagged=True).all()
    return render_template('admin/dashboard.html', 
                           flagged_students_list=flagged_students_list,
                           total_items=0, pending_claims=0, 
                           flagged_students=len(flagged_students_list), 
                           total_students=Student.query.count())
