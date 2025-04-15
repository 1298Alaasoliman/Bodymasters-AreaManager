from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.employee import Employee
from app.models.schedule import Schedule
from app.forms.schedule import ScheduleForm
from datetime import time

bp = Blueprint('schedules', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض قائمة جدول سير العمل
    """
    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.all()
    else:
        clubs = current_user.clubs

    # الحصول على النادي المحدد (إذا تم تحديده)
    club_id = request.args.get('club_id', type=int)
    selected_club = None

    if club_id:
        selected_club = Club.query.get_or_404(club_id)
        # التحقق من صلاحية الوصول
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('schedules.index'))

    return render_template('schedules/index.html',
                           title='جدول سير العمل',
                           clubs=clubs,
                           selected_club=selected_club)

@bp.route('/club/<int:club_id>')
@login_required
def club_schedules(club_id):
    """
    عرض جدول سير العمل لنادي محدد
    """
    club = Club.query.get_or_404(club_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('schedules.index'))

    # الحصول على جميع الموظفين (نشطين وغير نشطين) حسب المسمى الوظيفي
    all_admin_employees = Employee.query.filter_by(club_id=club_id, position='خدمة عملاء').all()
    all_trainer_employees = Employee.query.filter_by(club_id=club_id, position='مدرب').all()
    all_worker_employees = Employee.query.filter_by(club_id=club_id, position='عامل').all()

    # الحصول على العدد المتوقع للموظفين من ملف الإعدادات
    from app.config import EXPECTED_EMPLOYEES_COUNT

    # العدد المتوقع للموظفين لكل نادي
    expected_employees = EXPECTED_EMPLOYEES_COUNT

    # طباعة للتشخيص
    print(f'\n\nالنادي: {club_id}')
    print(f'هل النادي موجود في قائمة الأندية المتوقعة: {club_id in expected_employees}')

    # الحصول على العدد الفعلي للموظفين في كل نادي
    # هذا للتشخيص فقط
    from sqlalchemy import func

    # الحصول على عدد الموظفين لكل نادي
    club_employee_counts = {}
    club_counts = db.session.query(Employee.club_id, func.count(Employee.id)).filter(Employee.is_active == True).group_by(Employee.club_id).all()
    for club_id_count, count in club_counts:
        if club_id_count is not None:  # تجاهل الموظفين بدون نادي
            club_employee_counts[club_id_count] = count

    # طباعة عدد الموظفين لكل نادي للتحقق
    print(f'\n\nعدد الموظفين لكل نادي:')
    for club_id_count, count in club_employee_counts.items():
        club_name = Club.query.get(club_id_count).name if Club.query.get(club_id_count) else 'غير معروف'
        print(f'\t- النادي {club_id_count} ({club_name}): {count} موظف')

    # التحقق من عدد الموظفين المتوقع
    total_count = len(all_admin_employees) + len(all_trainer_employees) + len(all_worker_employees)

    if club_id in expected_employees:
        # تحديد العدد المتوقع لكل نوع من الموظفين
        expected_count = expected_employees[club_id]
        print(f'العدد المتوقع للموظفين: {expected_count}')
        print(f'العدد الفعلي للموظفين: {total_count}')

        if total_count > expected_count:
            # إذا كان العدد الإجمالي أكبر من المتوقع، قم بتقليص القوائم
            # توزيع العدد المتوقع بين الأنواع الثلاثة بنسبة تقريبية
            admin_ratio = len(all_admin_employees) / total_count
            trainer_ratio = len(all_trainer_employees) / total_count
            worker_ratio = len(all_worker_employees) / total_count

            admin_count = min(len(all_admin_employees), max(1, int(expected_count * admin_ratio)))
            trainer_count = min(len(all_trainer_employees), max(1, int(expected_count * trainer_ratio)))
            worker_count = min(len(all_worker_employees), max(1, int(expected_count * worker_ratio)))

            # التأكد من أن مجموع الأعداد لا يتجاوز العدد المتوقع
            while admin_count + trainer_count + worker_count > expected_count:
                if admin_count > 1 and admin_count >= trainer_count and admin_count >= worker_count:
                    admin_count -= 1
                elif trainer_count > 1 and trainer_count >= worker_count:
                    trainer_count -= 1
                elif worker_count > 1:
                    worker_count -= 1
                else:
                    break

            # التأكد من أن مجموع الأعداد يساوي العدد المتوقع
            while admin_count + trainer_count + worker_count < expected_count:
                if admin_count < len(all_admin_employees):
                    admin_count += 1
                elif trainer_count < len(all_trainer_employees):
                    trainer_count += 1
                elif worker_count < len(all_worker_employees):
                    worker_count += 1
                else:
                    break

            # اقتطاع القوائم للعدد المطلوب
            admin_employees = all_admin_employees[:admin_count]
            trainer_employees = all_trainer_employees[:trainer_count]
            worker_employees = all_worker_employees[:worker_count]

            print(f'بعد التقليص: عدد موظفي خدمة العملاء: {len(admin_employees)}')
            print(f'بعد التقليص: عدد المدربين: {len(trainer_employees)}')
            print(f'بعد التقليص: عدد العمال: {len(worker_employees)}')
            print(f'بعد التقليص: إجمالي عدد الموظفين: {len(admin_employees) + len(trainer_employees) + len(worker_employees)}')

            # إظهار رسالة تنبيه
            flash(f'تنبيه: عدد الموظفين المتوقع لهذا النادي هو {expected_count} ولكن تم العثور على {total_count} موظف. يتم عرض الموظفين المتوقعين فقط.', 'warning')
        else:
            # إذا كان العدد الإجمالي أقل من أو يساوي المتوقع، استخدم جميع الموظفين
            admin_employees = all_admin_employees
            trainer_employees = all_trainer_employees
            worker_employees = all_worker_employees
    else:
        # إذا لم يكن هناك عدد متوقع لهذا النادي، استخدم جميع الموظفين
        admin_employees = all_admin_employees
        trainer_employees = all_trainer_employees
        worker_employees = all_worker_employees

    # طباعة عدد الموظفين للتحقق
    print(f'\n\nعدد موظفي خدمة العملاء النشطين: {len(admin_employees)}')
    print(f'عدد المدربين النشطين: {len(trainer_employees)}')
    print(f'عدد العمال النشطين: {len(worker_employees)}')
    print(f'إجمالي عدد الموظفين النشطين: {total_count}')

    # الحصول على جداول الدوامات للموظفين
    admin_schedules = {}
    trainer_schedules = {}
    worker_schedules = {}

    for employee in admin_employees:
        schedule = Schedule.query.filter_by(employee_id=employee.id).first()
        admin_schedules[employee.id] = schedule

    for employee in trainer_employees:
        schedule = Schedule.query.filter_by(employee_id=employee.id).first()
        trainer_schedules[employee.id] = schedule

    for employee in worker_employees:
        schedule = Schedule.query.filter_by(employee_id=employee.id).first()
        worker_schedules[employee.id] = schedule

    return render_template('schedules/club_schedules.html',
                           title=f'جدول سير العمل {club.name}',
                           club=club,
                           admin_employees=admin_employees,
                           trainer_employees=trainer_employees,
                           worker_employees=worker_employees,
                           admin_schedules=admin_schedules,
                           trainer_schedules=trainer_schedules,
                           worker_schedules=worker_schedules)

@bp.route('/employee/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def employee_schedule(employee_id):
    """
    إنشاء أو تعديل جدول سير العمل لموظف
    """
    employee = Employee.query.get_or_404(employee_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(employee.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا الموظف', 'danger')
        return redirect(url_for('schedules.index'))

    # البحث عن جدول الدوام الحالي للموظف
    schedule = Schedule.query.filter_by(employee_id=employee_id).first()

    # إنشاء نموذج جديد
    form = ScheduleForm()

    if request.method == 'GET' and schedule:
        # ملء النموذج بالبيانات الحالية
        form.saturday.data = schedule.saturday
        form.sunday.data = schedule.sunday
        form.monday.data = schedule.monday
        form.tuesday.data = schedule.tuesday
        form.wednesday.data = schedule.wednesday
        form.thursday.data = schedule.thursday
        form.friday.data = schedule.friday
        form.shift_type.data = schedule.shift_type
        # تحويل الأوقات إلى سلاسل نصية للقائمة المنسدلة
        if schedule.shift1_start:
            form.shift1_start.data = schedule.shift1_start.strftime('%H:%M')
        if schedule.shift1_end:
            form.shift1_end.data = schedule.shift1_end.strftime('%H:%M')
        if schedule.shift2_start:
            form.shift2_start.data = schedule.shift2_start.strftime('%H:%M')
        if schedule.shift2_end:
            form.shift2_end.data = schedule.shift2_end.strftime('%H:%M')
        form.specific_day.data = schedule.specific_day
        if schedule.specific_day_start:
            form.specific_day_start.data = schedule.specific_day_start.strftime('%H:%M')
        if schedule.specific_day_end:
            form.specific_day_end.data = schedule.specific_day_end.strftime('%H:%M')
        form.notes.data = schedule.notes

    if form.validate_on_submit():
        if not schedule:
            # إنشاء جدول دوام جديد
            schedule = Schedule(
                employee_id=employee_id,
                club_id=employee.club_id
            )
            db.session.add(schedule)

        # تحديث بيانات جدول الدوام
        schedule.saturday = form.saturday.data
        schedule.sunday = form.sunday.data
        schedule.monday = form.monday.data
        schedule.tuesday = form.tuesday.data
        schedule.wednesday = form.wednesday.data
        schedule.thursday = form.thursday.data
        schedule.friday = form.friday.data
        schedule.shift_type = form.shift_type.data
        # تحويل السلاسل النصية إلى كائنات time
        if form.shift1_start.data:
            hours, minutes = map(int, form.shift1_start.data.split(':'))
            schedule.shift1_start = time(hours, minutes)
        else:
            schedule.shift1_start = None

        if form.shift1_end.data:
            hours, minutes = map(int, form.shift1_end.data.split(':'))
            schedule.shift1_end = time(hours, minutes)
        else:
            schedule.shift1_end = None

        if form.shift2_start.data:
            hours, minutes = map(int, form.shift2_start.data.split(':'))
            schedule.shift2_start = time(hours, minutes)
        else:
            schedule.shift2_start = None

        if form.shift2_end.data:
            hours, minutes = map(int, form.shift2_end.data.split(':'))
            schedule.shift2_end = time(hours, minutes)
        else:
            schedule.shift2_end = None
        schedule.specific_day = form.specific_day.data

        # تحويل أوقات يوم التخصيص
        if form.specific_day_start.data:
            hours, minutes = map(int, form.specific_day_start.data.split(':'))
            schedule.specific_day_start = time(hours, minutes)
        else:
            schedule.specific_day_start = None

        if form.specific_day_end.data:
            hours, minutes = map(int, form.specific_day_end.data.split(':'))
            schedule.specific_day_end = time(hours, minutes)
        else:
            schedule.specific_day_end = None
        schedule.notes = form.notes.data

        db.session.commit()

        flash(f'تم حفظ جدول سير العمل {employee.name} بنجاح!', 'success')
        return redirect(url_for('schedules.club_schedules', club_id=employee.club_id))

    return render_template('schedules/employee_schedule.html',
                           title=f'جدول سير العمل {employee.name}',
                           employee=employee,
                           form=form,
                           schedule=schedule)
