from app import create_app, db
from app.models.club import Club
from app.models.employee import Employee

app = create_app()

with app.app_context():
    # التحقق من النادي رقم 1
    club = Club.query.get(1)
    if club:
        print(f"Club ID: {club.id}, Name: {club.name}")
        
        # استرجاع الموظفين باستخدام العلاقة
        rel_employees = club.employees.all()
        print(f"Employees from relationship: {len(rel_employees)}")
        for emp in rel_employees:
            print(f"  - ID: {emp.id}, Name: {emp.name}, Club ID: {emp.club_id}")
        
        # استرجاع الموظفين باستخدام الاستعلام المباشر
        query_employees = Employee.query.filter_by(club_id=club.id).all()
        print(f"Employees from direct query: {len(query_employees)}")
        for emp in query_employees:
            print(f"  - ID: {emp.id}, Name: {emp.name}, Club ID: {emp.club_id}")
        
        # التحقق من الموظفين الذين لديهم club_id=1 ولكن لا يظهرون في العلاقة
        rel_ids = [emp.id for emp in rel_employees]
        missing_employees = [emp for emp in query_employees if emp.id not in rel_ids]
        if missing_employees:
            print(f"Employees missing from relationship: {len(missing_employees)}")
            for emp in missing_employees:
                print(f"  - ID: {emp.id}, Name: {emp.name}, Club ID: {emp.club_id}")
        
        # التحقق من الموظفين الذين يظهرون في العلاقة ولكن ليس لديهم club_id=1
        query_ids = [emp.id for emp in query_employees]
        extra_employees = [emp for emp in rel_employees if emp.id not in query_ids]
        if extra_employees:
            print(f"Extra employees in relationship: {len(extra_employees)}")
            for emp in extra_employees:
                print(f"  - ID: {emp.id}, Name: {emp.name}, Club ID: {emp.club_id}")
    else:
        print("Club with ID 1 not found.")
