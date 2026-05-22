from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.claim import Claim
from app.models.handover import Handover
from app.models.item import Item
from app.models.student import Student
from app.models.admin import Admin

claims = Blueprint('claims', __name__)

@claims.route('/claims/submit', methods=['POST'])
@login_required
def submit():
    if current_user.role != 'student':
        flash("Student access required", "error")
        return redirect(url_for('auth.login'))
        
    item_id = request.form.get("item_id")
    proof = request.form.get("proof")
    
    item = Item.query.get(item_id)
    if not item:
        flash("Item not found", "error")
        return redirect(url_for('items.search'))
        
    if item.status != "Found":
        flash("This item is not available", "error")
        return redirect(url_for('items.search'))
        
    existing = Claim.query.filter_by(
        person_id=current_user.id,
        item_id=item.id
    ).filter(
        Claim.status != "Rejected"
    ).first()
    
    if existing:
        flash("You already claimed this", "error")
        return redirect(url_for('claims.student_my_claims'))
        
    new_claim = Claim(
        claim_id=Claim.generate_claim_id(),
        proof=proof,
        status="Pending",
        item_id=item.id,
        person_id=current_user.id
    )
    
    if not new_claim.validate_claim():
        flash("Please provide proof", "error")
        return redirect(url_for('items.search'))
        
    new_claim.submit_claim()
    item.update_status("UnderReview")
    db.session.add(new_claim)
    db.session.commit()
    
    flash("Claim submitted successfully", "success")
    return redirect(url_for('claims.student_my_claims'))

@claims.route('/student/my-claims')
@login_required
def student_my_claims():
    if current_user.role != 'student':
        flash("Student access required", "error")
        return redirect(url_for('auth.login'))
        
    user_claims = Claim.query.filter_by(person_id=current_user.id).order_by(Claim.date_submitted.desc()).all()
    return render_template('student/my_claims.html', claims=user_claims)

@claims.route('/admin/claims')
@login_required
def admin_claims():
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    pending = Claim.query.filter_by(status="Pending").order_by(Claim.date_submitted.desc()).all()
    all_claims = Claim.query.order_by(Claim.date_submitted.desc()).all()
    
    return render_template('admin/claims.html', pending=pending, all_claims=all_claims)

@claims.route('/admin/claims/approve/<claim_id>', methods=['POST'])
@login_required
def approve(claim_id):
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    claim = Claim.query.filter_by(claim_id=claim_id).first()
    if claim:
        admin = Admin.query.get(current_user.id)
        admin.approve_claim(claim)
        flash("Claim approved successfully", "success")
        
    return redirect(url_for('claims.admin_claims'))

@claims.route('/admin/claims/reject/<claim_id>', methods=['POST'])
@login_required
def reject(claim_id):
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    claim = Claim.query.filter_by(claim_id=claim_id).first()
    if claim:
        student = Student.query.get(claim.person_id)
        admin = Admin.query.get(current_user.id)
        admin.reject_claim(claim, student)
        
        if student.is_flagged:
            flash(f"{student.name} has been flagged (3 rejections)", "warning")
        else:
            flash("Claim rejected", "error")
            
    return redirect(url_for('claims.admin_claims'))

@claims.route('/admin/claims/dispute/<claim_id>', methods=['POST'])
@login_required
def dispute(claim_id):
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    claim = Claim.query.filter_by(claim_id=claim_id).first()
    if claim:
        claim.set_disputed()
        flash("Claim marked as disputed", "warning")
        
    return redirect(url_for('claims.admin_claims'))

@claims.route('/admin/handover/<claim_id>', methods=['GET', 'POST'])
@login_required
def handover(claim_id):
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    claim = Claim.query.filter_by(claim_id=claim_id).first()
    if not claim:
        flash("Claim not found", "error")
        return redirect(url_for('claims.admin_claims'))
        
    if claim.status != "Approved":
        flash("Claim must be approved first", "error")
        return redirect(url_for('claims.admin_claims'))
        
    if request.method == 'POST':
        witness = request.form.get("witness")
        condition = request.form.get("condition")
        
        admin = Admin.query.get(current_user.id)
        admin.process_handover(claim, witness, condition)
        
        flash("Handover completed successfully", "success")
        return redirect(url_for('claims.admin_claims'))
        
    return render_template('admin/handover.html', claim=claim)
