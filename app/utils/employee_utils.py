from app.models import Employee
from app.config import EXPECTED_EMPLOYEES_COUNT
import os

def update_expected_employees_count():
    """
    تحديث العدد المتوقع للموظفين في ملف الإعدادات
    """
    # الحصول على العدد الفعلي للموظفين في كل نادي
    from sqlalchemy import func
    from app import db
    
    # الحصول على عدد الموظفين لكل نادي
    club_employee_counts = {}
    club_counts = db.session.query(Employee.club_id, func.count(Employee.id)).filter(Employee.is_active == True).group_by(Employee.club_id).all()
    for club_id, count in club_counts:
        if club_id is not None:  # تجاهل الموظفين بدون نادي
            club_employee_counts[club_id] = count
    
    # تحديث ملف الإعدادات
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # تحديث قيم EXPECTED_EMPLOYEES_COUNT
    new_config_content = config_content.split('EXPECTED_EMPLOYEES_COUNT = {')[0] + 'EXPECTED_EMPLOYEES_COUNT = {\n'
    for club_id, count in club_employee_counts.items():
        new_config_content += f'    {club_id}: {count},  # نادي رقم {club_id}\n'
    new_config_content += '}'
    
    # حفظ التغييرات
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_config_content)
    
    return club_employee_counts
