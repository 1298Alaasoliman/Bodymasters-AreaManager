from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()
with app.app_context():
    # محاولة تسجيل الدخول باسم المستخدم admin
    username = 'admin'
    password = 'admin'
    
    # البحث عن المستخدم
    user = User.query.filter_by(username=username).first()
    
    if user is None:
        print(f"لم يتم العثور على مستخدم باسم {username}")
    else:
        print(f"تم العثور على المستخدم: {user.username}")
        
        # التحقق من كلمة المرور
        if user.check_password(password):
            print("كلمة المرور صحيحة")
            
            # التحقق من حالة المستخدم
            if user.is_active:
                print("المستخدم نشط ويمكنه تسجيل الدخول")
            else:
                print("المستخدم غير نشط")
        else:
            print("كلمة المرور غير صحيحة")
            
            # التحقق من كلمة المرور المخزنة
            print(f"كلمة المرور المخزنة: {user.password_hash}")
            
            # التحقق من كلمة المرور باستخدام check_password_hash مباشرة
            direct_check = check_password_hash(user.password_hash, password)
            print(f"التحقق المباشر من كلمة المرور: {direct_check}")
            
            # تجربة كلمات مرور أخرى
            test_passwords = ['password', 'admin123', 'Admin', 'ADMIN']
            for test_pass in test_passwords:
                result = user.check_password(test_pass)
                print(f"هل كلمة المرور '{test_pass}' صحيحة؟ {result}")
