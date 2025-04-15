from app import create_app, db
from app.models.user import DetailedPermission

app = create_app()

def create_detailed_permissions_table():
    """إنشاء جدول الصلاحيات التفصيلية"""
    with app.app_context():
        # إنشاء الجدول إذا لم يكن موجوداً
        db.create_all()
        print("تم إنشاء جدول الصلاحيات التفصيلية بنجاح!")

if __name__ == '__main__':
    create_detailed_permissions_table()
