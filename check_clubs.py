from app import create_app
from app.models import Club

app = create_app()
with app.app_context():
    clubs = Club.query.all()
    print(f'عدد الأندية: {len(clubs)}')
    for club in clubs:
        print(f'النادي: {club.name}, المعرف: {club.id}')
