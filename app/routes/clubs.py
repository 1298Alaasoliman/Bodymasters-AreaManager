from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import os
from app import db
from app.models import Club
from app.models.facility_type import FacilityType, FacilityTypeItem, ClubFacilityTypeItem, club_facility_types
from app.models.issue import Issue
from app.forms.club import ClubForm
from app.utils.decorators import admin_required

bp = Blueprint('clubs', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض قائمة النوادي
    """
    if current_user.role == 'admin':
        clubs = Club.query.all()
    else:
        clubs = current_user.clubs

    # جلب أنواع المرافق النشطة لعرضها في الجدول
    facility_types = FacilityType.query.filter_by(is_active=True).order_by(FacilityType.order.asc(), FacilityType.name.asc()).all()

    return render_template('clubs/index.html', title='النوادي', clubs=clubs, facility_types=facility_types)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    إنشاء نادٍ جديد
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('clubs.index'))

    form = ClubForm()

    # تحميل أنواع المرافق المتاحة
    facility_types = FacilityType.query.filter_by(is_active=True).order_by(FacilityType.order.asc(), FacilityType.name.asc()).all()
    form.facility_types.choices = [(ft.id, ft.name) for ft in facility_types]

    if form.validate_on_submit():
        club = Club(
            name=form.name.data,
            location=form.location.data,
            manager_name=form.manager_name.data,
            employee_id=form.employee_id.data,
            email=form.email.data,
            # تم إزالة حقل تاريخ الافتتاح بناءً على طلب المستخدم
            is_active=form.is_active.data
            # تم إزالة الحقول المتعلقة بالمرافق المختلفة بناءً على طلب المستخدم
        )
        # إضافة أنواع المرافق المحددة
        if form.facility_types.data:
            for facility_type_id in form.facility_types.data:
                facility_type = FacilityType.query.get(facility_type_id)
                if facility_type:
                    club.facility_types.append(facility_type)

        db.session.add(club)
        db.session.commit()

        flash(f'تم إنشاء النادي {form.name.data} بنجاح!', 'success')
        return redirect(url_for('clubs.index'))

    return render_template('clubs/create.html', title='إنشاء نادٍ جديد', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    """
    عرض تفاصيل النادي
    """
    club = Club.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and club not in current_user.clubs:
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('clubs.index'))

    # استرجاع الموظفين المنتمين لهذا النادي بشكل مباشر من قاعدة البيانات
    from app.models.employee import Employee

    # التحقق من عدد الموظفين باستخدام استعلام مباشر
    direct_employees = Employee.query.filter_by(club_id=club.id).all()

    # استخدام جميع الموظفين المسترجعين
    employees = direct_employees

    # طباعة عدد الموظفين للتشخيص
    print(f"Number of employees for club {club.id} ({club.name}): {len(employees)}")

    # استرجاع الأعطال للنادي
    issues = Issue.query.filter_by(club_id=club.id).all()

    # جلب حالة بنود المرافق لهذا النادي
    for facility_type in club.facility_types:
        for item in facility_type.items:
            # التحقق من حالة البند لهذا النادي
            club_item = ClubFacilityTypeItem.query.filter_by(
                club_id=club.id,
                facility_type_item_id=item.id
            ).first()

            # إذا لم يكن هناك سجل، أنشئ واحداً بالحالة الافتراضية (نشط)
            if not club_item:
                club_item = ClubFacilityTypeItem(
                    club_id=club.id,
                    facility_type_item_id=item.id,
                    is_active=True
                )
                db.session.add(club_item)
                db.session.commit()

            # إضافة حالة البند إلى الكائن
            item.is_active = club_item.is_active

    # طباعة عدد الموظفين للتشخيص
    print(f"Number of employees for club {club.id} ({club.name}): {len(employees)}")

    return render_template('clubs/view.html', title=f'النادي: {club.name}', club=club, employees=employees, issues=issues)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    تعديل النادي
    """
    club = Club.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('clubs.index'))

    form = ClubForm(obj=club)

    # تحميل أنواع المرافق المتاحة
    facility_types = FacilityType.query.filter_by(is_active=True).order_by(FacilityType.order.asc(), FacilityType.name.asc()).all()
    form.facility_types.choices = [(ft.id, ft.name) for ft in facility_types]

    # تحديد أنواع المرافق الحالية
    if request.method == 'GET':
        form.facility_types.data = [ft.id for ft in club.facility_types]

    if form.validate_on_submit():
        # تحديث الحقول الأساسية
        club.name = form.name.data
        club.manager_name = form.manager_name.data
        club.employee_id = form.employee_id.data
        club.is_active = form.is_active.data

        # تعيين قيم افتراضية للحقول الغير موجودة في النموذج
        if not club.location:
            club.location = ''
        if not club.email:
            club.email = ''

        # طباعة البيانات للتشخيص
        print(f"Updating club: {club.name}")
        print(f"Manager: {club.manager_name}")
        print(f"Employee ID: {club.employee_id}")
        print(f"Active: {club.is_active}")

        # تم إزالة الحقول المتعلقة بالمرافق المختلفة بناءً على طلب المستخدم

        # تحديث أنواع المرافق
        print(f"Current facility types: {[ft.id for ft in club.facility_types]}")
        print(f"Selected facility types: {form.facility_types.data}")

        # إزالة جميع أنواع المرافق الحالية
        club.facility_types = []

        # إضافة أنواع المرافق المحددة
        if form.facility_types.data:
            for facility_type_id in form.facility_types.data:
                facility_type = FacilityType.query.get(facility_type_id)
                if facility_type:
                    club.facility_types.append(facility_type)

        db.session.commit()
        flash(f'تم تحديث النادي {club.name} بنجاح!', 'success')
        return redirect(url_for('clubs.view', id=club.id))

    return render_template('clubs/edit.html', title=f'تعديل النادي: {club.name}', form=form, club=club)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    حذف النادي
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('clubs.index'))

    club = Club.query.get_or_404(id)
    db.session.delete(club)
    db.session.commit()

    flash(f'تم حذف النادي {club.name} بنجاح!', 'success')
    return redirect(url_for('clubs.index'))


