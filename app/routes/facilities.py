from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.facility import Facility, FacilityCategory, FacilityCheckItem, FacilityCheck, FacilityCheckResult
from app.models.facility_type import FacilityType, FacilityTypeItem, ClubFacilityTypeItem
from app.forms.facility import FacilityForm, FacilityCategoryForm, FacilityCheckItemForm, FacilityCheckResultForm, FacilityCheckForm
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta
import os
import traceback
from werkzeug.utils import secure_filename

bp = Blueprint('facilities', __name__)

# مسارات فئات المرافق
@bp.route('/categories')
@login_required
def categories():
    """
    عرض قائمة فئات المرافق
    """
    categories = FacilityCategory.query.order_by(FacilityCategory.order).all()
    return render_template('facilities/categories.html',
                           title='فئات المرافق',
                           categories=categories)

@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """
    إنشاء فئة مرافق جديدة
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.categories'))

    form = FacilityCategoryForm()

    if form.validate_on_submit():
        category = FacilityCategory(
            name=form.name.data,
            description=form.description.data,
            order=form.order.data,
            is_active=form.is_active.data
        )
        db.session.add(category)
        db.session.commit()
        flash('تم إنشاء الفئة بنجاح', 'success')
        return redirect(url_for('facilities.categories'))

    return render_template('facilities/category_form.html',
                           title='إنشاء فئة جديدة',
                           form=form)

@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """
    تعديل فئة مرافق
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.categories'))

    category = FacilityCategory.query.get_or_404(id)
    form = FacilityCategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.order = form.order.data
        category.is_active = form.is_active.data
        db.session.commit()
        flash('تم تحديث الفئة بنجاح', 'success')
        return redirect(url_for('facilities.categories'))

    return render_template('facilities/category_form.html',
                           title='تعديل الفئة',
                           form=form)

