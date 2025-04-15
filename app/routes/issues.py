from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.issue import Issue
from app.models.club import Club
from app.models.facility import Facility
from app.forms.issue import IssueForm, IssueUpdateForm
from datetime import datetime

bp = Blueprint('issues', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض قائمة الأعطال
    """
    # تم تعديل التحقق من صلاحية الوصول للسماح لجميع المستخدمين بالوصول إلى صفحة الأعطال
    # if current_user.role != 'admin' and not current_user.has_permission('issues', 'can_view'):
    #     flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
    #     return redirect(url_for('main.index'))

    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.all()
        issues = Issue.query.order_by(Issue.reported_date.desc()).all()
    else:
        clubs = current_user.clubs
        club_ids = [club.id for club in clubs]
        issues = Issue.query.filter(Issue.club_id.in_(club_ids)).order_by(Issue.reported_date.desc()).all()

    return render_template('issues/index.html', title='الأعطال', issues=issues, clubs=clubs)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    print("\n\nتم استدعاء وظيفة إنشاء العطل")
    """
    إنشاء عطل جديد
    """
    # تم تعديل التحقق من صلاحية الوصول للسماح لجميع المستخدمين بإنشاء الأعطال
    # if current_user.role != 'admin' and not current_user.has_permission('issues', 'can_create'):
    #     flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
    #     return redirect(url_for('issues.index'))

    form = IssueForm()

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    # تحميل المرافق المتاحة للنادي المحدد
    club_id = request.args.get('club_id', type=int) or form.club_id.data
    if club_id:
        facilities = Facility.query.filter_by(club_id=club_id).all()
        if facilities:
            form.facility_id.choices = [(f.id, f.name) for f in facilities]
        else:
            form.facility_id.choices = []
    else:
        form.facility_id.choices = []

    if request.method == 'POST':
        # طباعة بيانات النموذج للتشخيص
        print(f"\n\nبيانات النموذج: club_id={request.form.get('club_id')}, facility_id={request.form.get('facility_id')}, request_number={request.form.get('request_number')}")
        print(f"request_date={request.form.get('request_date')}, due_date={request.form.get('due_date')}, status={request.form.get('status')}")

        # التحقق من صلاحية الوصول للنادي
        club_id = int(request.form.get('club_id'))
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('issues.index'))

        try:
            # التحقق من قيمة المرفق ومعالجتها
            facility_id = None
            facility_id_str = request.form.get('facility_id')
            if facility_id_str and facility_id_str.strip():
                try:
                    facility_id = int(facility_id_str)
                    print(f"\n\nتم تعيين قيمة المرفق إلى: {facility_id}")
                except ValueError:
                    facility_id = None

            # إنشاء عطل جديد
            # التأكد من أن رقم الطلب باللغة الإنجليزية
            request_number_str = request.form.get('request_number')
            # تحويل الأرقام العربية إلى إنجليزية إن وجدت
            arabic_to_english = {
                '\u0660': '0', '\u0661': '1', '\u0662': '2', '\u0663': '3', '\u0664': '4',
                '\u0665': '5', '\u0666': '6', '\u0667': '7', '\u0668': '8', '\u0669': '9'
            }
            for ar, en in arabic_to_english.items():
                request_number_str = request_number_str.replace(ar, en)

            issue = Issue(
                club_id=club_id,
                facility_id=facility_id,  # استخدام القيمة التي تم التحقق منها
                request_number=int(request_number_str),
                request_date=datetime.strptime(request.form.get('request_date'), '%d/%m/%Y').date(),
                due_date=datetime.strptime(request.form.get('due_date'), '%d/%m/%Y').date(),
                status=request.form.get('status'),
                notes=request.form.get('notes'),
                reported_by=current_user.id,
                reported_date=datetime.now()
            )
            db.session.add(issue)
            db.session.commit()

            flash('تم إنشاء العطل بنجاح!', 'success')
            return redirect(url_for('issues.index'))
        except Exception as e:
            db.session.rollback()
            print(f"\n\nخطأ في إنشاء العطل: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'حدث خطأ في إنشاء العطل: {str(e)}', 'danger')

    return render_template('issues/create.html', title='إنشاء عطل جديد', form=form)

@bp.route('/<int:id>')
@login_required
def view(id):
    """
    عرض تفاصيل العطل
    """
    issue = Issue.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_club_access(issue.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا العطل', 'danger')
        return redirect(url_for('issues.index'))

    return render_template('issues/view.html', title=f'العطل: {issue.request_number}', issue=issue)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    تعديل العطل
    """
    issue = Issue.query.get_or_404(id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and not current_user.has_permission('issues', 'can_edit'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('issues.index'))

    if current_user.role != 'admin' and not current_user.has_club_access(issue.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا العطل', 'danger')
        return redirect(url_for('issues.index'))

    # تهيئة النموذج بدون البيانات الحالية
    form = IssueForm()

    # تعيين البيانات الحالية يدوياً
    form.club_id.data = issue.club_id
    form.facility_id.data = issue.facility_id
    form.request_number.data = issue.request_number
    form.status.data = issue.status
    form.notes.data = issue.notes

    # تنسيق التاريخ بالشكل المطلوب
    if request.method == 'GET':
        # عند عرض الصفحة، نعرض التاريخ بالتنسيق dd/mm/yyyy
        form.request_date.data = issue.request_date
        form.due_date.data = issue.due_date

    # تحميل النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        form.club_id.choices = [(club.id, club.name) for club in Club.query.all()]
    else:
        form.club_id.choices = [(club.id, club.name) for club in current_user.clubs]

    # تحميل المرافق المتاحة للنادي المحدد
    form.facility_id.choices = [(0, 'اختر المرفق...')] + [(f.id, f.name) for f in Facility.query.filter_by(club_id=issue.club_id).all()]

    if request.method == 'POST':
        # معالجة تنسيق التاريخ من النموذج
        try:
            # تحويل التاريخ من التنسيق dd/mm/yyyy إلى كائن تاريخ
            request_date_str = request.form.get('request_date')
            due_date_str = request.form.get('due_date')
            request_number_str = request.form.get('request_number')

            if request_date_str and due_date_str and request_number_str:
                # تحويل التاريخ من التنسيق dd/mm/yyyy إلى كائن تاريخ
                request_date = datetime.strptime(request_date_str, '%d/%m/%Y').date()
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y').date()
                request_number = int(request_number_str)

                # تعيين البيانات في النموذج
                form.request_date.data = request_date
                form.due_date.data = due_date
                form.request_number.data = request_number

                # التحقق من صحة النموذج
                if form.validate():
                    # التحقق من صلاحية الوصول للنادي
                    if current_user.role != 'admin' and not current_user.has_club_access(form.club_id.data):
                        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
                        return redirect(url_for('issues.index'))

                    # تحديث العطل
                    issue.club_id = form.club_id.data
                    issue.facility_id = form.facility_id.data if form.facility_id.data != 0 else None

                    # التأكد من أن رقم الطلب باللغة الإنجليزية
                    request_number_str = str(form.request_number.data)
                    # تحويل الأرقام العربية إلى إنجليزية إن وجدت
                    arabic_to_english = {
                        '\u0660': '0', '\u0661': '1', '\u0662': '2', '\u0663': '3', '\u0664': '4',
                        '\u0665': '5', '\u0666': '6', '\u0667': '7', '\u0668': '8', '\u0669': '9'
                    }
                    for ar, en in arabic_to_english.items():
                        request_number_str = request_number_str.replace(ar, en)

                    issue.request_number = int(request_number_str)
                    issue.request_date = request_date
                    issue.due_date = due_date
                    issue.status = form.status.data
                    issue.notes = form.notes.data

                    # حفظ التغييرات
                    db.session.commit()

                    flash('تم تحديث العطل بنجاح!', 'success')
                    return redirect(url_for('issues.view', id=issue.id))
        except Exception as e:
            # إذا حدث خطأ في معالجة التاريخ
            flash(f'حدث خطأ أثناء معالجة النموذج: {str(e)}', 'danger')
            print(f"Error processing form: {str(e)}")

    return render_template('issues/edit.html', title=f'تعديل العطل: {issue.request_number}', form=form, issue=issue)

@bp.route('/<int:id>/update_status', methods=['POST'])
@login_required
def update_status(id):
    """
    تحديث حالة العطل
    """
    issue = Issue.query.get_or_404(id)

    # تم تعديل التحقق من صلاحية الوصول للسماح لجميع المستخدمين بتعديل الأعطال
    # if current_user.role != 'admin' and not current_user.has_permission('issues', 'can_edit'):
    #     flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
    #     return redirect(url_for('issues.index'))

    if current_user.role != 'admin' and not current_user.has_club_access(issue.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا العطل', 'danger')
        return redirect(url_for('issues.index'))

    form = IssueUpdateForm()

    if request.method == 'POST':
        # تحديث حالة العطل
        status = request.form.get('status')
        notes = request.form.get('notes')

        if status:
            issue.status = status
            if notes:
                issue.notes = notes

            db.session.commit()

            flash('تم تحديث حالة العطل بنجاح!', 'success')

    return redirect(url_for('issues.view', id=issue.id))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    حذف العطل
    """
    issue = Issue.query.get_or_404(id)

    # تم تعديل التحقق من صلاحية الوصول للسماح لجميع المستخدمين بحذف الأعطال
    # if current_user.role != 'admin' and not current_user.has_permission('issues', 'can_delete'):
    #     flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
    #     return redirect(url_for('issues.index'))

    if current_user.role != 'admin' and not current_user.has_club_access(issue.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا العطل', 'danger')
        return redirect(url_for('issues.index'))

    db.session.delete(issue)
    db.session.commit()

    flash('تم حذف العطل بنجاح!', 'success')
    return redirect(url_for('issues.index'))

@bp.route('/get_facilities/<int:club_id>')
@login_required
def get_facilities(club_id):
    """
    الحصول على المرافق المتاحة للنادي
    """
    from flask import jsonify
    import traceback

    try:
        # التحقق من صلاحية الوصول للنادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            return jsonify({'facilities': []})

        # الحصول على المرافق المتاحة للنادي
        facilities = []
        club = Club.query.get(club_id)
        if club:
            # قائمة المرافق المطلوبة
            facility_names = [
                "مدخل النادي ومنطقة الإستقبال",
                "صالة الترفية",
                "الحصص الجماعية",
                "صالة الحديد",
                "صالة التمارين الوظيفيه",
                "صالة الكارديو",
                "صالة السياكل الهوائية",
                "القسم الصحي",
                "المسبح",
                "الملاعب",
                "المضمار",
                "غرفة غسيل المناشف",
                "مواقف السيارات",
                "غرفة المعدات"
            ]

            # حذف المرافق القديمة للنادي لضمان ظهور القائمة الجديدة فقط
            old_facilities = Facility.query.filter_by(club_id=club.id).all()
            for old_facility in old_facilities:
                db.session.delete(old_facility)
            db.session.commit()
            print(f"تم حذف {len(old_facilities)} مرفق قديم")

            # إنشاء المرافق الجديدة
            created_facilities = []
            for facility_name in facility_names:
                new_facility = Facility(
                    name=facility_name,
                    description=f"{facility_name} في {club.name}",
                    club_id=club.id,
                    facility_type=facility_name,
                    is_active=True
                )
                db.session.add(new_facility)
                created_facilities.append(new_facility)

            db.session.commit()
            print(f"تم إنشاء {len(created_facilities)} مرفق جديد")

            # الحصول على المرافق المحدثة
            facilities = Facility.query.filter_by(club_id=club.id).all()

        # طباعة المرافق للتحقق
        print(f"\nتم العثور على {len(facilities)} مرفق للنادي {club_id}")
        for facility in facilities:
            print(f"ID: {facility.id}, الاسم: {facility.name}, النوع: {facility.facility_type}")

        # إرجاع المرافق مع اسم المرفق فقط (بدون اسم النادي)
        facility_list = []
        for f in facilities:
            # استخراج اسم المرفق بدون اسم النادي
            facility_name = f.name
            if ' - ' in facility_name:
                facility_name = facility_name.split(' - ')[0]
            facility_list.append({'id': f.id, 'name': facility_name})

        return jsonify({'facilities': facility_list})
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
        traceback.print_exc()
        return jsonify({'facilities': [], 'error': str(e)})
