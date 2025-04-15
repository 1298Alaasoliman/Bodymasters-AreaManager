from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.shomoos import Shomoos
from datetime import datetime

bp = Blueprint('shomoos', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض صفحة شموس الرئيسية
    """
    clubs = Club.query.all()

    # الحصول على معرف النادي من معلمات الاستعلام للفلترة
    filter_club_id = request.args.get('club_id', type=int)

    # بناء الاستعلام الأساسي
    query = Shomoos.query

    # تحديد النوادي التي يمكن للمستخدم الوصول إليها
    if current_user.role != 'admin':
        accessible_clubs = [club for club in clubs if current_user.has_club_access(club.id)]
        accessible_club_ids = [club.id for club in accessible_clubs]
        query = query.filter(Shomoos.club_id.in_(accessible_club_ids))

    # تطبيق فلتر النادي إذا تم تحديده
    if filter_club_id:
        query = query.filter(Shomoos.club_id == filter_club_id)

    # ترتيب النتائج والحصول عليها
    records = query.order_by(Shomoos.created_at.desc()).all()

    return render_template('shomoos/index.html',
                           clubs=clubs,
                           records=records,
                           filter_club_id=filter_club_id,
                           title='شموس')

@bp.route('/add', methods=['POST'])
@login_required
def add():
    """
    إضافة سجل شموس جديد
    """
    try:
        club_id = request.form.get('club_id')
        current_number = request.form.get('current_number')

        # التحقق من البيانات
        if not club_id or not current_number:
            flash('يرجى إدخال جميع البيانات المطلوبة', 'danger')
            return redirect(url_for('shomoos.index'))

        # تحويل القيم إلى أرقام
        try:
            club_id = int(club_id)
            current_number = int(current_number)
        except ValueError:
            flash('قيمة غير صحيحة', 'danger')
            return redirect(url_for('shomoos.index'))

        # التحقق من صلاحية الوصول إلى النادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
            return redirect(url_for('shomoos.index'))

        # الحصول على آخر سجل للنادي لحساب الفارق
        last_record = Shomoos.query.filter_by(club_id=club_id).order_by(Shomoos.created_at.desc()).first()
        previous_number = last_record.new_number if last_record else 0
        difference = current_number - previous_number

        # إنشاء سجل جديد
        record = Shomoos(
            club_id=club_id,
            new_number=current_number,
            previous_total=difference,
            total=current_number
        )

        db.session.add(record)
        db.session.commit()

        flash('تم إضافة السجل بنجاح', 'success')
        return redirect(url_for('shomoos.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('shomoos.index'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    تعديل سجل شموس
    """
    record = Shomoos.query.get_or_404(id)
    clubs = Club.query.all()

    # التحقق من صلاحية الوصول إلى النادي
    if current_user.role != 'admin' and not current_user.has_club_access(record.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('shomoos.index'))

    if request.method == 'POST':
        try:
            # الحصول على البيانات من الطلب
            club_id = request.form.get('club_id')
            current_number = request.form.get('current_number')

            # التحقق من البيانات
            if not club_id or not current_number:
                flash('يرجى إدخال جميع البيانات المطلوبة', 'danger')
                return render_template('shomoos/edit.html', record=record, clubs=clubs, title='تعديل سجل شموس')

            # تحويل القيم إلى أرقام
            try:
                club_id = int(club_id)
                current_number = int(current_number)
            except ValueError:
                flash('قيمة غير صحيحة', 'danger')
                return render_template('shomoos/edit.html', record=record, clubs=clubs, title='تعديل سجل شموس')

            # الحصول على آخر سجل للنادي لحساب الفارق
            last_record = Shomoos.query.filter_by(club_id=club_id).filter(Shomoos.id != id).order_by(Shomoos.created_at.desc()).first()
            previous_number = last_record.new_number if last_record else 0
            difference = current_number - previous_number

            # تحديث السجل
            record.club_id = club_id
            record.new_number = current_number
            record.previous_total = difference
            record.total = current_number
            record.updated_at = datetime.now()

            db.session.commit()

            flash('تم تحديث السجل بنجاح', 'success')
            return redirect(url_for('shomoos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
            return render_template('shomoos/edit.html', record=record, clubs=clubs, title='تعديل سجل شموس')

    # GET request
    return render_template('shomoos/edit.html', record=record, clubs=clubs, title='تعديل سجل شموس')

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """
    حذف سجل شموس
    """
    record = Shomoos.query.get_or_404(id)

    # التحقق من صلاحية الوصول إلى النادي
    if current_user.role != 'admin' and not current_user.has_club_access(record.club_id):
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('shomoos.index'))

    try:
        db.session.delete(record)
        db.session.commit()
        flash('تم حذف السجل بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')

    return redirect(url_for('shomoos.index'))

@bp.route('/get_last_number/<int:club_id>')
@login_required
def get_last_number(club_id):
    """
    الحصول على آخر رقم للنادي
    """
    last_record = Shomoos.query.filter_by(club_id=club_id).order_by(Shomoos.created_at.desc()).first()

    if last_record:
        return jsonify({'current_number': last_record.new_number})
    else:
        return jsonify({'current_number': 0})
