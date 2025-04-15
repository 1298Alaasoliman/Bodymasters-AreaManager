from app import create_app, db
from app.models.club import Club

def add_clubs():
    """إضافة بعض الأندية للتحقق"""
    app = create_app()
    with app.app_context():
        # التحقق من وجود أندية
        existing_clubs = Club.query.all()
        print(f'عدد الأندية الموجودة: {len(existing_clubs)}')
        
        # إذا لم تكن هناك أندية، نضيف بعضها
        if len(existing_clubs) == 0:
            clubs = [
                {'name': 'نادي البديعة', 'manager_name': 'أحمد محمد', 'employee_id': '1001'},
                {'name': 'نادي النهضة', 'manager_name': 'محمد علي', 'employee_id': '1002'},
                {'name': 'نادي الروضة', 'manager_name': 'خالد عبدالله', 'employee_id': '1003'}
            ]
            
            for club_data in clubs:
                club = Club(
                    name=club_data['name'],
                    manager_name=club_data['manager_name'],
                    employee_id=club_data['employee_id'],
                    is_active=True
                )
                db.session.add(club)
            
            db.session.commit()
            print('تمت إضافة الأندية بنجاح')
        else:
            print('توجد أندية بالفعل في قاعدة البيانات')
            for club in existing_clubs:
                print(f'النادي: {club.name}, نشط: {club.is_active}')

if __name__ == '__main__':
    add_clubs()
