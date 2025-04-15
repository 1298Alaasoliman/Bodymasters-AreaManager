from app import create_app, db
from app.models.club import Club
from app.models.employee import Employee

app = create_app()
with app.app_context():
    club = Club.query.get(1)
    print(f'Club ID: {club.id}, Name: {club.name}')
    print(f'Employees count: {club.employees.count()}')
    for emp in club.employees:
        print(f'Employee ID: {emp.id}, Name: {emp.name}, Club ID: {emp.club_id}')
