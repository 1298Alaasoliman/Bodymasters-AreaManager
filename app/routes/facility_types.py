from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.facility_type import FacilityType
from app.forms.facility import FacilityTypeForm
from sqlalchemy import desc
import pandas as pd
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# مزخرف مؤقت للتحقق من أن المستخدم هو مدير
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('facility_types.index'))
        return f(*args, **kwargs)
    return decorated_function

facility_types_bp = Blueprint('facility_types', __name__, url_prefix='/facility_types')

# تكوين مجلد التحميلات المؤقتة
def get_upload_folder():
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'temp')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

@facility_types_bp.route('/')
@login_required
def index():
    """
    عرض قائمة أنواع المرافق
    """
    page = request.args.get('page', 1, type=int)
    per_page = 100  # زيادة عدد العناصر في الصفحة الواحدة لعرض جميع المرافق في صفحة واحدة

    # البحث
    search = request.args.get('search', '')

    # الفلترة حسب الحالة
    status = request.args.get('status', '')

    query = FacilityType.query

    # تطبيق البحث
    if search:
        query = query.filter(FacilityType.name.ilike(f'%{search}%'))

    # تطبيق الفلترة حسب الحالة
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    # ترتيب النتائج
    query = query.order_by(FacilityType.name.asc())

    # تقسيم النتائج إلى صفحات
    facility_types = query.paginate(page=page, per_page=per_page)

    return render_template('facility_types/index.html',
                           facility_types=facility_types,
                           search=search,
                           status=status)

@facility_types_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """
    إنشاء نوع مرفق جديد
    """
    form = FacilityTypeForm()

    if form.validate_on_submit():
        facility_type = FacilityType(
            name=form.name.data,
            # تم إزالة حقول الوصف والأيقونة والترتيب بناءً على طلب المستخدم
            is_active=form.is_active.data
        )

        db.session.add(facility_type)
        db.session.commit()

        flash('تم إنشاء نوع المرفق بنجاح', 'success')
        return redirect(url_for('facility_types.index'))

    return render_template('facility_types/create.html', form=form)

@facility_types_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """
    تعديل نوع مرفق
    """
    facility_type = FacilityType.query.get_or_404(id)
    form = FacilityTypeForm(obj=facility_type)

    if form.validate_on_submit():
        facility_type.name = form.name.data
        # تم إزالة حقول الوصف والأيقونة والترتيب بناءً على طلب المستخدم
        facility_type.is_active = form.is_active.data

        db.session.commit()

        flash('تم تعديل نوع المرفق بنجاح', 'success')
        return redirect(url_for('facility_types.index'))

    return render_template('facility_types/edit.html', form=form, facility_type=facility_type)

@facility_types_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """
    حذف نوع مرفق
    """
    facility_type = FacilityType.query.get_or_404(id)

    # التحقق من عدم وجود مرافق مرتبطة بهذا النوع - تم تعطيل هذا التحقق مؤقتًا
    # if facility_type.facilities.count() > 0:
    #     flash('لا يمكن حذف نوع المرفق لأنه مرتبط بمرافق', 'danger')
    #     return redirect(url_for('facility_types.index'))

    # التحقق من عدم وجود نوادي مرتبطة بهذا النوع
    if facility_type.clubs.count() > 0:
        flash('لا يمكن حذف نوع المرفق لأنه مرتبط بنوادي', 'danger')
        return redirect(url_for('facility_types.index'))

    db.session.delete(facility_type)
    db.session.commit()

    flash('تم حذف نوع المرفق بنجاح', 'success')
    return redirect(url_for('facility_types.index'))

@facility_types_bp.route('/<int:id>/view')
@login_required
def view(id):
    """
    عرض تفاصيل نوع مرفق
    """
    facility_type = FacilityType.query.get_or_404(id)

    # استرجاع عدد بنود نوع المرفق
    items_count = facility_type.items.count()

    return render_template('facility_types/view.html', facility_type=facility_type, items_count=items_count)

@facility_types_bp.route('/api/list')
@login_required
def api_list():
    """
    الحصول على قائمة أنواع المرافق بتنسيق JSON
    """
    facility_types = FacilityType.query.filter_by(is_active=True).order_by(FacilityType.name.asc()).all()
    return jsonify([{'id': ft.id, 'name': ft.name} for ft in facility_types])

@facility_types_bp.route('/import-excel', methods=['GET', 'POST'])
@login_required
@admin_required
def import_excel():
    """
    استيراد أنواع المرافق من ملف إكسيل
    """
    if request.method == 'POST':
        # التحقق من وجود ملف
        if 'excel_file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        file = request.files['excel_file']

        # التحقق من اسم الملف
        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        # التحقق من امتداد الملف
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('يجب أن يكون الملف بصيغة Excel (.xlsx أو .xls)', 'danger')
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

            return render_template('facility_types/import_excel.html', preview_data=preview_data, file_path=file_path)

        except Exception as e:
            flash(f'حدث خطأ أثناء قراءة الملف: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('facility_types/import_excel.html')

@facility_types_bp.route('/import-excel-confirm', methods=['POST'])
@login_required
@admin_required
def import_excel_confirm():
    """
    تأكيد استيراد أنواع المرافق من ملف إكسيل
    """
    file_path = request.form.get('file_path')
    name_column = request.form.get('name_column')
    status_column = request.form.get('status_column')

    if not file_path or not name_column:
        flash('بيانات غير صحيحة', 'danger')
        return redirect(url_for('facility_types.import_excel'))

    try:
        # قراءة الملف
        df = pd.read_excel(file_path)

        # التحقق من وجود العمود المطلوب
        if name_column not in df.columns:
            flash(f'العمود {name_column} غير موجود في الملف', 'danger')
            return redirect(url_for('facility_types.import_excel'))

        # إضافة أنواع المرافق
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

                # التحقق من وجود نوع المرفق
                existing = FacilityType.query.filter_by(name=name).first()
                if existing:
                    skipped_count += 1
                    continue

                # تحديد الحالة
                is_active = True
                if status_column and status_column in df.columns:
                    status_value = row[status_column]
                    if not pd.isna(status_value):
                        if isinstance(status_value, str):
                            is_active = status_value.lower() in ['نشط', 'active', 'yes', 'نعم', 'true', '1']
                        elif isinstance(status_value, (int, float)):
                            is_active = bool(status_value)

                # إنشاء نوع المرفق
                facility_type = FacilityType(name=name, is_active=is_active)
                db.session.add(facility_type)
                added_count += 1

            except Exception as e:
                error_count += 1
                continue

        db.session.commit()

        # حذف الملف المؤقت
        if os.path.exists(file_path):
            os.remove(file_path)

        flash(f'تم استيراد {added_count} نوع مرفق بنجاح. تم تخطي {skipped_count} سجل موجود مسبقًا أو فارغ. حدثت {error_count} أخطاء.', 'success')
        return redirect(url_for('facility_types.index'))

    except Exception as e:
        flash(f'حدث خطأ أثناء استيراد البيانات: {str(e)}', 'danger')
        return redirect(url_for('facility_types.import_excel'))
