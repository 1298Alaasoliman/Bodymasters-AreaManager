from app import create_app, db
from app.models.facility import FacilityCheck, FacilityCheckResult

def update_violations_count():
    """
    تحديث قيم عمود violations_count لفحوصات المرافق الموجودة
    """
    app = create_app()
    
    with app.app_context():
        # الحصول على جميع فحوصات المرافق
        checks = FacilityCheck.query.all()
        print(f"تم العثور على {len(checks)} فحص مرافق")
        
        updated_count = 0
        
        for check in checks:
            # الحصول على نتائج الفحص
            results = FacilityCheckResult.query.filter_by(facility_check_id=check.id).all()
            
            # حساب عدد المخالفات (النتائج التي حالتها 'failed')
            violations_count = sum(1 for result in results if result.status == 'failed')
            
            # تحديث عدد المخالفات
            check.violations_count = violations_count
            updated_count += 1
        
        # حفظ التغييرات
        db.session.commit()
        
        print(f"تم تحديث عدد المخالفات لـ {updated_count} فحص مرافق")

if __name__ == "__main__":
    update_violations_count()
