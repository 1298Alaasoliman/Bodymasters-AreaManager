from app import create_app, db
from app.models.user import User, Permission

app = create_app()

with app.app_context():
    # الحصول على صلاحية الأعطال
    issues_permission = Permission.query.filter_by(name='issues').first()
    
    if not issues_permission:
        print("صلاحية الأعطال غير موجودة. جاري إنشاؤها...")
        issues_permission = Permission(
            name='issues',
            description='إدارة الأعطال',
            can_view=True,
            can_create=True,
            can_edit=True,
            can_delete=True
        )
        db.session.add(issues_permission)
        db.session.commit()
        print("تم إنشاء صلاحية الأعطال بنجاح.")
    
    # الحصول على جميع المستخدمين
    users = User.query.filter_by(role='user').all()
    
    # إضافة صلاحية الأعطال لجميع المستخدمين
    for user in users:
        if issues_permission not in user.permissions:
            user.permissions.append(issues_permission)
            print(f"تمت إضافة صلاحية الأعطال للمستخدم: {user.username}")
    
    # حفظ التغييرات
    db.session.commit()
    
    print("تم الانتهاء من إضافة صلاحية الأعطال لجميع المستخدمين.")
