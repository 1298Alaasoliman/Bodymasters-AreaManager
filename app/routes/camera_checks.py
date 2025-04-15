from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.camera_check import CameraCheck
from app.forms.camera_check import CameraCheckForm
from datetime import datetime, time, timedelta
from sqlalchemy import func, and_

bp = Blueprint('camera_checks', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    صفحة تشيك الكاميرات الجديد
    """
    form = CameraCheckForm()

    # الحصول على النوادي المتاحة للمستخدم
    # إذا كان المستخدم مديراً، فسيتمكن من الوصول إلى جميع النوادي
    if current_user.role in ['admin', 'manager']:
        user_clubs = Club.query.filter(Club.is_active == True).all()
    else:
        user_clubs = Club.query.join(Club.users).filter(Club.users.any(id=current_user.id), Club.is_active == True).all()

    # طباعة عدد النوادي المتاحة للمستخدم للتصحيح
    print(f"\n\nAvailable clubs for user {current_user.username}: {len(user_clubs)}")
    for club in user_clubs:
        print(f"Club ID: {club.id}, Name: {club.name}")

    # إضافة خيار افتراضي للقائمة
    form.club_id.choices = [(0, 'اختر النادي')] + [(club.id, club.name) for club in user_clubs]

    if form.validate_on_submit():
        # التحقق من اختيار نادي صحيح
        try:
            club_id = int(form.club_id.data)
            if club_id <= 0:
                flash('الرجاء اختيار نادي صحيح', 'warning')
                return render_template('camera_checks/index.html', form=form, title='تشيك كاميرات جديد')
        except ValueError:
            flash('الرجاء اختيار نادي صحيح', 'warning')
            return render_template('camera_checks/index.html', form=form, title='تشيك كاميرات جديد')

        # التحقق من عدم وجود تشيك سابق لنفس النادي في نفس اليوم
        today_start = datetime.combine(datetime.today(), time.min)
        today_end = datetime.combine(datetime.today(), time.max)

        existing_check = CameraCheck.query.filter(
            CameraCheck.club_id == club_id,
            CameraCheck.check_date >= today_start,
            CameraCheck.check_date <= today_end
        ).first()

        if existing_check:
            flash('لا يمكن إجراء تشيك الكاميرات لهذا النادي أكثر من مرة واحدة في اليوم', 'warning')
            return redirect(url_for('camera_checks.index'))

        # إنشاء تشيك جديد
        camera_check = CameraCheck(
            club_id=club_id,
            user_id=current_user.id,
            opening_check=form.opening_check.data,
            check_12=form.check_12.data,
            check_2=form.check_2.data,
            check_3=form.check_3.data,
            check_5=form.check_5.data,
            check_8=form.check_8.data,
            check_10=form.check_10.data,
            check_11=form.check_11.data,
            check_1150=form.check_1150.data,
            violations_count=form.violations_count.data,
            notes=form.notes.data
        )

        db.session.add(camera_check)
        db.session.commit()

        flash('تم حفظ تشيك الكاميرات بنجاح', 'success')
        return redirect(url_for('camera_checks.history'))

    return render_template('camera_checks/index.html', form=form, title='تشيك كاميرات جديد')

@bp.route('/history')
@login_required
def history():
    """
    صفحة سجل تشيكات الكاميرات
    """
    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role in ['admin', 'manager']:
        user_clubs_ids = [club.id for club in Club.query.filter(Club.is_active == True).all()]
    else:
        user_clubs_ids = [club.id for club in Club.query.join(Club.users).filter(Club.users.any(id=current_user.id), Club.is_active == True).all()]

    # الحصول على تشيكات الكاميرات للنوادي المتاحة للمستخدم
    camera_checks = CameraCheck.query.filter(CameraCheck.club_id.in_(user_clubs_ids)).order_by(CameraCheck.check_date.desc()).all()

    return render_template('camera_checks/history.html', camera_checks=camera_checks, title='سجل تشيكات الكاميرات')

@bp.route('/details/<int:check_id>')
@login_required
def details(check_id):
    """
    صفحة تفاصيل تشيك الكاميرات
    """
    camera_check = CameraCheck.query.get_or_404(check_id)

    # التحقق من أن المستخدم لديه صلاحية الوصول إلى هذا التشيك
    if current_user.role in ['admin', 'manager']:
        # المدير لديه صلاحية الوصول إلى جميع التشيكات
        pass
    else:
        user_clubs_ids = [club.id for club in Club.query.join(Club.users).filter(Club.users.any(id=current_user.id), Club.is_active == True).all()]
        if camera_check.club_id not in user_clubs_ids:
            flash('ليس لديك صلاحية الوصول إلى هذا التشيك', 'danger')
            return redirect(url_for('camera_checks.history'))

    return render_template('camera_checks/details.html', camera_check=camera_check, title='تفاصيل تشيك الكاميرات')

@bp.route('/edit/<int:check_id>', methods=['GET', 'POST'])
@login_required
def edit(check_id):
    """
    صفحة تعديل تشيك الكاميرات
    """
    camera_check = CameraCheck.query.get_or_404(check_id)

    # التحقق من أن المستخدم لديه صلاحية الوصول إلى هذا التشيك
    if current_user.role in ['admin', 'manager']:
        # المدير لديه صلاحية الوصول إلى جميع التشيكات
        pass
    else:
        user_clubs_ids = [club.id for club in Club.query.join(Club.users).filter(Club.users.any(id=current_user.id), Club.is_active == True).all()]
        if camera_check.club_id not in user_clubs_ids:
            flash('ليس لديك صلاحية الوصول إلى هذا التشيك', 'danger')
            return redirect(url_for('camera_checks.history'))

    form = CameraCheckForm(obj=camera_check)

    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role in ['admin', 'manager']:
        user_clubs = Club.query.filter(Club.is_active == True).all()
    else:
        user_clubs = Club.query.join(Club.users).filter(Club.users.any(id=current_user.id), Club.is_active == True).all()

    # إضافة خيار افتراضي للقائمة
    form.club_id.choices = [(0, 'اختر النادي')] + [(club.id, club.name) for club in user_clubs]

    if form.validate_on_submit():
        # تحديث بيانات التشيك
        camera_check.opening_check = form.opening_check.data
        camera_check.check_12 = form.check_12.data
        camera_check.check_2 = form.check_2.data
        camera_check.check_3 = form.check_3.data
        camera_check.check_5 = form.check_5.data
        camera_check.check_8 = form.check_8.data
        camera_check.check_10 = form.check_10.data
        camera_check.check_11 = form.check_11.data
        camera_check.check_1150 = form.check_1150.data
        camera_check.violations_count = form.violations_count.data
        camera_check.notes = form.notes.data

        db.session.commit()

        flash('تم تحديث تشيك الكاميرات بنجاح', 'success')
        return redirect(url_for('camera_checks.history'))

    return render_template('camera_checks/edit.html', form=form, camera_check=camera_check, title='تعديل تشيك الكاميرات')
