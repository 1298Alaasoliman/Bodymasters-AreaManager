from app import create_app, db
from app.models.club import Club
from app.models.facility import Facility
from app.models.facility_type import FacilityType

app = create_app()
with app.app_context():
    # الحصول على نادي اشبليه
    club = Club.query.filter_by(name="نادي اشبليه").first()
    
    if not club:
        print("لم يتم العثور على نادي اشبليه")
        exit()
    
    print(f"تم العثور على نادي اشبليه (ID: {club.id})")
    
    # الحصول على أنواع المرافق المرتبطة بالنادي
    facility_types = club.facility_types.all()
    
    if not facility_types:
        print("لا توجد أنواع مرافق مرتبطة بالنادي")
        exit()
    
    print(f"عدد أنواع المرافق المرتبطة بالنادي: {len(facility_types)}")
    
    # إنشاء مرافق للنادي
    created_facilities = []
    
    for ft in facility_types:
        # التحقق من وجود مرفق لهذا النوع
        existing_facility = Facility.query.filter_by(club_id=club.id, facility_type=ft.name).first()
        
        if existing_facility:
            print(f"المرفق {existing_facility.name} موجود بالفعل")
            continue
        
        # إنشاء مرفق جديد
        facility = Facility(
            name=f"{ft.name} - {club.name}",
            description=f"مرفق {ft.name} في {club.name}",
            club_id=club.id,
            facility_type=ft.name,
            is_active=True
        )
        
        db.session.add(facility)
        created_facilities.append(facility)
    
    if created_facilities:
        db.session.commit()
        print(f"تم إنشاء {len(created_facilities)} مرفق جديد:")
        for facility in created_facilities:
            print(f"  - {facility.name} (ID: {facility.id})")
    else:
        print("لم يتم إنشاء أي مرافق جديدة")
