from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # البحث عن مستخدم admin
    admin_user = User.query.filter_by(username='admin').first()
    
    if admin_user:
        print(f"تم العثور على مستخدم admin:")
        print(f"ID: {admin_user.id}")
        print(f"اسم المستخدم: {admin_user.username}")
        print(f"البريد الإلكتروني: {admin_user.email}")
        print(f"الرقم الوظيفي: {admin_user.employee_number}")
        print(f"الدور: {admin_user.role}")
        print(f"نشط: {admin_user.is_active}")
        print(f"تاريخ الإنشاء: {admin_user.created_at}")
        print(f"آخر تسجيل دخول: {admin_user.last_login}")
        
        # التحقق من كلمة المرور
        test_password = 'admin'
        password_check = admin_user.check_password(test_password)
        print(f"هل كلمة المرور '{test_password}' صحيحة؟ {password_check}")
    else:
        print("لم يتم العثور على مستخدم admin")
        
    # عرض جميع المستخدمين
    print("\nجميع المستخدمين:")
    all_users = User.query.all()
    for user in all_users:
        print(f"ID: {user.id}, اسم المستخدم: {user.username}, الدور: {user.role}, نشط: {user.is_active}")
