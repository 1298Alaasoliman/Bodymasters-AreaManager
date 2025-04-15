from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    print('Current users:')
    users = User.query.all()
    for user in users:
        print(f'Username: {user.username}, Is Admin: {user.is_admin}')
