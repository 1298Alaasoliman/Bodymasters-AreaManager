from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
# from flask_wtf.csrf import CSRFProtect, csrf_exempt
from app import db
from app.models.violation import ViolationType, ViolationSource, Violation
from app.models.employee import Employee
from app.models.club import Club
from app.forms.violation import ViolationTypeForm, ViolationSourceForm, ViolationForm, ImportViolationTypesForm, ImportViolationSourcesForm
from app.utils.decorators import admin_required
from app.utils.excel import import_from_excel
from datetime import datetime
import pandas as pd

violations_bp = Blueprint('violations', __name__, url_prefix='/violations')

# صفحة قائمة المخالفات
@violations_bp.route('/')
@login_required
def index():
    # جلب المخالفات من قاعدة البيانات بناءً على صلاحيات المستخدم
    try:
        # إذا كان المستخدم مسؤولاً، اعرض جميع المخالفات
        if current_user.role == 'admin':
            violations = Violation.query.order_by(Violation.violation_date.desc()).all()
            print(f"Admin user - Found {len(violations)} violations")
        else:
            # الحصول على قائمة الأندية المتاحة للمستخدم
            user_clubs = [club.id for club in current_user.clubs]
            print(f"User clubs: {user_clubs}")

            # الحصول على قائمة الموظفين التابعين لهذه الأندية
            employees = Employee.query.filter(Employee.club_id.in_(user_clubs)).all()
            employee_ids = [emp.id for emp in employees]
            print(f"Employees in user clubs: {employee_ids}")

            # الحصول على المخالفات الخاصة بهؤلاء الموظفين فقط
            violations = Violation.query.filter(Violation.employee_id.in_(employee_ids)).order_by(Violation.violation_date.desc()).all()
            print(f"User with restricted access - Found {len(violations)} violations")

        # جلب جميع مصادر المخالفات
        sources = ViolationSource.query.all()
    except Exception as e:
        print(f"Error fetching violations: {str(e)}")
        flash(f'حدث خطأ أثناء جلب المخالفات: {str(e)}', 'error')
        violations = []
        sources = []
    return render_template('violations/index.html', violations=violations, sources=sources)

# التأكد من وجود مصادر المخالفات في قاعدة البيانات
def ensure_violation_sources_exist():
    # قائمة مصادر المخالفات
    sources = [
        'مدير الأندية',
        'مدبر المنطقه',
        'مدير النادي',
        'مراقب الكاميرات'
    ]

    # التحقق من وجود كل مصدر وإضافته إذا لم يكن موجوداً
    for source_name in sources:
        source = ViolationSource.query.filter_by(name=source_name).first()
        if not source:
            source = ViolationSource(name=source_name)
            db.session.add(source)

    # حفظ التغييرات في قاعدة البيانات
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"خطأ في إنشاء مصادر المخالفات: {str(e)}")

