from app import create_app
from app.models.user import User
from app.models.club import Club

app = create_app()
with app.app_context():
    print('المستخدمين:')
    users = User.query.all()
    for user in users:
        print(f'المستخدم: {user.username}, الدور: {user.role}, عدد النوادي: {len(user.clubs)}')
        if user.clubs:
            for club in user.clubs:
                print(f'  - النادي: {club.name}, نشط: {club.is_active}')
    
    print('\nالنوادي:')
    clubs = Club.query.filter_by(is_active=True).all()
    print(f'عدد النوادي النشطة: {len(clubs)}')
    for club in clubs:
        print(f'النادي: {club.name}, نشط: {club.is_active}')
