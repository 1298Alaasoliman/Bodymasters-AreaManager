from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.revenue import MonthlyTarget, DailyRevenue
from app.forms.revenue import MonthlyTargetForm, DailyRevenueForm
from datetime import datetime, date
import calendar

bp = Blueprint('daily_revenue', __name__)

@bp.route('/')
@login_required
def index():
    """
    صفحة الإيرادات الرئيسية
    """
    # الحصول على الشهر والسنة الحالية
    current_month = date.today().month
    current_year = date.today().year

    # الحصول على الأندية التي يمكن للمستخدم الوصول إليها
    if current_user.role == 'admin':
        user_clubs = Club.query.filter_by(is_active=True).all()
    else:
        user_clubs = current_user.clubs

    # الحصول على التارجت الشهري لكل نادي
    club_targets = {}
    club_revenues = {}
    club_percentages = {}
    club_remaining = {}

    total_target = 0
    total_revenue = 0

    for club in user_clubs:
        # البحث عن التارجت الشهري للنادي
        target = MonthlyTarget.query.filter_by(
            club_id=club.id,
            month=current_month,
            year=current_year
        ).first()

        if target:
            target_amount = target.target_amount
        else:
            target_amount = 0

        # حساب الإيرادات الشهرية للنادي
        start_date = date(current_year, current_month, 1)
        if current_month == 12:
            end_month = 1
            end_year = current_year + 1
        else:
            end_month = current_month + 1
            end_year = current_year

        end_date = date(end_year, end_month, 1)

        revenues = DailyRevenue.query.filter(
            DailyRevenue.club_id == club.id,
            DailyRevenue.date >= start_date,
            DailyRevenue.date < end_date
        ).all()

        revenue_amount = sum(rev.amount for rev in revenues)

        # حساب النسبة المئوية والمبلغ المتبقي
        if target_amount > 0:
            percentage = (revenue_amount / target_amount) * 100
            remaining = target_amount - revenue_amount
        else:
            percentage = 0
            remaining = 0

        club_targets[club.id] = target_amount
        club_revenues[club.id] = revenue_amount
        club_percentages[club.id] = percentage
        club_remaining[club.id] = remaining

        total_target += target_amount
        total_revenue += revenue_amount

    # حساب النسبة المئوية الإجمالية والمبلغ المتبقي الإجمالي
    if total_target > 0:
        total_percentage = (total_revenue / total_target) * 100
        total_remaining = total_target - total_revenue
    else:
        total_percentage = 0
        total_remaining = 0

    # الحصول على اسم الشهر الحالي بالعربية
    months_ar = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
    current_month_name = months_ar[current_month - 1]

    return render_template('daily_revenue/index.html',
                           title='الإيرادات اليومية',
                           user_clubs=user_clubs,
                           club_targets=club_targets,
                           club_revenues=club_revenues,
                           club_percentages=club_percentages,
                           club_remaining=club_remaining,
                           total_target=total_target,
                           total_revenue=total_revenue,
                           total_percentage=total_percentage,
                           total_remaining=total_remaining,
                           current_month=current_month,
                           current_year=current_year,
                           current_month_name=current_month_name)