# صفحة إنشاء مخالفة جديدة
@violations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # التأكد من وجود مصادر المخالفات
    ensure_violation_sources_exist()

    form = ViolationForm()

    # تعبئة قائمة النوادي للتحقق من صحة النموذج
    if current_user.role == 'admin':
        # إذا كان المستخدم مسؤولاً، اعرض جميع النوادي النشطة
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        # إذا كان المستخدم عادياً، اعرض فقط النوادي المتاحة له
        # الحصول على قائمة معرفات النوادي المتاحة للمستخدم
        user_club_ids = [club.id for club in current_user.clubs]
        # الحصول على النوادي النشطة من قائمة النوادي المتاحة
        clubs = Club.query.filter(Club.id.in_(user_club_ids), Club.is_active == True).all()

    form.club_id.choices = [(club.id, club.name) for club in clubs]
    if not form.club_id.choices:
        form.club_id.choices = [(1, 'نادي 1')]

    # تعبئة قائمة أنواع المخالفات
    violation_types = ViolationType.query.all()
    form.violation_type_id.choices = [('', 'اختر--')] + [(vt.id, vt.name) for vt in violation_types]
    if not form.violation_type_id.choices or len(form.violation_type_id.choices) == 1:
        form.violation_type_id.choices = [('', 'اختر--'), (1, 'نوع مخالفة 1')]

    print(f"Form submitted: {request.method == 'POST'}")
    print(f"Form validation: {form.validate()}")
    if request.method == 'POST':
        # الحصول على رقم النادي من الموظف
        employee = Employee.query.filter_by(employee_number=form.employee_id.data).first()
        if employee and employee.club_id:
            form.club_id.data = employee.club_id

        # إنشاء مخالفة جديدة وحفظها في قاعدة البيانات
        try:
            # التحقق من وجود الموظف
            if not employee:
                flash('لم يتم العثور على الموظف', 'error')
                return render_template('violations/create.html', form=form)

            # الحصول على مصدر المخالفة من قاعدة البيانات
            source_name = dict(form.source.choices).get(form.source.data)
            violation_source = ViolationSource.query.filter_by(name=source_name).first()

            if not violation_source:
                # إذا لم يتم العثور على المصدر، قم بإنشائه
                violation_source = ViolationSource(name=source_name)
                db.session.add(violation_source)
                db.session.flush()  # للحصول على المعرف قبل الحفظ

            # إنشاء مخالفة جديدة
            violation = Violation(
                employee_id=employee.id,
                club_id=employee.club_id,
                violation_type_id=form.violation_type_id.data,
                violation_source_id=violation_source.id,  # استخدام معرف مصدر المخالفة
                violation_date=form.violation_date.data,
                violation_number=int(form.violation_number.data),  # تحويل النص إلى رقم
                notes=form.notes.data,  # الملاحظات فقط بدون إضافة مصدر المخالفة
                employee_signature=form.employee_signature.data,
                created_by=current_user.id
            )

            # حفظ المخالفة في قاعدة البيانات
            db.session.add(violation)
            db.session.commit()

            flash('تم حفظ المخالفة بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء حفظ المخالفة: {str(e)}', 'error')
        return redirect(url_for('violations.index'))

    return render_template('violations/create.html', form=form)

# الحصول على بيانات الموظف بناءً على الرقم الوظيفي
@violations_bp.route('/get_employee_data', methods=['GET'])
@login_required
def get_employee_data():
    employee_id = request.args.get('employee_id')
    employee = Employee.query.filter_by(employee_number=employee_id).first()

    if employee:
        # التحقق من صلاحية المستخدم للوصول إلى هذا الموظف
        if current_user.role != 'admin':
            # الحصول على قائمة الأندية المتاحة للمستخدم
            user_clubs = [club.id for club in current_user.clubs]

            # التحقق من أن الموظف ينتمي إلى أحد الأندية المتاحة للمستخدم
            if employee.club_id not in user_clubs:
                return jsonify({
                    'success': False,
                    'message': 'ليس لديك صلاحية للوصول إلى هذا الموظف'
                })
        # الحصول على اسم النادي التابع له الموظف
        club_name = ""
        if employee.club_id:
            club = Club.query.get(employee.club_id)
            if club:
                club_name = club.name

        # حساب عدد المخالفات السابقة للموظف في نفس الشهر
        from datetime import datetime
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        # البحث عن المخالفات السابقة للموظف في نفس الشهر
        from sqlalchemy import extract
        violations_count = Violation.query.filter(
            Violation.employee_id == employee.id,
            extract('month', Violation.violation_date) == current_month,
            extract('year', Violation.violation_date) == current_year
        ).count()

        # رقم المخالفة الجديدة هو عدد المخالفات السابقة + 1
        violation_number = violations_count + 1

        # تحويل رقم المخالفة إلى نص إنجليزي
        violation_number_str = str(violation_number)

        return jsonify({
            'success': True,
            'employee_name': employee.name,
            'job_role': employee.role,
            'employee_club': club_name,
            'violation_number': violation_number_str
        })

    return jsonify({
        'success': False,
        'message': 'الموظف غير موجود'
    })

