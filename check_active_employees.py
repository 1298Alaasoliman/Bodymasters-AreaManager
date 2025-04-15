from app import create_app
from app.models import Employee, Club

app = create_app()
with app.app_context():
    club_id = 1
    club = Club.query.get(club_id)
    if not club:
        print(f"النادي رقم {club_id} غير موجود")
        exit()
    
    print(f"النادي: {club.name}")
    
    # الحصول على الموظفين النشطين حسب المسمى الوظيفي
    admin_employees = Employee.query.filter_by(club_id=club_id, position='خدمة عملاء', is_active=True).all()
    trainer_employees = Employee.query.filter_by(club_id=club_id, position='مدرب', is_active=True).all()
    worker_employees = Employee.query.filter_by(club_id=club_id, position='عامل', is_active=True).all()
    
    print(f"عدد موظفي خدمة العملاء النشطين: {len(admin_employees)}")
    print(f"عدد المدربين النشطين: {len(trainer_employees)}")
    print(f"عدد العمال النشطين: {len(worker_employees)}")
    print(f"إجمالي عدد الموظفين النشطين: {len(admin_employees) + len(trainer_employees) + len(worker_employees)}")
    
    # عرض جميع الموظفين
    all_active_employees = Employee.query.filter_by(club_id=club_id, is_active=True).all()
    all_inactive_employees = Employee.query.filter_by(club_id=club_id, is_active=False).all()
    
    print(f"إجمالي عدد الموظفين النشطين في النادي: {len(all_active_employees)}")
    print(f"إجمالي عدد الموظفين غير النشطين في النادي: {len(all_inactive_employees)}")
    
    # عرض عدد الموظفين النشطين لكل نادي
    clubs = Club.query.all()
    for c in clubs:
        active_count = Employee.query.filter_by(club_id=c.id, is_active=True).count()
        inactive_count = Employee.query.filter_by(club_id=c.id, is_active=False).count()
        print(f"النادي: {c.name}, عدد الموظفين النشطين: {active_count}, عدد الموظفين غير النشطين: {inactive_count}")
