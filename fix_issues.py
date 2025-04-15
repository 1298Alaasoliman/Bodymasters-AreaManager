from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import create_app, db
from app.models.issue import Issue
from app.models.club import Club
from app.models.facility import Facility
from app.forms.issue import IssueForm
from datetime import datetime
import traceback

app = create_app()

@app.route('/issues/create_issue', methods=['POST'])
@login_required
def create_issue():
    """
    إنشاء عطل جديد
    """
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
            form.facility_id.choices = [(f.id, f.facility_type) for f in facilities]
        else:
            form.facility_id.choices = []
    else:
        form.facility_id.choices = []
    
    if form.validate_on_submit():
        # طباعة بيانات النموذج للتشخيص
        print(f"\n\nبيانات النموذج: club_id={form.club_id.data}, facility_id={form.facility_id.data}, request_number={form.request_number.data}")
        print(f"request_date={form.request_date.data}, due_date={form.due_date.data}, status={form.status.data}")
        
        # التحقق من صلاحية الوصول للنادي
        if current_user.role != 'admin' and not current_user.has_club_access(form.club_id.data):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('issues.index'))
        
        try:
            # إنشاء عطل جديد
            issue = Issue(
                club_id=form.club_id.data,
                facility_id=None,  # سنقوم بتعيين قيمة المرفق لاحقًا
                request_number=form.request_number.data,
                request_date=form.request_date.data,
                due_date=form.due_date.data,
                status=form.status.data,
                notes=form.notes.data,
                reported_by=current_user.id,
                reported_date=datetime.now()
            )
            
            # تعيين قيمة المرفق إذا كانت موجودة
            if form.facility_id.data is not None:
                issue.facility_id = form.facility_id.data
            
            db.session.add(issue)
            db.session.commit()
            
            flash('تم إنشاء العطل بنجاح!', 'success')
            return redirect(url_for('issues.index'))
        except Exception as e:
            db.session.rollback()
            print(f"\n\nخطأ في إنشاء العطل: {str(e)}")
            traceback.print_exc()
            flash(f'حدث خطأ في إنشاء العطل: {str(e)}', 'danger')
    
    return render_template('issues/create.html', title='إنشاء عطل جديد', form=form)

@app.route('/issues/get_facilities_fixed/<int:club_id>')
@login_required
def get_facilities_fixed(club_id):
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

if __name__ == '__main__':
    app.run(debug=True, port=8081)
