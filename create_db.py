from app import create_app, db
from app.models.user import User, Permission
from app.models.club import Club
from app.models.facility import Facility, FacilityCheckItem, FacilityCheck, FacilityCheckResult
from app.models.employee import Employee, WorkRecord
from app.models.issue import Issue
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

def create_db():
    """إنشاء قاعدة البيانات وتهيئتها بالبيانات الأساسية"""
    app = create_app()

    with app.app_context():
        # حذف قاعدة البيانات إذا كانت موجودة
        if os.path.exists('app.db'):
            os.remove('app.db')

        # إنشاء جميع الجداول
        db.create_all()

        # إنشاء المستخدم الأول (المسؤول)
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            name='المسؤول',
            role='admin',
            is_active=True
        )
        db.session.add(admin)

        # إنشاء الصلاحيات
        permissions = [
            {'name': 'clubs', 'description': 'إدارة النوادي'},
            {'name': 'facilities', 'description': 'إدارة المرافق'},
            {'name': 'employees', 'description': 'إدارة الموظفين'},
            {'name': 'issues', 'description': 'إدارة الأعطال'},
            {'name': 'violations', 'description': 'إدارة المخالفات'},
            {'name': 'cameras', 'description': 'فحص الكاميرات'},
            {'name': 'visits', 'description': 'زيارات الفروع'},
            {'name': 'suggestions', 'description': 'الاقتراحات والملاحظات'},
            {'name': 'revenue', 'description': 'الإيرادات'}
        ]

        for perm in permissions:
            permission = Permission(
                name=perm['name'],
                description=perm['description'],
                can_view=True,
                can_create=True,
                can_edit=True,
                can_delete=True
            )
            db.session.add(permission)

        # إنشاء بعض النوادي
        clubs = [
            {'name': 'نادي البديعة', 'manager_name': 'أحمد محمد', 'employee_id': '1001'},
            {'name': 'نادي النهضة', 'manager_name': 'محمد علي', 'employee_id': '1002'},
            {'name': 'نادي الروضة', 'manager_name': 'خالد عبدالله', 'employee_id': '1003'}
        ]

        for club_data in clubs:
            club = Club(
                name=club_data['name'],
                manager_name=club_data['manager_name'],
                employee_id=club_data['employee_id'],
                is_active=True
            )
            db.session.add(club)

        # حفظ التغييرات
        db.session.commit()

        # إنشاء بعض المرافق
        facilities = [
            {'name': 'مسبح', 'club_id': 1, 'is_active': True},
            {'name': 'صالة رياضية', 'club_id': 1, 'is_active': True},
            {'name': 'ملعب كرة قدم', 'club_id': 1, 'is_active': True},
            {'name': 'مسبح', 'club_id': 2, 'is_active': True},
            {'name': 'صالة رياضية', 'club_id': 2, 'is_active': True},
            {'name': 'مسبح', 'club_id': 3, 'is_active': True}
        ]

        for facility_data in facilities:
            facility = Facility(
                name=facility_data['name'],
                club_id=facility_data['club_id'],
                is_active=facility_data['is_active']
            )
            db.session.add(facility)

        # إنشاء بعض الموظفين
        employees = [
            {'employee_number': '1001', 'name': 'أحمد محمد', 'position': 'مدير', 'club_id': 1, 'is_active': True},
            {'employee_number': '1002', 'name': 'محمد علي', 'position': 'مدير', 'club_id': 2, 'is_active': True},
            {'employee_number': '1003', 'name': 'خالد عبدالله', 'position': 'مدير', 'club_id': 3, 'is_active': True},
            {'employee_number': '1004', 'name': 'عبدالرحمن محمد', 'position': 'مشرف', 'club_id': 1, 'is_active': True},
            {'employee_number': '1005', 'name': 'فهد سعد', 'position': 'مشرف', 'club_id': 2, 'is_active': True},
            {'employee_number': '1006', 'name': 'سعد محمد', 'position': 'مشرف', 'club_id': 3, 'is_active': True},
            {'employee_number': '1007', 'name': 'عبدالله خالد', 'position': 'موظف', 'club_id': 1, 'is_active': True},
            {'employee_number': '1008', 'name': 'محمد عبدالله', 'position': 'موظف', 'club_id': 2, 'is_active': True},
            {'employee_number': '1009', 'name': 'خالد محمد', 'position': 'موظف', 'club_id': 3, 'is_active': True}
        ]

        for employee_data in employees:
            employee = Employee(
                employee_number=employee_data['employee_number'],
                name=employee_data['name'],
                position=employee_data['position'],
                department='',
                phone='',
                email='',
                hire_date=None,
                club_id=employee_data['club_id'],
                is_active=employee_data['is_active']
            )
            db.session.add(employee)

        # إنشاء بعض الأعطال
        issues = [
            {'club_id': 1, 'facility_id': 1, 'request_number': 1001, 'request_date': datetime.now().date(), 'due_date': (datetime.now() + timedelta(days=7)).date(), 'status': 'open', 'notes': 'عطل في نظام التدفئة', 'reported_by': 1},
            {'club_id': 1, 'facility_id': 2, 'request_number': 1002, 'request_date': datetime.now().date(), 'due_date': (datetime.now() + timedelta(days=5)).date(), 'status': 'pending', 'notes': 'عطل في نظام التكييف', 'reported_by': 1},
            {'club_id': 2, 'facility_id': 4, 'request_number': 1003, 'request_date': datetime.now().date(), 'due_date': (datetime.now() + timedelta(days=3)).date(), 'status': 'closed', 'notes': 'عطل في نظام الإضاءة', 'reported_by': 1}
        ]

        for issue_data in issues:
            issue = Issue(
                club_id=issue_data['club_id'],
                facility_id=issue_data['facility_id'],
                request_number=issue_data['request_number'],
                request_date=issue_data['request_date'],
                due_date=issue_data['due_date'],
                status=issue_data['status'],
                notes=issue_data['notes'],
                reported_by=issue_data['reported_by'],
                reported_date=datetime.now()
            )
            db.session.add(issue)

        # حفظ التغييرات
        db.session.commit()

        print('تم إنشاء قاعدة البيانات وتهيئتها بنجاح!')

if __name__ == '__main__':
    create_db()
