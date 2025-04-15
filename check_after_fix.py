from app import create_app, db
from app.models.club import Club
from app.models.employee import Employee

app = create_app()
with app.app_context():
    # عرض عدد الموظفين في النادي رقم 1
    club1 = Club.query.get(1)
    print(f'Club ID 1: {club1.name}, Employees count: {club1.employees.count()}')
    
    # عرض الموظفين في النادي رقم 1
    print('\nEmployees in Club 1:')
    for i, emp in enumerate(club1.employees):
        print(f'{i+1}. {emp.name} (ID: {emp.id})')
