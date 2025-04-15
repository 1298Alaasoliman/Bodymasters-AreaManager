from app import db, create_app

app = create_app()

with app.app_context():
    # إعادة إنشاء جميع الجداول
    db.drop_all()
    db.create_all()
    print("تم إعادة إنشاء قاعدة البيانات بنجاح!")
