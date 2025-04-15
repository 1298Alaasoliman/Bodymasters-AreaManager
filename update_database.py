from app import create_app, db
from app.models.facility import FacilityCheck
import sqlite3
import os

def update_database():
    """
    تحديث قاعدة البيانات لإضافة عمود violations_count إلى جدول facility_check
    """
    app = create_app()
    
    with app.app_context():
        # التحقق من وجود ملف قاعدة البيانات
        db_path = os.path.join(os.getcwd(), 'app.db')
        if not os.path.exists(db_path):
            print(f"ملف قاعدة البيانات غير موجود في المسار: {db_path}")
            return
        
        print(f"تم العثور على ملف قاعدة البيانات في المسار: {db_path}")
        
        # الاتصال بقاعدة البيانات مباشرة باستخدام sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود عمود violations_count في جدول facility_check
        cursor.execute("PRAGMA table_info(facility_check)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'violations_count' not in column_names:
            print("إضافة عمود violations_count إلى جدول facility_check...")
            try:
                cursor.execute("ALTER TABLE facility_check ADD COLUMN violations_count INTEGER DEFAULT 0")
                conn.commit()
                print("تم إضافة العمود بنجاح!")
            except Exception as e:
                print(f"حدث خطأ أثناء إضافة العمود: {str(e)}")
        else:
            print("العمود violations_count موجود بالفعل في جدول facility_check")
        
        # إغلاق الاتصال
        conn.close()
        
        print("تم الانتهاء من تحديث قاعدة البيانات")

if __name__ == "__main__":
    update_database()