@bp.route('/target/create', methods=['GET', 'POST'])
@login_required
def create_target():
    """
    إنشاء تارجت شهري جديد
    """
    form = MonthlyTargetForm()

    # تعبئة قائمة الأندية
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    form.club_id.choices = [(club.id, club.name) for club in clubs]

    if form.validate_on_submit():
        # التحقق من وجود تارجت للنادي في نفس الشهر والسنة
        existing_target = MonthlyTarget.query.filter_by(
            club_id=form.club_id.data,
            month=form.month.data,
            year=form.year.data
        ).first()

        # تحويل السنة من نص إلى رقم
        try:
            year_value = int(form.year.data)
            if year_value < 2020 or year_value > 2100:
                flash(f'يجب أن تكون السنة بين 2020 و 2100', 'danger')
                return render_template('daily_revenue/create_target.html',
                                   title='إنشاء تارجت شهري',
                                   form=form,
                                   targets=targets,
                                   months_en=months_en)
        except ValueError:
            flash(f'يرجى إدخال سنة صحيحة', 'danger')
            return render_template('daily_revenue/create_target.html',
                               title='إنشاء تارجت شهري',
                               form=form,
                               targets=targets,
                               months_en=months_en)

        if existing_target:
            # تحديث التارجت الموجود
            existing_target.target_amount = form.target_amount.data
            db.session.commit()
            flash(f'تم تحديث التارجت الشهري بنجاح', 'success')
        else:
            # إنشاء تارجت جديد
            target = MonthlyTarget(
                club_id=form.club_id.data,
                month=form.month.data,
                year=year_value,
                target_amount=form.target_amount.data,
                created_by=current_user.id
            )
            db.session.add(target)
            db.session.commit()
            flash(f'تم إنشاء التارجت الشهري بنجاح', 'success')

        return redirect(url_for('daily_revenue.index'))

    # الحصول على قائمة التارجت المسجلة (فقط للأندية التي يمكن للمستخدم الوصول إليها)
    if current_user.role == 'admin':
        # المسؤول يمكنه رؤية جميع التارجت
        targets = db.session.query(
            MonthlyTarget, Club.name.label('club_name')
        ).join(
            Club, MonthlyTarget.club_id == Club.id
        ).order_by(
            MonthlyTarget.year.desc(),
            MonthlyTarget.month.desc(),
            Club.name
        ).all()
    else:
        # المستخدم العادي يرى فقط التارجت الخاصة بالأندية المتاحة له
        user_club_ids = [club.id for club in current_user.clubs]
        targets = db.session.query(
            MonthlyTarget, Club.name.label('club_name')
        ).join(
            Club, MonthlyTarget.club_id == Club.id
        ).filter(
            MonthlyTarget.club_id.in_(user_club_ids)
        ).order_by(
            MonthlyTarget.year.desc(),
            MonthlyTarget.month.desc(),
            Club.name
        ).all()

    # الحصول على أسماء الشهور بالإنجليزية
    months_en = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    return render_template('daily_revenue/create_target.html',
                           title='إنشاء تارجت شهري',
                           form=form,
                           targets=targets,
                           months_en=months_en)

@bp.route('/revenue/create', methods=['GET', 'POST'])
@bp.route('/revenue/edit/<int:revenue_id>', methods=['GET', 'POST'])
@login_required
def create_revenue(revenue_id=None):
    """
    إنشاء أو تعديل إيراد يومي
    """
    form = DailyRevenueForm()

    # تعبئة قائمة الأندية
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    form.club_id.choices = [(club.id, club.name) for club in clubs]

    # إذا كان تعديل لإيراد موجود
    revenue_to_edit = None
    if revenue_id:
        revenue_to_edit = DailyRevenue.query.get_or_404(revenue_id)

        # التحقق من صلاحية الوصول
        if current_user.role != 'admin' and revenue_to_edit.club_id not in [club.id for club in current_user.clubs]:
            flash('ليس لديك صلاحية لتعديل هذا الإيراد', 'danger')
            return redirect(url_for('daily_revenue.index'))

        # ملء النموذج ببيانات الإيراد الحالي
        if request.method == 'GET':
            form.club_id.data = revenue_to_edit.club_id
            form.date.data = revenue_to_edit.date
            form.amount.data = revenue_to_edit.amount

    if form.validate_on_submit():
        # التحقق من أن التاريخ لا يكون أكبر من تاريخ اليوم
        today = date.today()
        if form.date.data > today:
            flash(f'لا يمكن تسجيل إيراد بتاريخ مستقبلي', 'danger')
            return render_template('daily_revenue/create_revenue_fixed.html',
                               title='إنشاء إيراد يومي',
                               form=form)

        # إذا كان تعديل لإيراد موجود
        if revenue_id and revenue_to_edit:
            # التحقق من وجود إيراد آخر لنفس النادي ونفس التاريخ
            if revenue_to_edit.club_id != form.club_id.data or revenue_to_edit.date != form.date.data:
                existing_revenue = DailyRevenue.query.filter_by(
                    club_id=form.club_id.data,
                    date=form.date.data
                ).first()

                if existing_revenue and existing_revenue.id != revenue_id:
                    flash(f'يوجد بالفعل إيراد مسجل لهذا النادي في نفس التاريخ', 'danger')
                    return render_template('daily_revenue/create_revenue_fixed.html',
                                   title='تعديل إيراد يومي',
                                   form=form)

            # تحديث الإيراد الموجود
            revenue_to_edit.club_id = form.club_id.data
            revenue_to_edit.date = form.date.data
            revenue_to_edit.amount = form.amount.data
            db.session.commit()
            flash(f'تم تحديث الإيراد اليومي بنجاح', 'success')

            # العودة إلى صفحة تفاصيل النادي
            return redirect(url_for('daily_revenue.club_details', club_id=form.club_id.data))
        else:
            # التحقق من وجود إيراد للنادي في نفس اليوم
            existing_revenue = DailyRevenue.query.filter_by(
                club_id=form.club_id.data,
                date=form.date.data
            ).first()

            if existing_revenue:
                # تحديث الإيراد الموجود
                existing_revenue.amount = form.amount.data
                db.session.commit()
                flash(f'تم تحديث الإيراد اليومي بنجاح', 'success')
            else:
                # إنشاء إيراد جديد
                revenue = DailyRevenue(
                    club_id=form.club_id.data,
                    date=form.date.data,
                    amount=form.amount.data,
                    notes='',
                    recorded_by=current_user.id
                )
                db.session.add(revenue)
                db.session.commit()
                flash(f'تم إنشاء الإيراد اليومي بنجاح', 'success')

            return redirect(url_for('daily_revenue.index'))

    # تحديد عنوان الصفحة بناءً على ما إذا كانت إنشاء أو تعديل
    title = 'تعديل إيراد يومي' if revenue_id else 'إنشاء إيراد يومي'

    return render_template('daily_revenue/create_revenue_fixed.html',
                           title=title,
                           form=form,
                           revenue_id=revenue_id)

