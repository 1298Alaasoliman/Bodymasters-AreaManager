from app import create_app, db
from app.models.club import Club
from app.models.facility import Facility

app = create_app()
with app.app_context():
    # الحصول على جميع النوادي
    clubs = Club.query.all()
    
    print("=== قائمة النوادي والمرافق ===")
    for club in clubs:
        facilities = Facility.query.filter_by(club_id=club.id).all()
        print(f"النادي: {club.name} (ID: {club.id})")
        print(f"عدد المرافق: {len(facilities)}")
        
        if facilities:
            print("المرافق:")
            for facility in facilities:
                print(f"  - {facility.name} (ID: {facility.id})")
        else:
            print("لا توجد مرافق لهذا النادي")
        print("-" * 50)
    
    # التحقق من نادي الشبلية بشكل خاص
    shabliya_club = Club.query.filter_by(name="نادي الشبلية").first()
    if shabliya_club:
        print(f"\n=== تفاصيل نادي الشبلية (ID: {shabliya_club.id}) ===")
        facilities = Facility.query.filter_by(club_id=shabliya_club.id).all()
        print(f"عدد المرافق: {len(facilities)}")
        
        if facilities:
            print("المرافق:")
            for facility in facilities:
                print(f"  - {facility.name} (ID: {facility.id})")
                print(f"    الوصف: {facility.description}")
                print(f"    النوع: {facility.facility_type}")
                print(f"    نشط: {facility.is_active}")
        else:
            print("لا توجد مرافق لهذا النادي")
            
        # التحقق من أنواع المرافق المرتبطة بالنادي
        facility_types = shabliya_club.facility_types
        print(f"\nأنواع المرافق المرتبطة بالنادي: {len(facility_types)}")
        for ft in facility_types:
            print(f"  - {ft.name} (ID: {ft.id})")
    else:
        print("لم يتم العثور على نادي الشبلية")
