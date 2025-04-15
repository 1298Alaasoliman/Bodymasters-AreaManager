from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.issue import Issue
from app.models.club import Club
from app.models.facility import Facility
from app.forms.issue import IssueForm
from datetime import datetime
import traceback

bp = Blueprint('create_issue', __name__)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    إنشاء عطل جديد
    """
    # التحقق من صلاحية الوصول
    if hasattr(current_user, 'has_permission') and current_user.role != 'admin' and not current_user.has_permission('issues', 'can_create'):
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('issues.index'))

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
            issue = Issue(
                club_id=club_id,
                facility_id=facility_id,  # استخدام القيمة التي تم التحقق منها
                request_number=int(request.form.get('request_number')),
                request_date=datetime.strptime(request.form.get('request_date'), '%Y-%m-%d').date(),
                due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date(),
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
            traceback.print_exc()
            flash(f'حدث خطأ في إنشاء العطل: {str(e)}', 'danger')

    return render_template('issues/create_simple.html', title='إنشاء عطل جديد', form=form)

@bp.route('/get_facilities/<int:club_id>')
@login_required
def get_facilities(club_id):
    """
    الحصول على المرافق المتاحة للنادي
    """
    try:
        # التحقق من صلاحية الوصول للنادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            return jsonify({'facilities': []})

        # الحصول على المرافق المتاحة للنادي
        facilities = Facility.query.filter_by(club_id=club_id).all()

        # طباعة المرافق للتشخيص
        print(f"\n\nتم العثور على {len(facilities)} مرفق للنادي {club_id}")
        for facility in facilities:
            print(f"ID: {facility.id}, الاسم: {facility.name}, النوع: {facility.facility_type}")

        # إرجاع المرافق مع اسم المرفق فقط (بدون اسم النادي)
        facility_list = []
        for f in facilities:
            # استخراج اسم المرفق بدون اسم النادي
            facility_name = f.facility_type
            facility_list.append({'id': f.id, 'name': facility_name})

        return jsonify({'facilities': facility_list})
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
        traceback.print_exc()
        return jsonify({'facilities': [], 'error': str(e)})
