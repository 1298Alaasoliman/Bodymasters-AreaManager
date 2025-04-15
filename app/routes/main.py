from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.club import Club
from app.models.employee import Employee
from app.models.issue import Issue
from app.models.revenue import DailyRevenue
from datetime import date

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """
    الصفحة الرئيسية / لوحة التحكم
    """
    # الأندية التي يمكن للمستخدم الوصول إليها
    if current_user.role == 'admin':
        user_clubs = Club.query.filter_by(is_active=True).all()
        # عدد الأندية النشطة
        clubs_count = len(user_clubs)

        # عدد الموظفين النشطين
        employees_count = Employee.query.filter_by(is_active=True).count()

        # عدد الأعطال المفتوحة
        open_issues = Issue.query.filter_by(status='open').count()

        # عدد الأعطال الحرجة (المتأخرة)
        today = date.today()
        critical_issues = Issue.query.filter(Issue.status != 'closed', Issue.due_date < today).count()
    else:
        # الأندية التي يمكن للمستخدم الوصول إليها
        user_clubs = current_user.clubs
        # عدد الأندية النشطة التي يمكن للمستخدم الوصول إليها
        clubs_count = len([club for club in user_clubs if club.is_active])

        # الحصول على قائمة معرفات الأندية التي يمكن للمستخدم الوصول إليها
        user_club_ids = [club.id for club in user_clubs]

        # عدد الموظفين النشطين في الأندية التي يمكن للمستخدم الوصول إليها
        employees_count = Employee.query.filter(Employee.is_active == True, Employee.club_id.in_(user_club_ids)).count()

        # عدد الأعطال المفتوحة في الأندية التي يمكن للمستخدم الوصول إليها
        open_issues = Issue.query.filter(Issue.status == 'open', Issue.club_id.in_(user_club_ids)).count()

        # عدد الأعطال الحرجة (المتأخرة) في الأندية التي يمكن للمستخدم الوصول إليها
        today = date.today()
        critical_issues = Issue.query.filter(Issue.status != 'closed', Issue.due_date < today, Issue.club_id.in_(user_club_ids)).count()

    # حساب إيرادات الشهر الحالي
    current_month = date.today().month
    current_year = date.today().year

    # تحديد بداية ونهاية الشهر الحالي
    start_date = date(current_year, current_month, 1)
    if current_month == 12:
        end_month = 1
        end_year = current_year + 1
    else:
        end_month = current_month + 1
        end_year = current_year
    end_date = date(end_year, end_month, 1)

    # حساب إجمالي الإيرادات للشهر الحالي
    current_month_revenue = 0

    if current_user.role == 'admin':
        # للمسؤول: جميع الإيرادات لجميع الأندية
        revenues = DailyRevenue.query.filter(
            DailyRevenue.date >= start_date,
            DailyRevenue.date < end_date
        ).all()
        current_month_revenue = sum(rev.amount for rev in revenues)
    else:
        # للمستخدم العادي: الإيرادات للأندية التي يمكنه الوصول إليها
        user_club_ids = [club.id for club in user_clubs]
        revenues = DailyRevenue.query.filter(
            DailyRevenue.date >= start_date,
            DailyRevenue.date < end_date,
            DailyRevenue.club_id.in_(user_club_ids)
        ).all()
        current_month_revenue = sum(rev.amount for rev in revenues)

    # تنسيق الرقم لعرضه بشكل مناسب
    formatted_revenue = "{:,.0f}".format(current_month_revenue)

    return render_template('index.html',
                           title='لوحة التحكم',
                           clubs_count=clubs_count,
                           open_issues=open_issues,
                           critical_issues=critical_issues,
                           employees_count=employees_count,
                           current_month_revenue=formatted_revenue,
                           user_clubs=user_clubs)

@bp.route('/about')
def about():
    """
    صفحة حول التطبيق
    """
    return render_template('about.html', title='حول التطبيق')