# صفحة تفاصيل المخالفة
@violations_bp.route('/<int:id>')
@login_required
def details(id):
    # الحصول على المخالفة من قاعدة البيانات
    violation = Violation.query.get_or_404(id)

    # التحقق من صلاحية المستخدم للوصول إلى هذه المخالفة
    if current_user.role != 'admin':
        # الحصول على قائمة الأندية المتاحة للمستخدم
        user_clubs = [club.id for club in current_user.clubs]

        # التحقق من أن الموظف ينتمي إلى أحد الأندية المتاحة للمستخدم
        employee = Employee.query.get(violation.employee_id)
        if employee and employee.club_id not in user_clubs:
            flash('ليس لديك صلاحية للوصول إلى هذه المخالفة', 'danger')
            return redirect(url_for('violations.index'))

    # الحصول على مصدر المخالفة
    violation_source = None
    if violation.violation_source_id:
        violation_source = ViolationSource.query.get(violation.violation_source_id)

    return render_template('violations/details.html',
                           title=f'تفاصيل المخالفة #{violation.violation_number}',
                           violation=violation,
                           violation_source=violation_source)

# تعديل المخالفة
@violations_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # الحصول على المخالفة من قاعدة البيانات
    violation = Violation.query.get_or_404(id)

    # التحقق من صلاحية المستخدم
    if violation.created_by != current_user.id and current_user.role != 'admin':
        flash('ليس لديك صلاحية لتعديل هذه المخالفة', 'error')
        return redirect(url_for('violations.index'))

    # إنشاء نموذج التعديل
    form = ViolationForm()

    # تعبئة قائمة أنواع المخالفات
    violation_types = ViolationType.query.all()
    form.violation_type_id.choices = [('', 'اختر--')] + [(vt.id, vt.name) for vt in violation_types]

    if request.method == 'GET':
        # تعبئة النموذج ببيانات المخالفة الحالية
        form.employee_id.data = violation.employee_rel.employee_number
        form.employee_name.data = violation.employee_rel.name
        form.job_role.data = violation.employee_rel.role
        form.employee_club.data = violation.club_rel.name
        form.violation_type_id.data = violation.violation_type_id
        form.violation_number.data = str(violation.violation_number)
        form.violation_date.data = violation.violation_date
        form.notes.data = violation.notes
        form.employee_signature.data = violation.employee_signature

        # الحصول على مصدر المخالفة
        if violation.violation_source_id:
            violation_source = ViolationSource.query.get(violation.violation_source_id)
            if violation_source:
                # البحث عن المصدر في قائمة الاختيارات
                for choice in form.source.choices:
                    if choice[1] == violation_source.name:
                        form.source.data = choice[0]
                        break

    if form.validate_on_submit():
        try:
            # الحصول على مصدر المخالفة من قاعدة البيانات
            source_name = dict(form.source.choices).get(form.source.data)
            violation_source = ViolationSource.query.filter_by(name=source_name).first()

            if not violation_source:
                # إذا لم يتم العثور على المصدر، قم بإنشائه
                violation_source = ViolationSource(name=source_name)
                db.session.add(violation_source)
                db.session.flush()  # للحصول على المعرف قبل الحفظ

            # تحديث بيانات المخالفة
            violation.violation_type_id = form.violation_type_id.data
            violation.violation_source_id = violation_source.id
            violation.violation_date = form.violation_date.data
            violation.notes = form.notes.data
            violation.employee_signature = form.employee_signature.data

            # حفظ التغييرات
            db.session.commit()

            flash('تم تحديث المخالفة بنجاح', 'success')
            return redirect(url_for('violations.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث المخالفة: {str(e)}', 'error')

    return render_template('violations/edit.html', form=form, violation=violation)

# حذف المخالفة
@violations_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    # الحصول على المخالفة من قاعدة البيانات
    violation = Violation.query.get_or_404(id)

    # التحقق من صلاحية المستخدم
    if violation.created_by != current_user.id and current_user.role != 'admin':
        flash('ليس لديك صلاحية لحذف هذه المخالفة', 'error')
        return redirect(url_for('violations.index'))

    try:
        # حذف المخالفة
        db.session.delete(violation)
        db.session.commit()
        flash('تم حذف المخالفة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المخالفة: {str(e)}', 'error')

    return redirect(url_for('violations.index'))

# صفحة إدارة أنواع المخالفات
@violations_bp.route('/types')
@login_required
@admin_required
def types():
    # جلب جميع أنواع المخالفات من قاعدة البيانات
    violation_types = ViolationType.query.all()
    form = ViolationTypeForm()
    import_form = ImportViolationTypesForm()
    return render_template('violations/types.html', violation_types=violation_types, form=form, import_form=import_form)

# إنشاء نوع مخالفة جديد
@violations_bp.route('/types/create', methods=['POST'])
@login_required
@admin_required
def create_type():
    form = ViolationTypeForm()

    if form.validate_on_submit():
        violation_type = ViolationType(
            name=form.name.data
        )

        db.session.add(violation_type)
        db.session.commit()

        flash('تم إنشاء نوع المخالفة بنجاح', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')

    return redirect(url_for('violations.types'))

# استيراد أنواع المخالفات من ملف Excel
@violations_bp.route('/types/import', methods=['POST'])
@login_required
@admin_required
def import_types():
    form = ImportViolationTypesForm()

    if form.validate_on_submit():
        try:
            file = form.file.data
            df = pd.read_excel(file)

            # التحقق من وجود الأعمدة المطلوبة
            required_columns = ['name']
            if not all(col in df.columns for col in required_columns):
                flash('يجب أن يحتوي الملف على عمود name', 'danger')
                return redirect(url_for('violations.types'))

            # استيراد البيانات
            count = 0
            for _, row in df.iterrows():
                # التحقق من عدم وجود نوع المخالفة مسبقاً
                existing = ViolationType.query.filter_by(name=row['name']).first()
                if not existing:
                    violation_type = ViolationType(
                        name=row['name']
                    )
                    db.session.add(violation_type)
                    count += 1

            db.session.commit()
            flash(f'تم استيراد {count} نوع مخالفة بنجاح', 'success')
        except Exception as e:
            flash(f'حدث خطأ أثناء استيراد البيانات: {str(e)}', 'danger')

    return redirect(url_for('violations.types'))

# صفحة إدارة مصادر المخالفات - تم إلغاؤها
# @violations_bp.route('/sources')
# @login_required
# @admin_required
# def sources():
#     form = ViolationSourceForm()
#     import_form = ImportViolationSourcesForm()
#     return render_template('violations/sources.html', violation_sources=[], form=form, import_form=import_form)

# إنشاء مصدر مخالفة جديد - تم إلغاؤه
# @violations_bp.route('/sources/create', methods=['POST'])
# @login_required
# @admin_required
# def create_source():
#     form = ViolationSourceForm()
#
#     if form.validate_on_submit():
#         violation_source = ViolationSource(
#             name=form.name.data
#         )
#
#         db.session.add(violation_source)
#         db.session.commit()
#
#         flash('تم إنشاء مصدر المخالفة بنجاح', 'success')
#     else:
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f'{getattr(form, field).label.text}: {error}', 'danger')
#
#     return redirect(url_for('violations.sources'))

# استيراد مصادر المخالفات من ملف Excel - تم إلغاؤه
# @violations_bp.route('/sources/import', methods=['POST'])
# @login_required
# @admin_required
# def import_sources():
#     form = ImportViolationSourcesForm()
#
#     if form.validate_on_submit():
#         try:
#             file = form.file.data
#             df = pd.read_excel(file)
#
#             # التحقق من وجود الأعمدة المطلوبة
#             required_columns = ['name']
#             if not all(col in df.columns for col in required_columns):
#                 flash('يجب أن يحتوي الملف على عمود name', 'danger')
#                 return redirect(url_for('violations.sources'))
#
#             # استيراد البيانات
#             count = 0
#             for _, row in df.iterrows():
#                 # التحقق من عدم وجود مصدر المخالفة مسبقاً
#                 existing = ViolationSource.query.filter_by(name=row['name']).first()
#                 if not existing:
#                     violation_source = ViolationSource(
#                         name=row['name']
#                     )
#                     db.session.add(violation_source)
#                     count += 1
#
#             db.session.commit()
#             flash(f'تم استيراد {count} مصدر مخالفة بنجاح', 'success')
#         except Exception as e:
#             flash(f'حدث خطأ أثناء استيراد البيانات: {str(e)}', 'danger')
#
#     return redirect(url_for('violations.sources'))
