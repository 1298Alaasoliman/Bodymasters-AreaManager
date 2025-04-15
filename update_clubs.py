from app import create_app, db
from app.models import Club
from sqlalchemy import text

app = create_app()
with app.app_context():
    # تحديث قاعدة البيانات
    try:
        db.session.execute(text('ALTER TABLE club ADD COLUMN expected_employees_count INTEGER DEFAULT 13'))
        db.session.commit()
        print("تم إضافة الحقل الجديد بنجاح")
    except Exception as e:
        print(f"حدث خطأ عند إضافة الحقل: {e}")
        db.session.rollback()

    try:
        # تحديث قيم العدد المتوقع للموظفين لكل نادي
        clubs = Club.query.all()
        for club in clubs:
            club.expected_employees_count = 13  # القيمة الافتراضية

        # حفظ التغييرات
        db.session.commit()
        print("تم تحديث جميع الأندية بنجاح")
    except Exception as e:
        print(f"حدث خطأ عند تحديث الأندية: {e}")
        db.session.rollback()
