from app import create_app
from app.models import User, Club

app = create_app()
with app.app_context():
    # التحقق من جميع المستخدمين
    users = User.query.all()
    for user in users:
        print(f'المستخدم: {user.username}, المعرف: {user.id}')
        print(f'عدد الأندية المحددة للمستخدم: {len(user.clubs)}')
        if user.clubs:
            for club in user.clubs:
                print(f'\t- النادي: {club.name}, المعرف: {club.id}')
            print()
