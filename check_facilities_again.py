from app import create_app, db
from app.models.club import Club
from app.models.facility import Facility

app = create_app()
with app.app_context():
    # الحصول على جميع المرافق
    facilities = Facility.query.all()
    
    print(f"إجمالي عدد المرافق في قاعدة البيانات: {len(facilities)}")
    
    for facility in facilities:
        print(f"ID: {facility.id}, الاسم: {facility.name}, النادي: {facility.club_id}, النوع: {facility.facility_type}")
    
    # التحقق من المرافق لنادي اشبليه
    club_facilities = Facility.query.filter_by(club_id=1).all()
    print(f"\nعدد المرافق لنادي اشبليه (ID: 1): {len(club_facilities)}")
    
    for facility in club_facilities:
        print(f"ID: {facility.id}, الاسم: {facility.name}, النوع: {facility.facility_type}")
