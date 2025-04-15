from app import create_app, db
from app.models import User, Club

app = create_app()
with app.app_context():
    # الحصول على المستخدم
    user = User.query.get(1)  # استخدم معرف المستخدم الذي تريد تعديله
    if not user:
        print("المستخدم غير موجود")
        exit()
    
    print(f"المستخدم: {user.username}")
    print(f"عدد الأندية الحالية: {len(user.clubs)}")
    
    # الحصول على بعض الأندية
    clubs = Club.query.limit(5).all()
    if not clubs:
        print("لا توجد أندية")
        exit()
    
    # إضافة الأندية للمستخدم
    for club in clubs:
        if club not in user.clubs:
            user.clubs.append(club)
            print(f"تمت إضافة النادي: {club.name}")
    
    # حفظ التغييرات
    db.session.commit()
    
    # التحقق من الأندية بعد الإضافة
    print(f"عدد الأندية بعد الإضافة: {len(user.clubs)}")
    for club in user.clubs:
        print(f"النادي: {club.name}, المعرف: {club.id}")
