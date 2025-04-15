from app import create_app, db
from app.models.facility_type import FacilityType, FacilityTypeItem
from app.models.club import Club

app = create_app()
with app.app_context():
    # الحصول على جميع أنواع المرافق
    facility_types = FacilityType.query.all()
    
    print("=== قائمة أنواع المرافق ===")
    for ft in facility_types:
        print(f"النوع: {ft.name} (ID: {ft.id})")
        print(f"الوصف: {ft.description}")
        print(f"نشط: {ft.is_active}")
        
        # الحصول على بنود نوع المرفق
        items = FacilityTypeItem.query.filter_by(facility_type_id=ft.id).all()
        print(f"عدد البنود: {len(items)}")
        
        if items:
            print("البنود:")
            for item in items:
                print(f"  - {item.name} (ID: {item.id})")
        else:
            print("لا توجد بنود لهذا النوع")
        
        # الحصول على النوادي المرتبطة بهذا النوع
        clubs = ft.clubs.all()
        print(f"عدد النوادي المرتبطة: {len(clubs)}")
        
        if clubs:
            print("النوادي المرتبطة:")
            for club in clubs:
                print(f"  - {club.name} (ID: {club.id})")
        else:
            print("لا توجد نوادي مرتبطة بهذا النوع")
        
        print("-" * 50)
    
    # التحقق من نادي الشبلية بشكل خاص
    shabliya_club = Club.query.filter_by(name="نادي اشبليه").first()
    if shabliya_club:
        print(f"\n=== تفاصيل نادي اشبليه (ID: {shabliya_club.id}) ===")
        
        # الحصول على أنواع المرافق المرتبطة بالنادي
        facility_types = shabliya_club.facility_types.all()
        print(f"عدد أنواع المرافق المرتبطة: {len(facility_types)}")
        
        if facility_types:
            print("أنواع المرافق المرتبطة:")
            for ft in facility_types:
                print(f"  - {ft.name} (ID: {ft.id})")
        else:
            print("لا توجد أنواع مرافق مرتبطة بهذا النادي")
    else:
        print("لم يتم العثور على نادي اشبليه")
