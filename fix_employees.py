import sqlite3

# اتصال بقاعدة البيانات
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# الحصول على قائمة الموظفين في النادي رقم 1
cursor.execute("SELECT id, name, employee_number, position FROM employee WHERE club_id = 1")
employees = cursor.fetchall()

# طباعة العدد الحالي للموظفين
print(f"عدد الموظفين الحالي في النادي رقم 1: {len(employees)}")

# تحديد الموظفين الذين سيتم الاحتفاظ بهم (أول 19 موظف)
keep_employees = employees[:19]
remove_employees = employees[19:]

# طباعة الموظفين الذين سيتم الاحتفاظ بهم
print(f"\nالموظفين الذين سيتم الاحتفاظ بهم في النادي رقم 1 ({len(keep_employees)}):")
for emp in keep_employees:
    print(f"ID: {emp[0]}, الاسم: {emp[1]}, الرقم الوظيفي: {emp[2]}, المسمى: {emp[3]}")

# طباعة الموظفين الذين سيتم نقلهم
print(f"\nالموظفين الذين سيتم نقلهم من النادي رقم 1 ({len(remove_employees)}):")
for emp in remove_employees:
    print(f"ID: {emp[0]}, الاسم: {emp[1]}, الرقم الوظيفي: {emp[2]}, المسمى: {emp[3]}")

# نقل الموظفين من النادي رقم 1 إلى النادي رقم 3
for emp in remove_employees:
    cursor.execute("UPDATE employee SET club_id = 3 WHERE id = ?", (emp[0],))

# حفظ التغييرات
conn.commit()

# التحقق من العدد الجديد للموظفين
cursor.execute("SELECT COUNT(*) FROM employee WHERE club_id = 1")
new_count = cursor.fetchone()[0]
print(f"\nتم نقل الموظفين بنجاح. عدد الموظفين الجديد في النادي رقم 1: {new_count}")

# إغلاق الاتصال
conn.close()