@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """
    حذف فئة مرافق
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.categories'))

    category = FacilityCategory.query.get_or_404(id)

    # التحقق من عدم وجود عناصر فحص مرتبطة بالفئة
    if category.check_items.count() > 0:
        flash('لا يمكن حذف الفئة لأنها تحتوي على عناصر فحص', 'danger')
        return redirect(url_for('facilities.categories'))

    db.session.delete(category)
    db.session.commit()
    flash('تم حذف الفئة بنجاح', 'success')
    return redirect(url_for('facilities.categories'))

# مسارات المرافق
@bp.route('/')
@login_required
def index():
    """
    عرض قائمة المرافق
    """
    # الحصول على معاملات التصفية
    club_id = request.args.get('club_id', type=int)
    status = request.args.get('status')
    search = request.args.get('search', '')

    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    # بناء استعلام المرافق
    query = Facility.query

    # تطبيق التصفية حسب النادي
    if current_user.role != 'admin':
        club_ids = [club.id for club in current_user.clubs]
        query = query.filter(Facility.club_id.in_(club_ids))

    if club_id:
        query = query.filter(Facility.club_id == club_id)

    # تطبيق التصفية حسب الحالة
    if status == 'active':
        query = query.filter(Facility.is_active == True)
    elif status == 'inactive':
        query = query.filter(Facility.is_active == False)

    # تطبيق البحث
    if search:
        query = query.filter(Facility.name.ilike(f'%{search}%'))

    # الحصول على النادي المحدد
    selected_club = None
    show_check_items = True
    if club_id:
        selected_club = Club.query.get(club_id)

        # التحقق من عدم وجود فحص لهذا النادي في نفس اليوم
        if selected_club:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())

            # البحث عن فحوصات اليوم لهذا النادي
            facilities = Facility.query.filter_by(club_id=club_id).all()
            facility_ids = [f.id for f in facilities]

            today_checks = FacilityCheck.query.filter(
                FacilityCheck.facility_id.in_(facility_ids),
                FacilityCheck.check_date >= today_start,
                FacilityCheck.check_date <= today_end
            ).first()

            if today_checks:
                # لا نعرض رسالة التحذير هنا لأنها ستظهر في القالب
                # flash('لا يمكن إجراء التشيك لهذا النادي أكثر من مرة واحدة في اليوم', 'warning')
                show_check_items = False

    # الحصول على أنواع المرافق وبنودها
    facility_types = []
    facility_type_items = {}

    if selected_club:
        # الحصول على أنواع المرافق المرتبطة بالنادي المحدد
        facility_types = selected_club.facility_types.filter_by(is_active=True).all()

        # إنشاء قاموس لبنود كل نوع مرفق
        for facility_type in facility_types:
            # الحصول على بنود المرفق النشطة
            items = FacilityTypeItem.query.filter_by(
                facility_type_id=facility_type.id,
                is_active=True
            ).order_by(FacilityTypeItem.order.asc()).all()

            # تصفية البنود المفعلة للنادي المحدد فقط
            from app.models.facility_type import ClubFacilityTypeItem
            filtered_items = []

            for item in items:
                # التحقق من حالة البند للنادي المحدد
                club_item = ClubFacilityTypeItem.query.filter_by(
                    club_id=selected_club.id,
                    facility_type_item_id=item.id
                ).first()

                # إضافة البند فقط إذا كان مفعلاً للنادي
                if club_item and club_item.is_active:
                    filtered_items.append(item)
                elif not club_item:  # إذا لم يكن هناك سجل، أضف البند افتراضياً
                    filtered_items.append(item)

            facility_type_items[facility_type.id] = filtered_items
    else:
        # إذا لم يتم تحديد نادي، فلا تعرض أي أنواع مرافق
        facility_types = []

    # الحصول على المرافق للعرض القديم
    facilities = []
    facilities_by_club = {}

    if selected_club:
        # الحصول على المرافق للنادي المحدد
        facilities = query.all()

        # تنظيم المرافق حسب النادي
        facilities_by_club = {selected_club: facilities}



    return render_template('facilities/index.html',
                           title='التشيك',
                           facilities=facilities,
                           facilities_by_club=facilities_by_club,
                           clubs=clubs,
                           facility_types=facility_types,
                           facility_type_items=facility_type_items,
                           categories=categories,
                           FacilityCheck=FacilityCheck,
                           show_check_items=show_check_items)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    إنشاء مرفق جديد
    """
    if current_user.role != 'admin' and not current_user.has_permission('facilities', 'can_create'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.index'))

    form = FacilityForm()

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    if form.validate_on_submit():
        facility = Facility(
            name=form.name.data,
            description=form.description.data,
            club_id=form.club_id.data,
            facility_type=form.facility_type.data,
            location=form.location.data,
            is_active=form.is_active.data
        )
        db.session.add(facility)
        db.session.commit()

        flash(f'تم إنشاء المرفق {form.name.data} بنجاح!', 'success')
        return redirect(url_for('facilities.index'))

    return render_template('facilities/create.html', title='إنشاء مرفق جديد', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    """
    عرض تفاصيل المرفق
    """
    facility = Facility.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    check_items = FacilityCheckItem.query.filter_by(facility_id=facility.id).all()
    recent_checks = FacilityCheck.query.filter_by(facility_id=facility.id).order_by(FacilityCheck.check_date.desc()).limit(10).all()

    return render_template('facilities/view.html',
                           title=f'المرفق: {facility.name}',
                           facility=facility,
                           check_items=check_items,
                           recent_checks=recent_checks,
                           FacilityCheck=FacilityCheck)

@bp.route('/club_check/<int:club_id>')
@login_required
def club_check(club_id):
    """
    عرض تفاصيل التشيك للنادي
    """
    club = Club.query.get_or_404(club_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(club.id):
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('facilities.index'))

    # الحصول على أنواع المرافق المرتبطة بالنادي
    facility_types = club.facility_types.filter_by(is_active=True).all()

    # إنشاء قاموس لبنود كل نوع مرفق
    facility_type_items = {}

    for facility_type in facility_types:
        # الحصول على بنود المرفق النشطة
        items = FacilityTypeItem.query.filter_by(
            facility_type_id=facility_type.id,
            is_active=True
        ).order_by(FacilityTypeItem.order.asc()).all()

        # تصفية البنود المفعلة للنادي المحدد فقط
        from app.models.facility_type import ClubFacilityTypeItem
        filtered_items = []

        for item in items:
            # التحقق من حالة البند للنادي المحدد
            club_item = ClubFacilityTypeItem.query.filter_by(
                club_id=club.id,
                facility_type_item_id=item.id
            ).first()

            # إضافة البند فقط إذا كان مفعلاً للنادي
            if club_item and club_item.is_active:
                filtered_items.append(item)
            elif not club_item:  # إذا لم يكن هناك سجل، أضف البند افتراضياً
                filtered_items.append(item)

        facility_type_items[facility_type.id] = filtered_items

    return render_template('facilities/club_check.html',
                           title=f'تشيك النادي: {club.name}',
                           club=club,
                           facility_types=facility_types,
                           facility_type_items=facility_type_items)

@bp.route('/facility_type_check/<int:facility_type_id>')
@login_required
def facility_type_check(facility_type_id):
    """
    عرض تفاصيل التشيك لنوع المرفق
    """
    facility_type = FacilityType.query.get_or_404(facility_type_id)

    # الحصول على بنود نوع المرفق
    items = FacilityTypeItem.query.filter_by(
        facility_type_id=facility_type.id,
        is_active=True
    ).order_by(FacilityTypeItem.order.asc()).all()

    # الحصول على النوادي المرتبطة بنوع المرفق
    clubs = facility_type.clubs.all()

    # تصفية النوادي التي يمكن للمستخدم الوصول إليها
    if current_user.role != 'admin':
        user_club_ids = [club.id for club in current_user.clubs]
        clubs = [club for club in clubs if club.id in user_club_ids]

    return render_template('facilities/facility_type_check.html',
                           title=f'تشيك نوع المرفق: {facility_type.name}',
                           facility_type=facility_type,
                           items=items,
                           clubs=clubs)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    تعديل المرفق
    """
    facility = Facility.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_permission('facilities', 'can_edit'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.index'))

    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    form = FacilityForm(obj=facility)

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    if form.validate_on_submit():
        facility.name = form.name.data
        facility.description = form.description.data
        facility.club_id = form.club_id.data
        facility.facility_type = form.facility_type.data
        facility.location = form.location.data
        facility.is_active = form.is_active.data

        db.session.commit()
        flash(f'تم تحديث المرفق {facility.name} بنجاح!', 'success')
        return redirect(url_for('facilities.view', id=facility.id))

    return render_template('facilities/edit.html', title=f'تعديل المرفق: {facility.name}', form=form, facility=facility)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    حذف المرفق
    """
    if current_user.role != 'admin' and not current_user.has_permission('facilities', 'can_delete'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('facilities.index'))

    facility = Facility.query.get_or_404(id)

    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    db.session.delete(facility)
    db.session.commit()

    flash(f'تم حذف المرفق {facility.name} بنجاح!', 'success')
    return redirect(url_for('facilities.index'))

@bp.route('/check_items/<int:facility_id>')
@login_required
def check_items(facility_id):
    """
    عرض قائمة عناصر الفحص للمرفق
    """
    facility = Facility.query.get_or_404(facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    check_items = FacilityCheckItem.query.filter_by(facility_id=facility_id).all()

    return render_template('facilities/check_items.html',
                           title=f'عناصر الفحص: {facility.name}',
                           facility=facility,
                           check_items=check_items)

@bp.route('/check_items/<int:facility_id>/create', methods=['GET', 'POST'])
@login_required
def create_check_item(facility_id):
    """
    إنشاء عنصر فحص جديد
    """
    facility = Facility.query.get_or_404(facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    form = FacilityCheckItemForm()

    # تعيين قيمة افتراضية لحقل الفئة (بدون فئة)
    form.category_id.choices = [(0, 'بدون فئة')]
    form.category_id.data = 0

    if form.validate_on_submit():
        check_item = FacilityCheckItem(
            name=form.name.data,
            # تم إزالة حقلي الوصف والترتيب بناءً على طلب المستخدم
            facility_id=facility_id,
            category_id=form.category_id.data if form.category_id.data > 0 else None,
            is_required=form.is_required.data,
            is_active=form.is_active.data
        )
        db.session.add(check_item)
        db.session.commit()

        flash(f'تم إنشاء عنصر الفحص {form.name.data} بنجاح!', 'success')
        return redirect(url_for('facilities.check_items', facility_id=facility_id))

    return render_template('facilities/create_check_item.html',
                           title=f'إنشاء عنصر فحص جديد: {facility.name}',
                           form=form,
                           facility=facility)

@bp.route('/import_check_items/<int:facility_id>', methods=['GET', 'POST'])
@login_required
def import_check_items(facility_id):
    """
    استيراد عناصر الفحص من ملف Excel
    """
    facility = Facility.query.get_or_404(facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        if file:
            try:
                # قراءة ملف Excel
                df = pd.read_excel(BytesIO(file.read()))

                # التحقق من وجود الأعمدة المطلوبة
                required_columns = ['name', 'description']
                for col in required_columns:
                    if col not in df.columns:
                        flash(f'العمود المطلوب "{col}" غير موجود في الملف', 'danger')
                        return redirect(request.url)

                # إضافة عناصر الفحص
                count = 0
                for _, row in df.iterrows():
                    # لم نعد نستخدم الفئات
                    category_id = None

                    # تحديد الترتيب إذا كان موجوداً
                    order = 0
                    if 'order' in df.columns and not pd.isna(row['order']):
                        try:
                            order = int(row['order'])
                        except:
                            pass

                    # تحديد ما إذا كان العنصر مطلوباً
                    is_required = True
                    if 'is_required' in df.columns and not pd.isna(row['is_required']):
                        is_required = str(row['is_required']).lower() in ['true', '1', 'yes', 'y', 'نعم']

                    check_item = FacilityCheckItem(
                        name=row['name'],
                        description=row['description'] if not pd.isna(row['description']) else None,
                        facility_id=facility_id,
                        category_id=category_id,
                        order=order,
                        is_required=is_required,
                        is_active=True
                    )
                    db.session.add(check_item)
                    count += 1

                db.session.commit()
                flash(f'تم استيراد {count} عنصر فحص بنجاح!', 'success')
                return redirect(url_for('facilities.check_items', facility_id=facility_id))

            except Exception as e:
                error_message = str(e)
                if 'openpyxl' in error_message:
                    error_message = 'يجب تثبيت مكتبة openpyxl لقراءة ملفات Excel. تم تثبيتها بالفعل، يرجى إعادة تشغيل التطبيق.'
                flash(f'حدث خطأ أثناء استيراد الملف: {error_message}', 'danger')
                return redirect(request.url)

    return render_template('facilities/import_check_items.html',
                           title=f'استيراد عناصر الفحص: {facility.name}',
                           facility=facility)

@bp.route('/perform_check/<int:facility_id>', methods=['GET', 'POST'])
@login_required
def perform_check(facility_id):
    """
    إجراء فحص للمرفق
    """
    facility = Facility.query.get_or_404(facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    # الحصول على عناصر الفحص النشطة
    check_items = FacilityCheckItem.query.filter_by(facility_id=facility_id, is_active=True).order_by(FacilityCheckItem.order).all()

    if not check_items:
        flash('لا توجد عناصر فحص نشطة لهذا المرفق', 'warning')
        return redirect(url_for('facilities.view', id=facility_id))

    # لم نعد نستخدم الفئات

    form = FacilityCheckForm()

    if form.validate_on_submit():
        # إنشاء فحص جديد
        facility_check = FacilityCheck(
            facility_id=facility_id,
            user_id=current_user.id,
            check_date=datetime.utcnow(),
            notes=form.notes.data,
            violations_count=0  # سيتم تحديثه لاحقاً
        )
        db.session.add(facility_check)
        db.session.flush()  # للحصول على معرف الفحص

        # إضافة نتائج الفحص لكل عنصر
        for item in check_items:
            status_value = request.form.get(f'status_{item.id}', 'not_checked')
            status_notes = request.form.get(f'status_notes_{item.id}', '')
            item_notes = request.form.get(f'notes_{item.id}', '')

            # دمج ملاحظات الحالة والملاحظات الإضافية إذا كانت موجودة
            combined_notes = ""
            if status_notes:
                combined_notes += f"ملاحظات الحالة: {status_notes}\n"
            if item_notes:
                combined_notes += f"ملاحظات إضافية: {item_notes}"

            item_value = ''  # لم نعد نستخدم حقل القيمة

            # معالجة الصورة إن وجدت
            image_path = None
            if f'image_{item.id}' in request.files:
                image_file = request.files[f'image_{item.id}']
                if image_file and image_file.filename != '':
                    # إنشاء مجلد للصور إن لم يكن موجوداً
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'checks')
                    os.makedirs(upload_folder, exist_ok=True)

                    # حفظ الصورة
                    filename = secure_filename(f"{facility_check.id}_{item.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    image_path = os.path.join('uploads', 'checks', filename)
                    image_file.save(os.path.join(current_app.static_folder, image_path))

            result = FacilityCheckResult(
                facility_check_id=facility_check.id,
                check_item_id=item.id,
                status=status_value or 'not_checked',
                value=item_value,
                notes=combined_notes,
                image_path=image_path
            )
            db.session.add(result)

        # حساب عدد المخالفات (العناصر التي حالتها failed)
        violations_count = 0
        for item in check_items:
            status_value = request.form.get(f'status_{item.id}', 'not_checked')
            if status_value == 'failed':
                violations_count += 1

        # تحديث عدد المخالفات في الفحص
        facility_check.violations_count = violations_count

        db.session.commit()
        flash('تم إجراء الفحص بنجاح!', 'success')
        return redirect(url_for('facilities.view', id=facility_id))

    return render_template('facilities/perform_check.html',
                           title=f'إجراء فحص: {facility.name}',
                           facility=facility,
                           check_items=check_items,
                           form=form)

@bp.route('/check_items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_check_item(item_id):
    """
    تعديل عنصر فحص
    """
    check_item = FacilityCheckItem.query.get_or_404(item_id)
    facility = Facility.query.get_or_404(check_item.facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    form = FacilityCheckItemForm(obj=check_item)

    # تعيين قيمة افتراضية لحقل الفئة (بدون فئة)
    form.category_id.choices = [(0, 'بدون فئة')]
    form.category_id.data = 0

    if form.validate_on_submit():
        check_item.name = form.name.data
        # تم إزالة حقلي الوصف والترتيب بناءً على طلب المستخدم
        check_item.category_id = form.category_id.data if form.category_id.data > 0 else None
        check_item.is_required = form.is_required.data
        check_item.is_active = form.is_active.data

        db.session.commit()
        flash(f'تم تحديث عنصر الفحص {check_item.name} بنجاح!', 'success')
        return redirect(url_for('facilities.view', id=facility.id))

    return render_template('facilities/create_check_item.html',
                           title=f'تعديل عنصر الفحص: {check_item.name}',
                           form=form,
                           facility=facility,
                           check_item=check_item)

@bp.route('/check_items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_check_item(item_id):
    """
    حذف عنصر فحص
    """
    check_item = FacilityCheckItem.query.get_or_404(item_id)
    facility = Facility.query.get_or_404(check_item.facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا المرفق', 'danger')
        return redirect(url_for('facilities.index'))

    # التحقق من عدم وجود نتائج فحص مرتبطة بالعنصر
    if check_item.check_results.count() > 0:
        flash('لا يمكن حذف عنصر الفحص لأنه مرتبط بنتائج فحص سابقة', 'danger')
        return redirect(url_for('facilities.view', id=facility.id))

    db.session.delete(check_item)
    db.session.commit()
    flash(f'تم حذف عنصر الفحص {check_item.name} بنجاح!', 'success')
    return redirect(url_for('facilities.view', id=facility.id))

@bp.route('/save_check/<int:club_id>', methods=['POST'])
@login_required
def save_check(club_id):
    """
    حفظ نتائج التشيك
    """
    try:
        # الحصول على النادي المحدد
        if not club_id:
            flash('لم يتم تحديد النادي', 'danger')
            return redirect(url_for('facilities.index'))

        club = Club.query.get_or_404(club_id)

        # التحقق من صلاحية الوصول
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('facilities.index'))

        # التحقق من عدم وجود فحص لهذا النادي في نفس اليوم
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # البحث عن فحوصات اليوم لهذا النادي
        facilities = Facility.query.filter_by(club_id=club_id).all()
        facility_ids = [f.id for f in facilities]

        today_checks = FacilityCheck.query.filter(
            FacilityCheck.facility_id.in_(facility_ids),
            FacilityCheck.check_date >= today_start,
            FacilityCheck.check_date <= today_end
        ).first()

        if today_checks:
            flash('لا يمكن إجراء التشيك لهذا النادي أكثر من مرة واحدة في اليوم', 'warning')
            return redirect(url_for('facilities.index'))

        # الحصول على مرفق النادي أو إنشاء واحد جديد إذا لم يكن موجوداً
        facility = Facility.query.filter_by(club_id=club_id, facility_type='general').first()
        if not facility:
            facility = Facility(
                name=f"{club.name} - مرفق عام",
                club_id=club_id,
                facility_type='general',
                is_active=True
            )
            db.session.add(facility)
            db.session.flush()

        # إنشاء فحص جديد
        check = FacilityCheck(
            facility_id=facility.id,
            check_date=datetime.now(),  # استخدام now بدلاً من utcnow
            user_id=current_user.id,
            notes=request.form.get('notes', ''),
            violations_count=0  # سيتم تحديثه لاحقاً
        )
        db.session.add(check)
        db.session.flush()  # للحصول على معرف الفحص

        # معالجة البيانات المرسلة من النموذج
        items_dict = {}
        for key, value in request.form.items():
            if key.startswith('items[') and key.endswith(']'):
                try:
                    item_id = key[6:-1]  # استخراج معرف البند
                    items_dict[item_id] = value
                except Exception as e:
                    current_app.logger.error(f"Error processing item {key}: {str(e)}")

        # الحصول على بنود المرافق المرتبطة بالنادي المحدد
        all_items = []
        for facility_type in club.facility_types.filter_by(is_active=True).all():
            items = FacilityTypeItem.query.filter_by(facility_type_id=facility_type.id, is_active=True).all()
            all_items.extend(items)

        # إضافة نتائج الفحص
        total_items = 0
        passed_items = 0

        for item in all_items:
            try:
                total_items += 1
                is_passed = str(item.id) in items_dict
                if is_passed:
                    passed_items += 1

                # الحصول على الملاحظات إن وجدت
                item_notes = request.form.get(f'notes_{item.id}', '')

                # معالجة الصورة إن وجدت
                image_path = None
                if f'image_{item.id}' in request.files:
                    image_file = request.files[f'image_{item.id}']
                    if image_file and image_file.filename != '':
                        # إنشاء مجلد للصور إن لم يكن موجوداً
                        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'checks')
                        os.makedirs(upload_folder, exist_ok=True)

                        # حفظ الصورة
                        filename = secure_filename(f"check_{check.id}_item_{item.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                        image_path = os.path.join('uploads', 'checks', filename)
                        image_file.save(os.path.join(current_app.static_folder, image_path))

                # إنشاء نتيجة الفحص
                result = FacilityCheckResult(
                    facility_check_id=check.id,
                    check_item_id=item.id,
                    status='passed' if is_passed else 'failed',
                    notes=item_notes,
                    image_path=image_path
                )
                db.session.add(result)
            except Exception as e:
                current_app.logger.error(f"Error processing check result for item {item.id}: {str(e)}")

        # تحديث عدد المخالفات في الفحص
        failed_count = total_items - passed_items
        check.violations_count = failed_count

        # حفظ التغييرات في قاعدة البيانات
        db.session.commit()

        flash('تم حفظ نتائج التشيك بنجاح!', 'success')
        return redirect(url_for('facilities.check_history'))

    except Exception as e:
        # التراجع عن التغييرات في حالة حدوث خطأ
        db.session.rollback()
        current_app.logger.error(f"Error saving check: {str(e)}")
        flash('حدث خطأ أثناء حفظ نتائج التشيك. الرجاء المحاولة مرة أخرى.', 'danger')
        return redirect(url_for('facilities.index', club_id=club_id))

@bp.route('/check_history')
@login_required
def check_history():
    """
    عرض سجل الفحوصات
    """
    # الحصول على الفترة الزمنية (افتراضيًا آخر 30 يوم)
    # إضافة يوم واحد للتأكد من تضمين اليوم الحالي
    end_date = datetime.now().date() + timedelta(days=1)
    start_date = end_date - timedelta(days=31)  # 30 يوم + يوم إضافي

    # الحصول على الفترة من الطلب إذا كانت موجودة
    if request.args.get('start_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            start_date = datetime.strptime(request.args.get('start_date'), '%d/%m/%Y').date()
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                pass

    if request.args.get('end_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            end_date_parsed = datetime.strptime(request.args.get('end_date'), '%d/%m/%Y').date()
            # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
            end_date = end_date_parsed + timedelta(days=1)
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                end_date_parsed = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
                # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
                end_date = end_date_parsed + timedelta(days=1)
            except ValueError:
                pass

    # الحصول على سجل الفحوصات للأندية التابعة للمستخدم
    recent_checks = []
    user_clubs = current_user.clubs if current_user.role != 'admin' else Club.query.all()

    for club in user_clubs:
        for facility in club.facilities:
            # تطبيق فلتر التاريخ
            checks = FacilityCheck.query.filter(
                FacilityCheck.facility_id == facility.id,
                FacilityCheck.check_date >= start_date,
                FacilityCheck.check_date <= end_date
            ).order_by(FacilityCheck.check_date.desc()).all()
            recent_checks.extend(checks)

    # ترتيب الفحوصات حسب التاريخ
    recent_checks.sort(key=lambda x: x.check_date, reverse=True)

    # تحديد ما إذا كانت التواريخ محددة من قبل المستخدم
    has_date_filter = 'start_date' in request.args or 'end_date' in request.args

    # إذا لم يتم تحديد التواريخ، نجعلها فارغة
    start_date_str = start_date.strftime('%d/%m/%Y') if has_date_filter else ''
    end_date_str = (end_date - timedelta(days=1)).strftime('%d/%m/%Y') if has_date_filter else ''

    return render_template('facilities/check_history.html',
                           title='سجل الفحوصات',
                           recent_checks=recent_checks,
                           start_date=start_date_str,
                           end_date=end_date_str)

@bp.route('/check_details/<int:check_id>')
@login_required
def check_details(check_id):
    """
    عرض تفاصيل الفحص
    """
    check = FacilityCheck.query.get_or_404(check_id)
    facility = Facility.query.get_or_404(check.facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الفحص', 'danger')
        return redirect(url_for('facilities.index'))

    # الحصول على نتائج الفحص
    results = FacilityCheckResult.query.filter_by(facility_check_id=check_id).all()

    # الحصول على بنود نوع المرفق لكل نتيجة
    items_dict = {}
    facility_types_dict = {}

    for result in results:
        # الحصول على بند الفحص
        item = FacilityTypeItem.query.get(result.check_item_id)
        if item:
            items_dict[result.check_item_id] = item

            # الحصول على نوع المرفق المرتبط بالبند
            facility_type = FacilityType.query.get(item.facility_type_id)
            if facility_type:
                if facility_type.id not in facility_types_dict:
                    facility_types_dict[facility_type.id] = {
                        'name': facility_type.name,
                        'results': []
                    }
                facility_types_dict[facility_type.id]['results'].append(result)

    # ترتيب النتائج حسب نوع المرفق
    grouped_results = []
    for facility_type_id, data in facility_types_dict.items():
        grouped_results.append({
            'facility_type_name': data['name'],
            'results': data['results']
        })

    # إضافة النتائج التي لا تنتمي إلى نوع مرفق محدد
    unassigned_results = []
    for result in results:
        if result.check_item_id in items_dict:
            item = items_dict[result.check_item_id]
            facility_type = FacilityType.query.get(item.facility_type_id)
            if not facility_type:
                unassigned_results.append(result)
        else:
            unassigned_results.append(result)

    if unassigned_results:
        grouped_results.append({
            'facility_type_name': 'بنود أخرى',
            'results': unassigned_results
        })

    return render_template('facilities/check_details.html',
                           title=f'تفاصيل الفحص: {facility.name}',
                           check=check,
                           facility=facility,
                           results=results,
                           items_dict=items_dict,
                           grouped_results=grouped_results)

@bp.route('/edit_check/<int:check_id>', methods=['GET', 'POST'])
@login_required
def edit_check(check_id):
    """
    تعديل نتائج الفحص
    """
    check = FacilityCheck.query.get_or_404(check_id)
    facility = Facility.query.get_or_404(check.facility_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الفحص', 'danger')
        return redirect(url_for('facilities.check_history'))

    # الحصول على نتائج الفحص
    results = FacilityCheckResult.query.filter_by(facility_check_id=check_id).all()

    # الحصول على بنود نوع المرفق لكل نتيجة
    items_dict = {}
    for item_id in [r.check_item_id for r in results]:
        item = FacilityTypeItem.query.get(item_id)
        if item:
            items_dict[item_id] = item

    return render_template('facilities/edit_check.html',
                           title=f'تعديل نتائج الفحص',
                           check=check,
                           facility=facility,
                           results=results,
                           items_dict=items_dict)

@bp.route('/update_check/<int:check_id>', methods=['POST'])
@login_required
def update_check(check_id):
    """
    تحديث نتائج الفحص
    """
    try:
        check = FacilityCheck.query.get_or_404(check_id)
        facility = Facility.query.get_or_404(check.facility_id)

        # التحقق من صلاحية الوصول
        if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا الفحص', 'danger')
            return redirect(url_for('facilities.check_history'))

        # الحصول على نتائج الفحص
        results = FacilityCheckResult.query.filter_by(facility_check_id=check_id).all()

        # تحديث كل نتيجة
        for result in results:
            # تحديث الحالة
            status_value = 'passed' if request.form.get(f'status_{result.id}') == 'passed' else 'failed'
            result.status = status_value

            # تحديث الملاحظات
            result.notes = request.form.get(f'notes_{result.id}', '')

            # تحديث الصورة إن وجدت
            if f'image_{result.id}' in request.files:
                image_file = request.files[f'image_{result.id}']
                if image_file and image_file.filename != '':
                    # إنشاء مجلد للصور إن لم يكن موجوداً
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'checks')
                    os.makedirs(upload_folder, exist_ok=True)

                    # حفظ الصورة
                    filename = secure_filename(f"check_{check.id}_item_{result.check_item_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    image_path = os.path.join('uploads', 'checks', filename)
                    image_file.save(os.path.join(current_app.static_folder, image_path))
                    result.image_path = image_path

        # تحديث تاريخ التعديل
        check.updated_at = datetime.now()

        # حفظ التغييرات
        db.session.commit()

        flash('تم تحديث نتائج الفحص بنجاح', 'success')
        return redirect(url_for('facilities.check_details', check_id=check_id))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating check: {str(e)}")
        flash('حدث خطأ أثناء تحديث نتائج الفحص. الرجاء المحاولة مرة أخرى.', 'danger')
        return redirect(url_for('facilities.check_history'))

@bp.route('/delete_check/<int:check_id>', methods=['POST'])
@login_required
def delete_check(check_id):
    """
    حذف الفحص ونتائجه
    """
    try:
        check = FacilityCheck.query.get_or_404(check_id)
        facility = Facility.query.get_or_404(check.facility_id)

        # التحقق من صلاحية الوصول
        if current_user.role != 'admin' and not current_user.has_club_access(facility.club_id):
            flash('ليس لديك صلاحية لحذف هذا الفحص', 'danger')
            return redirect(url_for('facilities.check_history'))

        # حذف نتائج الفحص أولاً
        FacilityCheckResult.query.filter_by(facility_check_id=check_id).delete()

        # حذف الفحص نفسه
        db.session.delete(check)
        db.session.commit()

        flash('تم حذف الفحص ونتائجه بنجاح', 'success')
        return redirect(url_for('facilities.check_history'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting check: {str(e)}")
        flash('حدث خطأ أثناء حذف الفحص. الرجاء المحاولة مرة أخرى.', 'danger')
        return redirect(url_for('facilities.check_history'))

