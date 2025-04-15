import os
import sys

# إضافة المسار الحالي إلى مسار النظام
sys.path.append(os.getcwd())

from app import create_app, db
from app.models.employee import Employee
from app.models.club import Club

app = create_app()
with app.app_context():
    # طباعة عدد الموظفين في كل نادي
    clubs = Club.query.all()
    print("\n=== عدد الموظفين في كل نادي ===")
    for club in clubs:
        employee_count = Employee.query.filter_by(club_id=club.id).count()
        print(f"النادي {club.id} ({club.name}): {employee_count} موظف")

    # طباعة تفاصيل الموظفين في النادي الأول
    print("\n=== تفاصيل الموظفين في النادي الأول ===")
    employees = Employee.query.filter_by(club_id=1).all()
    for i, emp in enumerate(employees[:10]):
        print(f"{i+1}. ID: {emp.id}, الاسم: {emp.name}, النادي: {emp.club_id}")
    if len(employees) > 10:
        print(f"... و{len(employees)-10} موظف آخر")

    # التحقق من وجود موظفين بدون نادي
    print("\n=== الموظفون بدون نادي ===")
    no_club_employees = Employee.query.filter_by(club_id=None).all()
    for i, emp in enumerate(no_club_employees):
        print(f"{i+1}. ID: {emp.id}, الاسم: {emp.name}")
    if not no_club_employees:
        print("لا يوجد موظفون بدون نادي")

    # التحقق من وجود موظفين مكررين
    print("\n=== التحقق من وجود موظفين مكررين ===")
    all_employees = Employee.query.all()
    employee_names = {}
    for emp in all_employees:
        if emp.name in employee_names:
            employee_names[emp.name].append(emp.id)
        else:
            employee_names[emp.name] = [emp.id]

    duplicates = {name: ids for name, ids in employee_names.items() if len(ids) > 1}
    if duplicates:
        print("تم العثور على موظفين مكررين:")
        for name, ids in duplicates.items():
            print(f"الاسم: {name}, المعرفات: {ids}")
            for emp_id in ids:
                emp = Employee.query.get(emp_id)
                print(f"  - ID: {emp.id}, النادي: {emp.club_id}, المسمى: {emp.position}, الدور: {emp.role}")
    else:
        print("لا يوجد موظفون مكررون")