@bp.route('/club/<int:club_id>')
@login_required
def club_details(club_id):
    """
    تفاصيل إيرادات النادي
    """
    club = Club.query.get_or_404(club_id)

    # التحقق من صلاحية الوصول
    if current_user.role != 'admin' and club not in current_user.clubs:
        flash('ليس لديك صلاحية للوصول إلى هذا النادي', 'danger')
        return redirect(url_for('daily_revenue.index'))

    # الحصول على الشهر والسنة الحالية
    current_month = date.today().month
    current_year = date.today().year

    # البحث عن التارجت الشهري للنادي
    target = MonthlyTarget.query.filter_by(
        club_id=club.id,
        month=current_month,
        year=current_year
    ).first()

    if target:
        target_amount = target.target_amount
    else:
        target_amount = 0

    # حساب الإيرادات الشهرية للنادي
    start_date = date(current_year, current_month, 1)
    if current_month == 12:
        end_month = 1
        end_year = current_year + 1
    else:
        end_month = current_month + 1
        end_year = current_year

    end_date = date(end_year, end_month, 1)

    revenues = DailyRevenue.query.filter(
        DailyRevenue.club_id == club.id,
        DailyRevenue.date >= start_date,
        DailyRevenue.date < end_date
    ).order_by(DailyRevenue.date.desc()).all()

    revenue_amount = sum(rev.amount for rev in revenues)

    # حساب النسبة المئوية والمبلغ المتبقي
    if target_amount > 0:
        percentage = (revenue_amount / target_amount) * 100
        remaining = target_amount - revenue_amount
    else:
        percentage = 0
        remaining = 0

    # حساب مستويات التارجت
    target_levels = {}
    if target_amount > 0:
        for level in [70, 80, 90, 100, 110, 120]:
            level_amount = (target_amount * level) / 100
            level_remaining = level_amount - revenue_amount
            daily_required = 0

            # حساب المطلوب يومياً
            today = date.today()
            if today.month == current_month and today.year == current_year:
                days_in_month = calendar.monthrange(current_year, current_month)[1]
                remaining_days = days_in_month - today.day + 1
                if remaining_days > 0 and level_remaining > 0:
                    daily_required = level_remaining / remaining_days

            target_levels[level] = {
                'amount': level_amount,
                'remaining': level_remaining,
                'daily_required': daily_required
            }

    # الحصول على اسم الشهر الحالي بالعربية
    months_ar = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
    current_month_name = months_ar[current_month - 1]

    return render_template('daily_revenue/club_details.html',
                           title=f'إيرادات {club.name}',
                           club=club,
                           target_amount=target_amount,
                           revenue_amount=revenue_amount,
                           percentage=percentage,
                           remaining=remaining,
                           revenues=revenues,
                           target_levels=target_levels,
                           current_month=current_month,
                           current_year=current_year,
                           current_month_name=current_month_name)