@bp.route('/delete_multiple', methods=['POST'])
@login_required
@admin_required
def delete_multiple():
    """
    حذف مجموعة من النوادي دفعة واحدة
    """
    if not request.json or 'club_ids' not in request.json:
        return jsonify({'success': False, 'message': 'البيانات غير صالحة'}), 400

    club_ids = request.json.get('club_ids', [])

    if not club_ids:
        return jsonify({'success': False, 'message': 'لم يتم تحديد أي نادي للحذف'}), 400

    deleted_count = 0
    deleted_names = []

    for club_id in club_ids:
        club = Club.query.get(club_id)
        if club:
            deleted_names.append(club.name)
            db.session.delete(club)
            deleted_count += 1

    if deleted_count > 0:
        db.session.commit()
        message = f'تم حذف {deleted_count} نادي بنجاح: {"، ".join(deleted_names)}'
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': 'لم يتم العثور على النوادي المحددة'}), 404


@bp.route('/update_facility_item_status', methods=['POST'])
@login_required
def update_facility_item_status():
    """
    تحديث حالة بند المرفق للنادي
    """
    # التحقق من أن الطلب يحتوي على بيانات JSON
    if not request.is_json:
        return jsonify({'success': False, 'message': 'الطلب غير صالح'}), 400

    data = request.json
    club_id = data.get('club_id')
    item_id = data.get('item_id')
    is_active = data.get('is_active')

    # التحقق من وجود جميع البيانات المطلوبة
    if not all([club_id, item_id, is_active is not None]):
        return jsonify({'success': False, 'message': 'البيانات غير مكتملة'}), 400

    # التحقق من وجود النادي والبند
    club = Club.query.get(club_id)
    item = FacilityTypeItem.query.get(item_id)

    if not club or not item:
        return jsonify({'success': False, 'message': 'النادي أو البند غير موجود'}), 404

    # التحقق من صلاحية المستخدم
    if current_user.role != 'admin' and club not in current_user.clubs:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية لتحديث هذا النادي'}), 403

    # البحث عن سجل الربط بين النادي والبند
    club_item = ClubFacilityTypeItem.query.filter_by(
        club_id=club_id,
        facility_type_item_id=item_id
    ).first()

    # إذا لم يكن هناك سجل، أنشئ واحداً
    if not club_item:
        club_item = ClubFacilityTypeItem(
            club_id=club_id,
            facility_type_item_id=item_id,
            is_active=is_active
        )
        db.session.add(club_item)
    else:
        # تحديث حالة البند
        club_item.is_active = is_active

    # حفظ التغييرات
    db.session.commit()

    return jsonify({'success': True, 'message': 'تم تحديث حالة البند بنجاح'})

