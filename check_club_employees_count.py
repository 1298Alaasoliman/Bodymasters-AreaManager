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
    
    # الحصول على الموظفين حسب المسمى الوظيفي
    admin_employees = Employee.query.filter_by(club_id=club_id, position='خدمة عملاء').all()
    trainer_employees = Employee.query.filter_by(club_id=club_id, position='مدرب').all()
    worker_employees = Employee.query.filter_by(club_id=club_id, position='عامل').all()
    
    print(f"عدد موظفي خدمة العملاء: {len(admin_employees)}")
    print(f"عدد المدربين: {len(trainer_employees)}")
    print(f"عدد العمال: {len(worker_employees)}")
    print(f"إجمالي عدد الموظفين: {len(admin_employees) + len(trainer_employees) + len(worker_employees)}")
    
    # عرض جميع الموظفين
    all_employees = Employee.query.all()
    print(f"إجمالي عدد الموظفين في قاعدة البيانات: {len(all_employees)}")
    
    # عرض عدد الموظفين لكل نادي
    clubs = Club.query.all()
    for c in clubs:
        count = Employee.query.filter_by(club_id=c.id).count()
        print(f"النادي: {c.name}, عدد الموظفين: {count}")
        
    # عرض الموظفين الذين ليس لديهم نادي محدد
    no_club_employees = Employee.query.filter_by(club_id=None).all()
    print(f"عدد الموظفين بدون نادي محدد: {len(no_club_employees)}")
    
    # عرض الموظفين الذين لديهم نادي محدد ولكن ليس لديهم مسمى وظيفي
    no_position_employees = Employee.query.filter(Employee.club_id.isnot(None), Employee.position.is_(None)).all()
    print(f"عدد الموظفين بدون مسمى وظيفي: {len(no_position_employees)}")
    for emp in no_position_employees[:10]:  # عرض أول 10 موظفين فقط
        print(f"الموظف: {emp.name}, النادي: {emp.club_id}, المسمى الوظيفي: {emp.position}")
