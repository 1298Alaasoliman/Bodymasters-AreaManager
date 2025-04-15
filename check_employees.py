from app import create_app, db
from app.models.club import Club
from app.models.employee import Employee

app = create_app()
with app.app_context():
    # عرض جميع النوادي وعدد الموظفين في كل نادي
    clubs = Club.query.all()
    for club in clubs:
        print(f'Club ID: {club.id}, Name: {club.name}, Employees count: {club.employees.count()}')
    
    # عرض تفاصيل الموظفين في النادي رقم 1
    club1 = Club.query.get(1)
    print(f'\nDetails for Club ID 1: {club1.name}')
    print(f'Employees count: {club1.employees.count()}')
    
    # عرض جميع الموظفين في النظام
    all_employees = Employee.query.all()
    print(f'\nTotal employees in system: {len(all_employees)}')
    
    # عرض عدد الموظفين الذين ليس لديهم نادي
    no_club_employees = Employee.query.filter_by(club_id=None).all()
    print(f'Employees with no club: {len(no_club_employees)}')
    
    # عرض عدد الموظفين في كل نادي باستخدام استعلام مباشر
    for club in clubs:
        direct_count = Employee.query.filter_by(club_id=club.id).count()
        print(f'Club ID: {club.id}, Direct employee count: {direct_count}')