@bp.route('/import-excel', methods=['POST', 'GET'])
@login_required
def import_excel():
    print("Import Excel function called")

    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('clubs.index'))

    # إذا كانت الطريقة GET، نقوم بعرض صفحة استيراد الإكسل
    if request.method == 'GET':
        return render_template('clubs/import_excel.html')

    # إذا كانت الطريقة POST، نقوم بمعالجة ملف الإكسل
    try:
        if 'file' not in request.files:
            flash('لم يتم تحميل أي ملف', 'danger')
            return redirect(url_for('clubs.index'))

        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار أي ملف', 'danger')
            return redirect(url_for('clubs.index'))

        if not file.filename.endswith(('.xls', '.xlsx')):
            flash('يجب أن يكون الملف بصيغة Excel (.xls أو .xlsx)', 'danger')
            return redirect(url_for('clubs.index'))

        # قراءة ملف إكسل
        import pandas as pd
        df = pd.read_excel(file)
        print(f"Excel file columns: {df.columns.tolist()}")
        print(f"Excel file data:\n{df.head()}")

        # التحقق من وجود الأعمدة المطلوبة
        # التعامل مع الأعمدة بشكل أكثر مرونة
        columns = df.columns.tolist()

        # البحث عن الأعمدة المطلوبة بشكل مرن
        club_name_col = None
        manager_name_col = None
        employee_id_col = None

        # طباعة أسماء الأعمدة للتشخيص
        print("Available columns:")
        for i, col in enumerate(columns):
            print(f"  {i+1}. '{col}'")

        # استخدام الأعمدة الثلاثة الأولى من الملف
        if len(columns) >= 3:
            club_name_col = columns[0]  # العمود الأول لاسم النادي
            manager_name_col = columns[1]  # العمود الثاني لاسم المدير
            employee_id_col = columns[2]  # العمود الثالث للرقم الوظيفي
        else:
            # إذا كان هناك أقل من 3 أعمدة، نحاول التعرف على الأعمدة بشكل مرن
            club_name_col = None
            manager_name_col = None
            employee_id_col = None

            for col in columns:
                col_lower = col.lower().strip()
                if 'اسم النادي' in col_lower or 'نادي' in col_lower:
                    club_name_col = col
                elif 'الاسم' in col_lower or 'اسم' in col_lower or 'مدير' in col_lower:
                    manager_name_col = col
                elif 'الرقم الوظيفي' in col_lower or 'رقم' in col_lower or 'وظيفي' in col_lower:
                    employee_id_col = col

        missing_columns = []
        if not club_name_col:
            missing_columns.append('اسم النادي')
        if not manager_name_col:
            missing_columns.append('الاسم')
        if not employee_id_col:
            missing_columns.append('الرقم الوظيفي')

        if missing_columns:
            flash(f'الأعمدة التالية غير موجودة في الملف: {", ".join(missing_columns)}', 'danger')
            return redirect(url_for('clubs.index'))

        print(f"Found columns: club_name={club_name_col}, manager_name={manager_name_col}, employee_id={employee_id_col}")

        # إضافة الأندية
        clubs_added = 0
        clubs_updated = 0
        errors = []

        for index, row in df.iterrows():
            try:
                club_name = row[club_name_col]
                manager_name = row[manager_name_col]
                employee_id = str(row[employee_id_col])

                # التحقق من وجود النادي
                existing_club = Club.query.filter_by(name=club_name).first()

                if existing_club:
                    # تحديث النادي الموجود
                    existing_club.manager_name = manager_name
                    existing_club.employee_id = employee_id
                    clubs_updated += 1
                else:
                    # إنشاء نادي جديد
                    new_club = Club(
                        name=club_name,
                        manager_name=manager_name,
                        employee_id=employee_id,
                        is_active=True
                    )
                    db.session.add(new_club)
                    clubs_added += 1
            except Exception as e:
                errors.append(f'خطأ في الصف {index + 1}: {str(e)}')

        db.session.commit()

        if errors:
            error_message = '\n'.join(errors[:5])
            if len(errors) > 5:
                error_message += f'\n... و{len(errors) - 5} أخطاء أخرى'
            flash(f'تمت العملية مع بعض الأخطاء:\n{error_message}', 'warning')
        else:
            flash(f'تمت إضافة {clubs_added} نادي وتحديث {clubs_updated} نادي بنجاح', 'success')

        return redirect(url_for('clubs.index'))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in import_excel: {str(e)}\n{error_details}")
        flash(f'حدث خطأ أثناء معالجة الملف: {str(e)}', 'danger')
        return redirect(url_for('clubs.index'))
