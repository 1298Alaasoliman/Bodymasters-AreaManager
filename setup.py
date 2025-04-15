import os
import sys
import click
from getpass import getpass
from app import create_app, db
from app.models import User, Permission, RevenueCategory, ViolationType, ActionType

app = create_app()

def setup_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    with app.app_context():
        db.create_all()
        print("تم إنشاء قاعدة البيانات بنجاح")

def create_admin():
    """إنشاء مستخدم مسؤول جديد"""
    with app.app_context():
        # التحقق من وجود مستخدمين مسؤولين
        admin_exists = User.query.filter_by(role='admin').first()
        if admin_exists:
            if not click.confirm("يوجد مستخدم مسؤول بالفعل. هل تريد إنشاء مستخدم مسؤول جديد؟"):
                return
        
        # جمع بيانات المستخدم المسؤول
        username = input("اسم المستخدم: ")
        email = input("البريد الإلكتروني: ")
        employee_number = input("الرقم الوظيفي: ")
        password = getpass("كلمة المرور: ")
        password_confirm = getpass("تأكيد كلمة المرور: ")
        
        # التحقق من تطابق كلمات المرور
        if password != password_confirm:
            print("خطأ: كلمات المرور غير متطابقة")
            return
        
        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print("خطأ: اسم المستخدم موجود بالفعل")
            return
        
        # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print("خطأ: البريد الإلكتروني موجود بالفعل")
            return
        
        # التحقق من عدم وجود مستخدم بنفس الرقم الوظيفي
        existing_employee = User.query.filter_by(employee_number=employee_number).first()
        if existing_employee:
            print("خطأ: الرقم الوظيفي موجود بالفعل")
            return
        
        # إنشاء المستخدم المسؤول
        user = User(
            username=username,
            email=email,
            employee_number=employee_number,
            role='admin',
            is_active=True
        )
        user.set_password(password)
        
        # إضافة المستخدم إلى قاعدة البيانات
        db.session.add(user)
        db.session.commit()
        
        print(f"تم إنشاء المستخدم المسؤول {username} بنجاح")

def init_data():
    """تهيئة البيانات الأساسية"""
    with app.app_context():
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
            {'name': 'revenue', 'description': 'إدارة الإيرادات'}
        ]
        
        for perm_data in permissions:
            # التحقق من عدم وجود الصلاحية مسبقًا
            existing = Permission.query.filter_by(name=perm_data['name']).first()
            if not existing:
                permission = Permission(
                    name=perm_data['name'],
                    description=perm_data['description'],
                    can_view=True,
                    can_create=False,
                    can_edit=False,
                    can_delete=False
                )
                db.session.add(permission)
        
        # إنشاء فئات الإيرادات
        revenue_categories = [
            {'name': 'اشتراكات', 'description': 'إيرادات الاشتراكات الشهرية والسنوية'},
            {'name': 'منتجات', 'description': 'إيرادات بيع المنتجات'},
            {'name': 'خدمات إضافية', 'description': 'إيرادات الخدمات الإضافية'},
            {'name': 'تأجير مرافق', 'description': 'إيرادات تأجير المرافق'},
            {'name': 'أخرى', 'description': 'إيرادات أخرى'}
        ]
        
        for cat_data in revenue_categories:
            # التحقق من عدم وجود الفئة مسبقًا
            existing = RevenueCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = RevenueCategory(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
        
        # إنشاء أنواع المخالفات
        violation_types = [
            {'name': 'تأخير', 'description': 'التأخر عن موعد العمل', 'severity': 'low'},
            {'name': 'غياب', 'description': 'الغياب بدون إذن', 'severity': 'medium'},
            {'name': 'إهمال', 'description': 'إهمال في العمل', 'severity': 'medium'},
            {'name': 'سلوك', 'description': 'سلوك غير لائق', 'severity': 'high'},
            {'name': 'مخالفة أنظمة', 'description': 'مخالفة أنظمة العمل', 'severity': 'high'}
        ]
        
        for vt_data in violation_types:
            # التحقق من عدم وجود نوع المخالفة مسبقًا
            existing = ViolationType.query.filter_by(name=vt_data['name']).first()
            if not existing:
                violation_type = ViolationType(
                    name=vt_data['name'],
                    description=vt_data['description'],
                    severity=vt_data['severity']
                )
                db.session.add(violation_type)
        
        # إنشاء أنواع الإجراءات
        action_types = [
            {'name': 'تنبيه شفهي', 'description': 'تنبيه شفهي للموظف'},
            {'name': 'إنذار كتابي', 'description': 'إنذار كتابي للموظف'},
            {'name': 'خصم', 'description': 'خصم من الراتب'},
            {'name': 'إيقاف مؤقت', 'description': 'إيقاف مؤقت عن العمل'},
            {'name': 'فصل', 'description': 'فصل من العمل'}
        ]
        
        for at_data in action_types:
            # التحقق من عدم وجود نوع الإجراء مسبقًا
            existing = ActionType.query.filter_by(name=at_data['name']).first()
            if not existing:
                action_type = ActionType(
                    name=at_data['name'],
                    description=at_data['description']
                )
                db.session.add(action_type)
        
        # حفظ التغييرات
        db.session.commit()
        
        print("تم تهيئة البيانات الأساسية بنجاح")

def main():
    """الدالة الرئيسية"""
    print("=== إعداد نظام إدارة النوادي الرياضية ===")
    
    # تهيئة قاعدة البيانات
    if click.confirm("هل تريد تهيئة قاعدة البيانات؟"):
        setup_database()
    
    # تهيئة البيانات الأساسية
    if click.confirm("هل تريد تهيئة البيانات الأساسية؟"):
        init_data()
    
    # إنشاء مستخدم مسؤول
    if click.confirm("هل تريد إنشاء مستخدم مسؤول؟"):
        create_admin()
    
    print("تم الإعداد بنجاح!")

if __name__ == '__main__':
    main()
