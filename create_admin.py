from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()

    if admin:
        print('Admin user already exists. Updating password...')
        admin.set_password('admin')
        print(f'Password hash: {admin.password_hash}')
    else:
        print('Creating new admin user...')
        admin = User(
            username='admin',
            email='admin@example.com',
            employee_number='0000',
            role='admin',
            is_active=True
        )
        admin.set_password('admin')
        print(f'Password hash: {admin.password_hash}')
        db.session.add(admin)

    db.session.commit()

    # Verify password
    admin = User.query.filter_by(username='admin').first()
    password_check = admin.check_password('admin')
    print(f'Password check: {password_check}')
    print(f'Direct check: {check_password_hash(admin.password_hash, "admin")}')
    print('Admin user created/updated successfully!')
