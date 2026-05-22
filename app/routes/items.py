from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.item import Item, ElectronicItem, DocumentItem, PersonalItem
import uuid

items = Blueprint('items', __name__, url_prefix='/items')

@items.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        desc = request.form.get("desc")
        location = request.form.get("location")
        date_found = request.form.get("date_found")
        category = request.form.get("category")
        
        item_id = Item.generate_item_id()
        item = None
        
        if category == "electronic":
            brand = request.form.get("brand")
            color = request.form.get("color")
            serial = request.form.get("serial_number")
            item = ElectronicItem(
                item_id=item_id,
                desc=desc,
                date_found=date_found,
                location=location,
                status="Found",
                item_type="electronic",
                brand=brand,
                color=color,
                serial_number=serial
            )
        elif category == "document":
            doc_type = request.form.get("doc_type")
            issued_by = request.form.get("issued_by")
            item = DocumentItem(
                item_id=item_id,
                desc=desc,
                date_found=date_found,
                location=location,
                status="Found",
                item_type="document",
                doc_type=doc_type,
                issued_by=issued_by
            )
        elif category == "personal":
            item_color = request.form.get("item_color")
            size = request.form.get("size")
            material = request.form.get("material")
            item = PersonalItem(
                item_id=item_id,
                desc=desc,
                date_found=date_found,
                location=location,
                status="Found",
                item_type="personal",
                item_color=item_color,
                size=size,
                material=material
            )
            
        if item:
            db.session.add(item)
            db.session.commit()
            flash("Item registered successfully", "success")
            return redirect(url_for('items.all_items'))

    all_items_list = Item.query.order_by(Item.id.desc()).all()
    return render_template('admin/items.html', items=all_items_list)

@items.route('/all')
@login_required
def all_items():
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    all_items_list = Item.query.order_by(Item.id.desc()).all()
    for item in all_items_list:
        if item.is_expired() and item.status == "Found":
            item.update_status("Expired")
            
    return render_template('admin/items.html', items=all_items_list)

@items.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    keyword = ""
    
    if request.method == 'POST':
        keyword = request.form.get("keyword", "").lower().strip()
        all_items_list = Item.query.filter(Item.status.not_in(["Returned", "Expired"])).all()
        
        results = [item for item in all_items_list if keyword in item.desc.lower() or (item.location and keyword in item.location.lower())]
        
        from app.models.searchlog import SearchLog
        log = SearchLog(
            log_id=str(uuid.uuid4())[:8],
            keyword=keyword,
            student_id=current_user.user_id
        )
        log.log_search()
        
    return render_template('student/search.html', results=results, keyword=keyword)

@items.route('/expire/<item_id>', methods=['POST'])
@login_required
def expire(item_id):
    if current_user.role != 'admin':
        flash("Admin access required", "error")
        return redirect(url_for('auth.login'))
        
    item = Item.query.filter_by(item_id=item_id).first()
    if item:
        item.update_status("Expired")
        flash("Item marked as expired", "success")
        
    return redirect(url_for('items.all_items'))
