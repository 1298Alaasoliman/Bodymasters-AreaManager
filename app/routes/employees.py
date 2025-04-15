from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.employee import Employee, WorkRecord
from app.forms.employee import EmployeeForm, WorkRecordForm
from app.utils.decorators import admin_required
import pandas as pd
from io import BytesIO
from datetime import datetime, date

bp = Blueprint('employees', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض قائمة الموظفين
    """
    # إذا كان المستخدم مديراً، عرض جميع الموظفين
    if current_user.role == 'admin':
        employees = Employee.query.all()
    else:
        # الحصول على قائمة معرفات النوادي التي يمكن للمستخدم الوصول إليها
        user_club_ids = [club.id for club in current_user.clubs]

        # إذا لم يكن لدى المستخدم أي نوادي، عرض قائمة فارغة
        if not user_club_ids:
            employees = []
        else:
            # الحصول على الموظفين التابعين للنوادي المحددة للمستخدم فقط
            employees = Employee.query.filter(Employee.club_id.in_(user_club_ids)).all()

    # حساب عدد الموظفين
    employees_count = len(employees)

    return render_template('employees/index.html', title='الموظفين', employees=employees, employees_count=employees_count)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    إنشاء موظف جديد
    """
    if current_user.role != 'admin' and not current_user.has_permission('employees', 'can_create'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('employees.index'))

    form = EmployeeForm()

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    # تحميل خيارات الدور الوظيفي بناءً على المسمى الوظيفي
    # تعريف الأدوار الوظيفية لكل مسمى وظيفي
    roles_by_position = {
        'مدير النادي': [
            'مدير نادي',
            'مدير نادي مكلف',
            'نائب مدير نادي',
            'نائب مدير نادي مكلف'
        ],
        'خدمة عملاء': [
            'خدمة عملاء',
            'منسق عمليات',
            'اختصاصي تسويق',
            'اختصاصي تسويق مكلف'
        ],
        'مدرب': [
            'مدرب',
            'مدرب كمال أجسام',
            'مدرب سباحة',
            'مدرب لياقة',
            'مدير لياقة',
            'مدرب رياضي',
            'مدرب لياقة وكمال اجسام',
            'مساعد مدرب'
        ],
        'عامل': [
            'مشرف عمال',
            'عامل نظافة',
            'عامل مغسلة'
        ]
    }

    # تجميع جميع الأدوار الوظيفية في قائمة واحدة
    all_roles = []
    for roles in roles_by_position.values():
        all_roles.extend(roles)

    # تعيين خيارات الدور الوظيفي
    form.role.choices = [(role, role) for role in sorted(all_roles)]

    if form.validate_on_submit():
        # تحويل قيمة is_active من سلسلة نصية إلى قيمة منطقية
        is_active = form.is_active.data == '1'

        employee = Employee(
            employee_number=form.employee_number.data,
            name=form.name.data,
            position=form.position.data,
            role=form.role.data,
            department='',  # تم إزالة هذا الحقل من النموذج ولكن لا يزال مطلوبًا في قاعدة البيانات
            phone='',  # تم إزالة هذا الحقل من النموذج
            email='',  # تم إزالة هذا الحقل من النموذج
            hire_date=None,  # تم إزالة هذا الحقل من النموذج
            club_id=form.club_id.data,
            is_active=is_active
        )
        db.session.add(employee)
        db.session.commit()

        # تحديث العدد المتوقع للموظفين
        try:
            from app.utils.employee_utils import update_expected_employees_count
            update_expected_employees_count()
            print(f"\n\nتم تحديث العدد المتوقع للموظفين بنجاح")
        except Exception as e:
            print(f"\n\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

        flash(f'تم إنشاء الموظف {form.name.data} بنجاح!', 'success')
        return redirect(url_for('employees.index'))

    return render_template('employees/create.html', title='إنشاء موظف جديد', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    """
    عرض تفاصيل الموظف
    """
    employee = Employee.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الموظف', 'danger')
        return redirect(url_for('employees.index'))

    work_records = WorkRecord.query.filter_by(employee_id=employee.id).order_by(WorkRecord.date.desc()).limit(30).all()

    # استرجاع جدول الدوام للموظف
    from app.models.schedule import Schedule
    schedule = Schedule.query.filter_by(employee_id=employee.id).first()

    return render_template('employees/view.html',
                           title=f'الموظف: {employee.name}',
                           employee=employee,
                           work_records=work_records,
                           schedule=schedule)

# تم إزالة وظيفة employee_work_record لأنها لم تعد مستخدمة

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    تعديل الموظف
    """
    employee = Employee.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_permission('employees', 'can_edit'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('employees.index'))

    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الموظف', 'danger')
        return redirect(url_for('employees.index'))

    form = EmployeeForm(obj=employee)

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    # تحميل خيارات الدور الوظيفي بناءً على المسمى الوظيفي
    # تعريف الأدوار الوظيفية لكل مسمى وظيفي
    roles_by_position = {
        'مدير النادي': [
            'مدير نادي',
            'مدير نادي مكلف',
            'نائب مدير نادي',
            'نائب مدير نادي مكلف'
        ],
        'خدمة عملاء': [
            'خدمة عملاء',
            'منسق عمليات',
            'اختصاصي تسويق',
            'اختصاصي تسويق مكلف'
        ],
        'مدرب': [
            'مدرب',
            'مدرب كمال أجسام',
            'مدرب سباحة',
            'مدرب لياقة',
            'مدير لياقة',
            'مدرب رياضي',
            'مدرب لياقة وكمال اجسام',
            'مساعد مدرب'
        ],
        'عامل': [
            'مشرف عمال',
            'عامل نظافة',
            'عامل مغسلة'
        ]
    }

    # تجميع جميع الأدوار الوظيفية في قائمة واحدة
    all_roles = []
    for roles in roles_by_position.values():
        all_roles.extend(roles)

    # إضافة الدور الحالي للموظف إذا لم يكن موجوداً في القائمة
    if employee.role and employee.role not in all_roles:
        all_roles.append(employee.role)

    # تعيين خيارات الدور الوظيفي
    form.role.choices = [(role, role) for role in sorted(all_roles)]

    if form.validate_on_submit():
        employee.employee_number = form.employee_number.data
        employee.name = form.name.data
        employee.position = form.position.data
        employee.role = form.role.data
        employee.department = ''
        employee.phone = ''
        employee.email = ''
        employee.hire_date = None
        # تخزين النادي القديم للتحقق من تغيير النادي
        old_club_id = employee.club_id

        # تحديث بيانات الموظف
        employee.club_id = form.club_id.data
        employee.is_active = form.is_active.data == '1'

        # حفظ التغييرات
        db.session.commit()

        # إذا تم تغيير النادي، قم بتحديث العدد المتوقع للموظفين
        if old_club_id != employee.club_id:
            try:
                from app.utils.employee_utils import update_expected_employees_count
                update_expected_employees_count()
                print(f"\n\nتم تحديث العدد المتوقع للموظفين بنجاح")
            except Exception as e:
                print(f"\n\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

        flash(f'تم تحديث الموظف {employee.name} بنجاح!', 'success')
        return redirect(url_for('employees.view', id=employee.id))

    return render_template('employees/edit.html', title=f'تعديل الموظف: {employee.name}', form=form, employee=employee)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    حذف الموظف
    """
    if current_user.role != 'admin' and not current_user.has_permission('employees', 'can_delete'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('employees.index'))

    employee = Employee.query.get_or_404(id)

    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الموظف', 'danger')
        return redirect(url_for('employees.index'))

    # تخزين النادي قبل الحذف
    club_id = employee.club_id

    db.session.delete(employee)
    db.session.commit()

    # تحديث العدد المتوقع للموظفين
    try:
        from app.utils.employee_utils import update_expected_employees_count
        update_expected_employees_count()
        print(f"\n\nتم تحديث العدد المتوقع للموظفين بعد حذف موظف من النادي {club_id}")
    except Exception as e:
        print(f"\n\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

    flash(f'تم حذف الموظف {employee.name} بنجاح!', 'success')
    return redirect(url_for('employees.index'))

@bp.route('/delete-all', methods=['POST'])
@login_required
def delete_all():
    """
    حذف جميع الموظفين
    """
    # التحقق من أن المستخدم هو المسؤول فقط
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية لحذف جميع الموظفين', 'danger')
        return redirect(url_for('employees.index'))

    # حذف جميع الموظفين
    employees = Employee.query.all()
    count = len(employees)
    for employee in employees:
        db.session.delete(employee)
    db.session.commit()

    # تحديث العدد المتوقع للموظفين
    try:
        from app.utils.employee_utils import update_expected_employees_count
        update_expected_employees_count()
        print(f"\n\nتم تحديث العدد المتوقع للموظفين بعد حذف جميع الموظفين")
    except Exception as e:
        print(f"\n\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

    flash(f'تم حذف {count} موظف بنجاح', 'success')
    return redirect(url_for('employees.index'))


@bp.route('/delete_multiple', methods=['POST'])
@login_required
@admin_required
def delete_multiple():
    """
    حذف مجموعة من الموظفين دفعة واحدة
    """
    if not request.json or 'employee_ids' not in request.json:
        return jsonify({'success': False, 'message': 'البيانات غير صالحة'}), 400

    employee_ids = request.json.get('employee_ids', [])

    if not employee_ids:
        return jsonify({'success': False, 'message': 'لم يتم تحديد أي موظف للحذف'}), 400

    deleted_count = 0
    deleted_names = []

    for employee_id in employee_ids:
        employee = Employee.query.get(employee_id)
        if employee:
            deleted_names.append(employee.name)
            db.session.delete(employee)
            deleted_count += 1

    if deleted_count > 0:
        db.session.commit()

        # تحديث العدد المتوقع للموظفين
        try:
            from app.utils.employee_utils import update_expected_employees_count
            update_expected_employees_count()
            print(f"\n\nتم تحديث العدد المتوقع للموظفين بعد حذف مجموعة من الموظفين")
        except Exception as e:
            print(f"\n\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

        message = f'تم حذف {deleted_count} موظف بنجاح: {"، ".join(deleted_names)}'
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'message': 'لم يتم العثور على الموظفين المحددين'}), 404

@bp.route('/import', methods=['GET', 'POST'])
@bp.route('/import_excel', methods=['GET', 'POST'])  # إضافة مسار بديل للتوافق مع الرابط الموجود في القالب
@login_required
def import_employees():
    """
    استيراد الموظفين من ملف Excel
    """
    print("\n\nتم استدعاء وظيفة استيراد الموظفين")
    print(f"المستخدم: {current_user.username}, الدور: {current_user.role}")

    if current_user.role != 'admin' and not current_user.has_permission('employees', 'can_create'):
        print("ليس لديه صلاحية للوصول إلى هذه الصفحة")
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('employees.index'))

    # جلب قائمة الأندية لعرضها في القالب
    from app.models.club import Club
    print("تم استيراد نموذج Club")

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        file = request.files['file']
        club_id = request.form.get('club_id', type=int)

        if not club_id:
            flash('يرجى تحديد النادي', 'danger')
            return redirect(request.url)

        # التحقق من صلاحية الوصول إلى النادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('employees.index'))

        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        if file:
            try:
                # قراءة ملف Excel
                df = pd.read_excel(BytesIO(file.read()))

                # طباعة أسماء الأعمدة الموجودة في الملف للتشخيص
                print("\n\nأسماء الأعمدة الموجودة في الملف:")
                for i, col in enumerate(df.columns):
                    print(f"{i+1}. '{col}' (type: {type(col).__name__})")

                # طباعة الصف الأول من البيانات للتحقق
                if not df.empty:
                    print("\nالصف الأول من البيانات:")
                    first_row = df.iloc[0]
                    for col in df.columns:
                        print(f"- {col}: {first_row[col]}")

                # تنظيف أسماء الأعمدة (إزالة المسافات الزائدة)
                cleaned_columns = {col: col.strip() for col in df.columns}
                df = df.rename(columns=cleaned_columns)

                # محاولة التعرف على الأعمدة بشكل مباشر
                # إذا كان هناك عمود يحتوي على كلمة "اسم" أو "موظف"، فهو على الأرجح عمود الاسم
                direct_mapping = {}
                for col in df.columns:
                    col_lower = col.lower()
                    if 'رقم' in col_lower or 'id' in col_lower.lower():
                        direct_mapping[col] = 'employee_number'
                    elif 'اسم' in col_lower or 'موظف' in col_lower:
                        direct_mapping[col] = 'name'
                    elif 'وظيف' in col_lower or 'مسمى' in col_lower:
                        direct_mapping[col] = 'position'
                    elif 'دور' in col_lower or 'قسم' in col_lower or 'إدار' in col_lower:
                        direct_mapping[col] = 'department'
                    elif 'ناد' in col_lower:
                        direct_mapping[col] = 'club_name'
                    elif 'حال' in col_lower or 'وضع' in col_lower:
                        direct_mapping[col] = 'status'

                print("\nالتعرف المباشر على الأعمدة:")
                for arabic_col, eng_col in direct_mapping.items():
                    print(f"- {arabic_col} => {eng_col}")

                # تعريف البدائل المحتملة لكل عمود
                column_alternatives = {
                    'employee_number': ['الرقم الوظيفي', 'رقم الموظف', 'رقم الهوية', 'رقم', 'ID', 'الرقم'],
                    'name': ['اسم الموظف', 'الاسم', 'الموظف', 'اسم'],
                    'position': ['الوظيفة', 'المسمى الوظيفي', 'مسمى وظيفي', 'مسمى'],
                    'department': ['الدور الوظيفي', 'الدور', 'القسم', 'الإدارة'],
                    'club_name': ['النادي', 'اسم النادي', 'نادي'],
                    'status': ['الحالة', 'حالة الموظف', 'الوضع']
                }

                # دمج التعرف المباشر مع التعرف بالبدائل
                column_mapping = direct_mapping.copy()  # استخدام التعرف المباشر كأساس

                # إضافة التعرف بالبدائل
                for eng_col, arabic_alternatives in column_alternatives.items():
                    # التحقق مما إذا كان العمود موجودًا بالفعل في التعرف المباشر
                    if eng_col in column_mapping.values():
                        continue  # تخطي إذا كان العمود موجودًا بالفعل

                    # البحث عن العمود باستخدام البدائل
                    for alt in arabic_alternatives:
                        if alt in df.columns:
                            column_mapping[alt] = eng_col
                            break

                print("\nالتعرف النهائي على الأعمدة:")
                for arabic_col, eng_col in column_mapping.items():
                    print(f"- {arabic_col} => {eng_col}")

                # التحقق من وجود الأعمدة المطلوبة
                required_columns = ['employee_number', 'name', 'position', 'department']
                missing_eng_columns = []

                # التحقق من الأعمدة المفقودة
                for eng_col in required_columns:
                    if eng_col not in column_mapping.values():
                        missing_eng_columns.append(eng_col)

                if missing_eng_columns:
                    # إذا كانت هناك أعمدة مفقودة، فقم بمحاولة التخمين بناءً على محتوى الأعمدة
                    print(f"\nالأعمدة المفقودة: {missing_eng_columns}")
                    print("محاولة التخمين بناءً على محتوى الأعمدة...")

                    # إذا كان هناك عمود واحد فقط غير معروف، فقد يكون هو العمود المفقود
                    unknown_columns = [col for col in df.columns if col not in column_mapping]
                    if len(unknown_columns) == len(missing_eng_columns):
                        for i, eng_col in enumerate(missing_eng_columns):
                            if i < len(unknown_columns):
                                column_mapping[unknown_columns[i]] = eng_col
                                print(f"تم تخمين {unknown_columns[i]} => {eng_col}")

                    # التحقق مرة أخرى بعد التخمين
                    missing_eng_columns = [col for col in required_columns if col not in column_mapping.values()]
                    if missing_eng_columns:
                        missing_columns_arabic = [column_alternatives[col][0] for col in missing_eng_columns]
                        flash(f'الأعمدة المطلوبة غير موجودة: {"، ".join(missing_columns_arabic)}', 'danger')
                        flash(f'الأعمدة المطلوبة هي: الرقم الوظيفي، اسم الموظف، الوظيفة، الدور الوظيفي', 'info')
                        return redirect(request.url)

                print("\nتم التعرف على الأعمدة التالية:")
                for arabic_col, eng_col in column_mapping.items():
                    print(f"- {arabic_col} => {eng_col}")

                # إعادة تسمية الأعمدة
                print("\nإعادة تسمية الأعمدة:")
                for arabic_col, eng_col in column_mapping.items():
                    print(f"- {arabic_col} => {eng_col}")

                # إنشاء نسخة من DataFrame مع الأسماء الجديدة
                renamed_df = df.copy()
                for arabic_col, eng_col in column_mapping.items():
                    if arabic_col in renamed_df.columns:
                        renamed_df = renamed_df.rename(columns={arabic_col: eng_col})

                # التحقق من وجود الأعمدة المطلوبة بعد إعادة التسمية
                required_columns = ['employee_number', 'name', 'position', 'department']
                missing_columns = [col for col in required_columns if col not in renamed_df.columns]

                print("\nالأعمدة الموجودة بعد إعادة التسمية:")
                for col in renamed_df.columns:
                    print(f"- {col}")

                if missing_columns:
                    missing_columns_arabic = [column_alternatives[col][0] for col in missing_columns]
                    flash(f'الأعمدة المطلوبة غير موجودة: {"، ".join(missing_columns_arabic)}', 'danger')
                    flash(f'الأعمدة المطلوبة هي: الرقم الوظيفي، اسم الموظف، الوظيفة، الدور الوظيفي', 'info')
                    return redirect(request.url)

                # استخدام DataFrame المعاد تسميته
                df = renamed_df
                print("الأعمدة المطلوبة موجودة وتم التعرف عليها بنجاح")

                # إضافة الموظفين
                count = 0
                imported_employees = []  # قائمة لتتبع الموظفين المستوردين

                # طباعة عدد الصفوف في ملف الإكسيل
                print(f"\nعدد الصفوف في ملف الإكسيل: {len(df)}")

                # طباعة عدد الموظفين الحاليين في النادي المحدد
                current_employees_count = Employee.query.filter_by(club_id=club_id).count()
                print(f"عدد الموظفين الحاليين في النادي {club_id}: {current_employees_count}")

                for _, row in df.iterrows():
                    # التحقق من عدم وجود موظف بنفس الرقم الوظيفي
                    existing = Employee.query.filter_by(employee_number=row['employee_number']).first()
                    if existing:
                        print(f"تجاهل الموظف {row['name']} (الرقم الوظيفي: {row['employee_number']}) - موجود بالفعل")
                        continue

                    # تحديد النادي من اسم النادي في ملف الإكسيل
                    selected_club_id = club_id  # القيمة الافتراضية من النموذج

                    # طباعة النادي المحدد للتشخيص
                    print(f"\nالنادي المحدد من النموذج: {club_id}")

                    if 'club_name' in row and row['club_name'] and not pd.isna(row['club_name']):
                        # استخراج اسم النادي من النص
                        club_name_text = str(row['club_name']).strip()
                        print(f"اسم النادي من ملف الإكسيل: '{club_name_text}'")

                        # البحث عن النادي باستخدام مطابقة دقيقة للاسم
                        from app.models.club import Club

                        # البحث عن تطابق تام أولاً
                        exact_match = Club.query.filter(Club.name == club_name_text).first()
                        if exact_match:
                            selected_club_id = exact_match.id
                            print(f"تم العثور على تطابق تام للنادي: {exact_match.name} (ID: {exact_match.id})")
                        else:
                            # إذا لم يتم العثور على تطابق تام، ابحث عن أفضل تطابق
                            best_match = None
                            best_match_score = 0

                            for club in Club.query.all():
                                # التحقق من أن اسم النادي موجود بالكامل في النص
                                if club.name in club_name_text:
                                    # استخدام طول الاسم كمقياس لدقة التطابق (الأسماء الأطول أفضل)
                                    match_score = len(club.name)
                                    if match_score > best_match_score:
                                        best_match = club
                                        best_match_score = match_score

                            if best_match:
                                selected_club_id = best_match.id
                                print(f"تم العثور على أفضل تطابق للنادي: {best_match.name} (ID: {best_match.id})")
                            else:
                                print(f"لم يتم العثور على نادي مطابق، استخدام النادي الافتراضي: {club_id}")

                    # تحديد حالة الموظف
                    is_active = True
                    if 'status' in row and row['status']:
                        status_text = str(row['status']).strip()
                        if 'مجاز' in status_text or 'إجازة' in status_text:
                            is_active = False

                    # إنشاء موظف جديد
                    employee = Employee(
                        employee_number=row['employee_number'],
                        name=row['name'],
                        position=row['position'],
                        role=row['department'],  # تعيين الدور الوظيفي من عمود "الدور الوظيفي"
                        department=row['department'],  # الاحتفاظ بهذا للتوافق مع البيانات القديمة
                        phone=row.get('phone', None),
                        email=row.get('email', None),
                        hire_date=row.get('hire_date', None),
                        club_id=selected_club_id,
                        is_active=is_active
                    )
                    db.session.add(employee)
                    count += 1

                    # إضافة الموظف إلى قائمة الموظفين المستوردين
                    imported_employees.append({
                        'name': row['name'],
                        'employee_number': row['employee_number'],
                        'club_id': selected_club_id
                    })

                    print(f"تمت إضافة الموظف {row['name']} (الرقم الوظيفي: {row['employee_number']}) إلى النادي {selected_club_id}")

                db.session.commit()

                # طباعة ملخص الاستيراد
                print("\n\nملخص الاستيراد:")
                print(f"- عدد الصفوف في ملف الإكسيل: {len(df)}")
                print(f"- عدد الموظفين المستوردين: {count}")
                print(f"- النادي المحدد: {club_id}")

                # طباعة عدد الموظفين الجديد في النادي المحدد
                new_employees_count = Employee.query.filter_by(club_id=club_id).count()
                print(f"- عدد الموظفين الجديد في النادي {club_id}: {new_employees_count}")
                print(f"- عدد الموظفين المضافين: {new_employees_count - current_employees_count}")

                # طباعة قائمة الموظفين المستوردين حسب النادي
                club_counts = {}
                for emp in imported_employees:
                    club_id = emp['club_id']
                    if club_id in club_counts:
                        club_counts[club_id] += 1
                    else:
                        club_counts[club_id] = 1

                print("\nعدد الموظفين المستوردين حسب النادي:")
                for club_id, count in club_counts.items():
                    from app.models.club import Club
                    club_name = Club.query.get(club_id).name if Club.query.get(club_id) else f"نادي {club_id}"
                    print(f"- {club_name} (ID: {club_id}): {count} موظف")

                # تحديث العدد المتوقع للموظفين
                try:
                    from app.utils.employee_utils import update_expected_employees_count
                    update_expected_employees_count()
                    print(f"\nتم تحديث العدد المتوقع للموظفين بعد استيراد الموظفين")
                except Exception as e:
                    print(f"\nحدث خطأ عند تحديث العدد المتوقع للموظفين: {e}")

                flash(f'تم استيراد {count} موظف بنجاح!', 'success')
                return redirect(url_for('employees.index'))

            except Exception as e:
                flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
                return redirect(request.url)

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).order_by(Club.name).all()
        print(f"\n\nالمستخدم مسؤول: تم تحميل {len(clubs)} نادي")
    else:
        # الحصول على النوادي النشطة التي يملك المستخدم صلاحية الوصول إليها
        user_clubs = current_user.clubs
        print(f"\n\nالمستخدم عادي: عدد النوادي المتاحة للمستخدم {len(user_clubs)}")
        club_ids = [club.id for club in user_clubs]
        clubs = Club.query.filter(Club.id.in_(club_ids), Club.is_active==True).order_by(Club.name).all()
        print(f"عدد النوادي النشطة المتاحة للمستخدم: {len(clubs)}")

    # إذا لم يتم العثور على أي نادي، قم بتحميل جميع النوادي النشطة
    if not clubs:
        print("\n\nلم يتم العثور على أي نادي، سيتم تحميل جميع النوادي النشطة")
        clubs = Club.query.filter_by(is_active=True).order_by(Club.name).all()
        print(f"تم تحميل {len(clubs)} نادي")

    return render_template('employees/import.html', title='استيراد الموظفين', clubs=clubs)

@bp.route('/work_record/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def add_work_record(employee_id):
    """
    إضافة سجل عمل للموظف
    """
    # لا نقوم بالتوجيه لأننا نريد عرض صفحة إضافة سجل عمل جديد
    employee = Employee.query.get_or_404(employee_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الموظف', 'danger')
        return redirect(url_for('employees.index'))

    form = WorkRecordForm()

    if form.validate_on_submit():
        work_record = WorkRecord(
            employee_id=employee_id,
            date=form.date.data,
            time_in=form.time_in.data,
            time_out=form.time_out.data,
            is_leave=form.is_leave.data,
            leave_type=form.leave_type.data if form.is_leave.data else None,
            notes=form.notes.data,
            created_by=current_user.id
        )

        # حساب ساعات العمل إذا تم تحديد وقت الدخول والخروج
        if form.time_in.data and form.time_out.data and not form.is_leave.data:
            work_record.calculate_hours()

        db.session.add(work_record)
        db.session.commit()

        flash('تم إضافة سجل العمل بنجاح!', 'success')
        return redirect(url_for('employees.view', id=employee_id))

    # تعيين التاريخ الافتراضي إلى اليوم
    if not form.date.data:
        form.date.data = date.today()

    return render_template('employees/add_work_record.html',
                           title=f'إضافة سجل عمل: {employee.name}',
                           form=form,
                           employee=employee)

@bp.route('/work_record/<int:employee_id>/readonly')
@login_required
def view_work_record_readonly(employee_id):
    """
    عرض سجل عمل للقراءة فقط
    """
    employee = Employee.query.get_or_404(employee_id)
    # إنشاء سجل عمل وهمي للعرض فقط
    from datetime import date, time
    work_record = WorkRecord.query.filter_by(employee_id=employee_id).order_by(WorkRecord.date.desc()).first()

    if not work_record:
        # إنشاء سجل عمل وهمي للعرض فقط (لن يتم حفظه في قاعدة البيانات)
        work_record = WorkRecord()
        work_record.employee_id = employee_id
        work_record.date = date.today()
        work_record.time_in = time(8, 0)
        work_record.time_out = time(16, 0)
        work_record.hours_worked = 8.0
        work_record.is_leave = False
        work_record.notes = 'سجل عمل للعرض فقط'
        work_record.created_at = datetime.utcnow()
        work_record.updated_at = datetime.utcnow()

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا السجل', 'danger')
        return redirect(url_for('employees.index'))

    return render_template('employees/work_record_readonly.html',
                           title=f'عرض سجل عمل: {employee.name}',
                           employee=employee,
                           work_record=work_record)

@bp.route('/work_record/<int:record_id>/view')
@login_required
def view_work_record(record_id):
    """
    عرض سجل عمل
    """
    work_record = WorkRecord.query.get_or_404(record_id)
    employee = Employee.query.get_or_404(work_record.employee_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا السجل', 'danger')
        return redirect(url_for('employees.index'))

    return render_template('employees/view_work_record.html',
                           title=f'عرض سجل عمل: {employee.name}',
                           employee=employee,
                           work_record=work_record)

@bp.route('/work_record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_work_record(record_id):
    """
    تعديل سجل عمل
    """
    work_record = WorkRecord.query.get_or_404(record_id)
    employee = Employee.query.get_or_404(work_record.employee_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا السجل', 'danger')
        return redirect(url_for('employees.index'))

    form = WorkRecordForm(obj=work_record)

    if form.validate_on_submit():
        work_record.date = form.date.data
        work_record.time_in = form.time_in.data
        work_record.time_out = form.time_out.data
        work_record.is_leave = form.is_leave.data
        work_record.leave_type = form.leave_type.data if form.is_leave.data else None
        work_record.notes = form.notes.data

        # حساب ساعات العمل إذا تم تحديد وقت الدخول والخروج
        if form.time_in.data and form.time_out.data and not form.is_leave.data:
            work_record.calculate_hours()
        else:
            work_record.hours_worked = None

        db.session.commit()

        flash('تم تحديث سجل العمل بنجاح!', 'success')
        return redirect(url_for('employees.view', id=employee.id))

    return render_template('employees/edit_work_record.html',
                           title=f'تعديل سجل عمل: {employee.name}',
                           form=form,
                           employee=employee,
                           work_record=work_record)

@bp.route('/work_record/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_work_record(record_id):
    """
    حذف سجل عمل
    """
    work_record = WorkRecord.query.get_or_404(record_id)
    employee = Employee.query.get_or_404(work_record.employee_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا السجل', 'danger')
        return redirect(url_for('employees.index'))

    db.session.delete(work_record)
    db.session.commit()

    flash('تم حذف سجل العمل بنجاح!', 'success')
    return redirect(url_for('employees.view', id=employee.id))

@bp.route('/report')
@login_required
def report():
    """
    تقرير الموظفين
    """
    if current_user.role == 'admin':
        clubs = Club.query.all()
    else:
        clubs = current_user.clubs

    club_id = request.args.get('club_id', type=int)
    department = request.args.get('department', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # التحقق من صلاحية الوصول إلى النادي
    if club_id and current_user.role != 'admin' and not current_user.has_club_access(club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('employees.report'))

    # بناء الاستعلام
    query = db.session.query(
        Employee.id,
        Employee.name,
        Employee.employee_number,
        Employee.position,
        Employee.department,
        Club.name.label('club_name'),
        db.func.count(WorkRecord.id).label('work_days'),
        db.func.sum(WorkRecord.hours_worked).label('total_hours'),
        db.func.sum(db.case((WorkRecord.is_leave == True, 1), else_=0)).label('leave_days')
    ).join(Club, Employee.club_id == Club.id
    ).outerjoin(WorkRecord, Employee.id == WorkRecord.employee_id)

    # تطبيق الفلاتر
    if club_id:
        query = query.filter(Employee.club_id == club_id)
    else:
        # إذا لم يتم تحديد نادي، فقط عرض النوادي التي يمكن للمستخدم الوصول إليها
        if current_user.role != 'admin':
            club_ids = [club.id for club in current_user.clubs]
            query = query.filter(Employee.club_id.in_(club_ids))

    if department:
        query = query.filter(Employee.department == department)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(db.or_(
                WorkRecord.date.between(start, end),
                WorkRecord.date == None
            ))
        except ValueError:
            pass

    # تجميع النتائج
    query = query.group_by(
        Employee.id,
        Employee.name,
        Employee.employee_number,
        Employee.position,
        Employee.department,
        Club.name
    )

    results = query.all()

    # الحصول على قائمة الأقسام المتاحة
    departments = db.session.query(Employee.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]

    return render_template('employees/report.html',
                           title='تقرير الموظفين',
                           results=results,
                           clubs=clubs,
                           departments=departments,
                           selected_club_id=club_id,
                           selected_department=department,
                           start_date=start_date,
                           end_date=end_date)

@bp.route('/import_excel', methods=['GET', 'POST'])
@login_required
def import_excel():
    """
    استيراد الموظفين من ملف Excel
    """
    if current_user.role != 'admin' and not current_user.has_permission('employees', 'can_create'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('employees.index'))

    if request.method == 'POST':
        # التحقق من وجود ملف
        if 'file' not in request.files:
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('لم يتم تحديد ملف', 'danger')
            return redirect(request.url)

        # التحقق من امتداد الملف
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('يجب أن يكون الملف بصيغة Excel (.xlsx أو .xls)', 'danger')
            return redirect(request.url)

        try:
            # قراءة ملف Excel
            df = pd.read_excel(BytesIO(file.read()))

            # قائمة بالأعمدة المطلوبة باللغة العربية وبدائلها المحتملة
            column_variants = {
                'employee_number': ['الرقم الوظيفي', 'رقم الموظف', 'رقم وظيفي', 'الرقم', 'ID', 'رقم'],
                'name': ['اسم الموظف', 'إسم الموظف', 'الاسم', 'الموظف', 'اسم'],
                'position': ['المسمى الوظيفي', 'الوظيفة', 'المسمى', 'المنصب'],
                'role': ['الدور الوظيفي', 'الدور', 'دور'],
                'club_name': ['النادي', 'اسم النادي', 'نادي'],
                'status': ['الحالة', 'حالة', 'الوضع']
            }

            # إنشاء قاموس لترجمة الأعمدة من العربية إلى الإنجليزية
            column_mapping = {}

            # البحث عن الأعمدة المطلوبة في الملف
            for eng_col, ar_variants in column_variants.items():
                found = False
                for variant in ar_variants:
                    # البحث عن العمود بالضبط أو العمود الذي يحتوي على النص
                    for col in df.columns:
                        if col.strip() == variant or variant in col:
                            column_mapping[col] = eng_col
                            found = True
                            break
                    if found:
                        break

                # إذا لم يتم العثور على العمود المطلوب
                if not found and eng_col in ['employee_number', 'name']:
                    # الرقم الوظيفي واسم الموظف إلزامية
                    flash(f'العمود {ar_variants[0]} غير موجود في الملف', 'danger')
                    return redirect(request.url)

            # إعادة تسمية الأعمدة لتسهيل التعامل معها في الكود
            df = df.rename(columns=column_mapping)

            # إضافة أعمدة افتراضية إذا لم تكن موجودة
            if 'position' not in df.columns:
                df['position'] = 'موظف'  # قيمة افتراضية
            if 'role' not in df.columns:
                df['role'] = 'موظف'  # قيمة افتراضية
            if 'club_name' not in df.columns:
                df['club_name'] = ''  # سيتم التعامل معها لاحقًا
            if 'status' not in df.columns:
                df['status'] = 'يعمل'  # القيمة الافتراضية هي يعمل

            # إضافة الموظفين
            count = 0
            errors = 0
            skipped = 0
            for _, row in df.iterrows():
                try:
                    # تخطي الصفوف الفارغة
                    if pd.isna(row.get('employee_number')) or pd.isna(row.get('name')):
                        skipped += 1
                        continue

                    # التحقق من عدم وجود موظف بنفس الرقم الوظيفي
                    employee_number = str(row['employee_number']).strip()
                    if not employee_number:
                        skipped += 1
                        continue

                    existing = Employee.query.filter_by(employee_number=employee_number).first()
                    if existing:
                        errors += 1
                        continue

                    # الحصول على النادي من الاسم
                    club = None
                    if 'club_name' in row and not pd.isna(row['club_name']) and str(row['club_name']).strip():
                        club_name = str(row['club_name']).strip()
                        club = Club.query.filter_by(name=club_name).first()
                        # إذا لم يتم العثور على النادي بالاسم المطابق، نبحث عن نادي يحتوي اسمه على النص
                        if not club:
                            clubs = Club.query.filter(Club.name.like(f'%{club_name}%')).all()
                            if clubs:
                                club = clubs[0]  # استخدام أول نادي مطابق

                    # إذا لم يتم تحديد نادي، نستخدم أول نادي موجود
                    if not club:
                        club = Club.query.first()
                        if not club:
                            errors += 1
                            continue

                    # تحويل الحالة إلى قيمة منطقية
                    is_active = True
                    if 'status' in row and not pd.isna(row['status']):
                        status_value = str(row['status']).strip()
                        if 'مجاز' in status_value or status_value == '0' or status_value.lower() == 'false':
                            is_active = False

                    # التحقق من المسمى الوظيفي
                    position = 'موظف'  # قيمة افتراضية
                    if 'position' in row and not pd.isna(row['position']):
                        position = str(row['position']).strip()

                    # التحقق من الدور الوظيفي
                    role = 'موظف'  # قيمة افتراضية
                    if 'role' in row and not pd.isna(row['role']):
                        role = str(row['role']).strip()

                    # التحقق من اسم الموظف
                    name = ''
                    if 'name' in row and not pd.isna(row['name']):
                        name = str(row['name']).strip()
                    if not name:
                        skipped += 1
                        continue

                    employee = Employee(
                        employee_number=employee_number,
                        name=name,
                        position=position,
                        role=role,  # إضافة حقل الدور الوظيفي
                        department='',  # تم إزالة هذا الحقل من النموذج ولكن لا يزال مطلوبًا في قاعدة البيانات
                        phone='',  # تم إزالة هذا الحقل من النموذج
                        email='',  # تم إزالة هذا الحقل من النموذج
                        hire_date=None,  # تم إزالة هذا الحقل من النموذج
                        club_id=club.id,
                        is_active=is_active
                    )
                    db.session.add(employee)
                    count += 1
                except Exception as e:
                    print(f"Error processing row: {e}")
                    errors += 1

            db.session.commit()
            flash(f'تم استيراد {count} موظف بنجاح! تم تجاهل {errors} سجل بسبب الأخطاء و {skipped} سجل بسبب نقص البيانات.', 'success')
            return redirect(url_for('employees.index'))

        except Exception as e:
            flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
            return redirect(request.url)

    # تم إلغاء تحميل النوادي لأن الاستيراد سيتضمن كل النوادي وسيكون لمرة واحدة
    return render_template('employees/import.html', title='استيراد الموظفين')