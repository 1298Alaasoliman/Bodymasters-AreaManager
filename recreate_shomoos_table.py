import sqlite3
import os

# التأكد من وجود قاعدة البيانات
if not os.path.exists('app.db'):
    print("قاعدة البيانات غير موجودة")
    exit()

# فتح اتصال بقاعدة البيانات
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# حذف جدول Shomoos إذا كان موجودًا
cursor.execute("DROP TABLE IF EXISTS shomoos")

# إنشاء جدول Shomoos من جديد
cursor.execute("""
CREATE TABLE shomoos (
    id INTEGER NOT NULL, 
    club_id INTEGER, 
    current_number INTEGER, 
    difference INTEGER, 
    created_at DATETIME, 
    updated_at DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(club_id) REFERENCES club (id)
)
""")

# حفظ التغييرات
conn.commit()

# إغلاق الاتصال
conn.close()

print("تم إعادة إنشاء جدول Shomoos بنجاح")
