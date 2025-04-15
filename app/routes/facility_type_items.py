from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.facility_type import FacilityType, FacilityTypeItem
from app.forms.facility import FacilityTypeItemForm, FacilityTypeItemImportForm
from app.utils.decorators import admin_required
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime

facility_type_items_bp = Blueprint('facility_type_items', __name__, url_prefix='/facility-type-items')

# تكوين مجلد التحميلات المؤقتة
def get_upload_folder():
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'temp')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

@facility_type_items_bp.route('/<int:facility_type_id>')
@login_required
def index(facility_type_id):
    """
    عرض قائمة بنود نوع المرفق
    """
    facility_type = FacilityType.query.get_or_404(facility_type_id)
    items = FacilityTypeItem.query.filter_by(facility_type_id=facility_type_id).order_by(FacilityTypeItem.order.asc()).all()
    
    return render_template(
        'facility_type_items/index.html',
        title=f'بنود نوع المرفق: {facility_type.name}',
        facility_type=facility_type,
        items=items
    )

@facility_type_items_bp.route('/create/<int:facility_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create(facility_type_id):
    """
    إنشاء بند جديد لنوع المرفق
    """
    facility_type = FacilityType.query.get_or_404(facility_type_id)
    form = FacilityTypeItemForm()
    
    if form.validate_on_submit():
        # تحديد الترتيب التلقائي
        max_order = db.session.query(db.func.max(FacilityTypeItem.order)).filter_by(facility_type_id=facility_type_id).scalar() or 0
        
        item = FacilityTypeItem(
            name=form.name.data,
            description=form.description.data,
            facility_type_id=facility_type_id,
            order=max_order + 1,
            is_required=form.is_required.data,
            is_active=form.is_active.data
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('تم إضافة البند بنجاح', 'success')
        return redirect(url_for('facility_type_items.index', facility_type_id=facility_type_id))
    
    return render_template(
        'facility_type_items/create.html',
        title=f'إضافة بند جديد لنوع المرفق: {facility_type.name}',
        form=form,
        facility_type=facility_type
    )

@facility_type_items_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """
    تعديل بند نوع المرفق
    """
    item = FacilityTypeItem.query.get_or_404(id)
    facility_type = FacilityType.query.get_or_404(item.facility_type_id)
    form = FacilityTypeItemForm()
    
    if request.method == 'GET':
        form.name.data = item.name
        form.description.data = item.description
        form.is_required.data = item.is_required
        form.is_active.data = item.is_active
    
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.is_required = form.is_required.data
        item.is_active = form.is_active.data
        item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('تم تعديل البند بنجاح', 'success')
        return redirect(url_for('facility_type_items.index', facility_type_id=item.facility_type_id))
    
    return render_template(
        'facility_type_items/edit.html',
        title=f'تعديل البند: {item.name}',
        form=form,
        item=item,
        facility_type=facility_type
    )

@facility_type_items_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """
    حذف بند نوع المرفق
    """
    item = FacilityTypeItem.query.get_or_404(id)
    facility_type_id = item.facility_type_id
    
    db.session.delete(item)
    db.session.commit()
    
    flash('تم حذف البند بنجاح', 'success')
    return redirect(url_for('facility_type_items.index', facility_type_id=facility_type_id))

@facility_type_items_bp.route('/import/<int:facility_type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def import_excel(facility_type_id):
    """
    استيراد بنود نوع المرفق من ملف إكسيل
    """
    facility_type = FacilityType.query.get_or_404(facility_type_id)
    form = FacilityTypeItemImportForm()
    
    if form.validate_on_submit():
        # التحقق من وجود ملف
        if 'excel_file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['excel_file']
        
        # التحقق من اسم الملف
        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)
        
        try:
            # حفظ الملف مؤقتًا
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(get_upload_folder(), filename)
            file.save(file_path)
            
            # قراءة الملف
            df = pd.read_excel(file_path)
            
            # التحقق من وجود بيانات
            if df.empty:
                flash('الملف لا يحتوي على بيانات', 'danger')
                os.remove(file_path)  # حذف الملف المؤقت
                return redirect(request.url)
            
            # إعداد بيانات المعاينة
            preview_data = {
                'columns': df.columns.tolist(),
                'data': df.head(5).values.tolist(),
                'total_rows': len(df)
            }
            
            return render_template(
                'facility_type_items/import_preview.html',
                title=f'استيراد بنود نوع المرفق: {facility_type.name}',
                preview_data=preview_data,
                file_path=file_path,
                facility_type=facility_type
            )
            
        except Exception as e:
            flash(f'حدث خطأ أثناء قراءة الملف: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template(
        'facility_type_items/import.html',
        title=f'استيراد بنود نوع المرفق: {facility_type.name}',
        form=form,
        facility_type=facility_type
    )

@facility_type_items_bp.route('/import-confirm/<int:facility_type_id>', methods=['POST'])
@login_required
@admin_required
def import_confirm(facility_type_id):
    """
    تأكيد استيراد بنود نوع المرفق من ملف إكسيل
    """
    facility_type = FacilityType.query.get_or_404(facility_type_id)
    file_path = request.form.get('file_path')
    name_column = request.form.get('name_column')
    description_column = request.form.get('description_column', None)
    required_column = request.form.get('required_column', None)
    
    if not file_path or not name_column:
        flash('بيانات غير صحيحة', 'danger')
        return redirect(url_for('facility_type_items.import_excel', facility_type_id=facility_type_id))
    
    try:
        # قراءة الملف
        df = pd.read_excel(file_path)
        
        # التحقق من وجود العمود المطلوب
        if name_column not in df.columns:
            flash(f'العمود {name_column} غير موجود في الملف', 'danger')
            return redirect(url_for('facility_type_items.import_excel', facility_type_id=facility_type_id))
        
        # تحديد الترتيب التلقائي
        max_order = db.session.query(db.func.max(FacilityTypeItem.order)).filter_by(facility_type_id=facility_type_id).scalar() or 0
        current_order = max_order + 1
        
        # إضافة بنود نوع المرفق
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                name = row[name_column]
                
                # تخطي الصفوف الفارغة
                if pd.isna(name) or name == '':
                    skipped_count += 1
                    continue
                
                # التحقق من وجود البند
                existing = FacilityTypeItem.query.filter_by(facility_type_id=facility_type_id, name=name).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # تحديد الوصف
                description = None
                if description_column and description_column in df.columns:
                    description_value = row[description_column]
                    if not pd.isna(description_value):
                        description = str(description_value)
                
                # تحديد ما إذا كان البند مطلوبًا
                is_required = True
                if required_column and required_column in df.columns:
                    required_value = row[required_column]
                    if not pd.isna(required_value):
                        if isinstance(required_value, str):
                            is_required = required_value.lower() in ['نعم', 'مطلوب', 'yes', 'required', 'true', '1']
                        elif isinstance(required_value, (int, float)):
                            is_required = bool(required_value)
                
                # إنشاء البند
                item = FacilityTypeItem(
                    name=name,
                    description=description,
                    facility_type_id=facility_type_id,
                    order=current_order,
                    is_required=is_required,
                    is_active=True
                )
                
                db.session.add(item)
                current_order += 1
                added_count += 1
                
            except Exception as e:
                error_count += 1
                continue
        
        db.session.commit()
        
        # حذف الملف المؤقت
        if os.path.exists(file_path):
            os.remove(file_path)
        
        flash(f'تم استيراد {added_count} بند بنجاح. تم تخطي {skipped_count} سجل موجود مسبقًا أو فارغ. حدثت {error_count} أخطاء.', 'success')
        return redirect(url_for('facility_type_items.index', facility_type_id=facility_type_id))
        
    except Exception as e:
        flash(f'حدث خطأ أثناء استيراد البيانات: {str(e)}', 'danger')
        return redirect(url_for('facility_type_items.import_excel', facility_type_id=facility_type_id))

@facility_type_items_bp.route('/api/list/<int:facility_type_id>')
@login_required
def api_list(facility_type_id):
    """
    الحصول على قائمة بنود نوع المرفق بتنسيق JSON
    """
    items = FacilityTypeItem.query.filter_by(facility_type_id=facility_type_id, is_active=True).order_by(FacilityTypeItem.order.asc()).all()
    return jsonify([{'id': item.id, 'name': item.name, 'is_required': item.is_required} for item in items])
