from app import create_app
from app.models.club import Club
from app.models.employee import Employee

app = create_app()
with app.app_context():
    # التحقق من عدد الموظفين في النادي رقم 2
    club = Club.query.get(2)
    if club:
        print(f'Club ID: {club.id}, Name: {club.name}')
        print(f'Employees count using relationship: {club.employees.count()}')
        
        direct_count = Employee.query.filter_by(club_id=club.id).count()
        print(f'Employees count using direct query: {direct_count}')
        
        employees = Employee.query.filter_by(club_id=club.id).all()
        print('Employees:')
        for emp in employees:
            print(f'- {emp.name} (ID: {emp.id})')
    else:
        print('Club with ID 2 not found')
