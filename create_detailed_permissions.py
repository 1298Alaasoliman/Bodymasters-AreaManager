from app import create_app, db
from app.models.user import DetailedPermission
import traceback

app = create_app()

def create_detailed_permissions():
    """إنشاء الصلاحيات التفصيلية للاختبار"""
    try:
        with app.app_context():
            # حذف جميع الصلاحيات التفصيلية الموجودة
            print("جاري حذف الصلاحيات التفصيلية الموجودة...")
            DetailedPermission.query.delete()

            # قائمة بالصفحات والأزرار
            print("جاري إنشاء الصلاحيات التفصيلية...")
            pages = {
            'الصفحة الرئيسية': {
                'description': 'الصفحة الرئيسية للتطبيق',
                'actions': [
                    {'name': 'عرض الصفحة', 'description': 'عرض الصفحة الرئيسية'},
                    {'name': 'عرض الإحصائيات', 'description': 'عرض إحصائيات النوادي'},
                ]
            },
            'النوادي': {
                'description': 'إدارة النوادي',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة النوادي'},
                    {'name': 'إضافة نادي', 'description': 'إضافة نادي جديد'},
                    {'name': 'تعديل نادي', 'description': 'تعديل بيانات النادي'},
                    {'name': 'حذف نادي', 'description': 'حذف نادي'},
                    {'name': 'استيراد من إكسل', 'description': 'استيراد النوادي من ملف إكسل'},
                ]
            },
            'المرافق': {
                'description': 'إدارة المرافق',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة المرافق'},
                    {'name': 'إضافة مرفق', 'description': 'إضافة مرفق جديد'},
                    {'name': 'تعديل مرفق', 'description': 'تعديل بيانات المرفق'},
                    {'name': 'حذف مرفق', 'description': 'حذف مرفق'},
                    {'name': 'إنشاء تشيك', 'description': 'إنشاء تشيك جديد للمرافق'},
                    {'name': 'عرض سجل التشيك', 'description': 'عرض سجل التشيك للمرافق'},
                ]
            },
            'الموظفين': {
                'description': 'إدارة الموظفين',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة الموظفين'},
                    {'name': 'إضافة موظف', 'description': 'إضافة موظف جديد'},
                    {'name': 'تعديل موظف', 'description': 'تعديل بيانات الموظف'},
                    {'name': 'حذف موظف', 'description': 'حذف موظف'},
                    {'name': 'استيراد من إكسل', 'description': 'استيراد الموظفين من ملف إكسل'},
                    {'name': 'عرض جدول العمل', 'description': 'عرض جدول عمل الموظفين'},
                ]
            },
            'الأعطال': {
                'description': 'إدارة الأعطال',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة الأعطال'},
                    {'name': 'إضافة عطل', 'description': 'إضافة عطل جديد'},
                    {'name': 'تعديل عطل', 'description': 'تعديل بيانات العطل'},
                    {'name': 'حذف عطل', 'description': 'حذف عطل'},
                    {'name': 'تحديث حالة', 'description': 'تحديث حالة العطل'},
                ]
            },
            'المخالفات': {
                'description': 'إدارة المخالفات',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة المخالفات'},
                    {'name': 'إضافة مخالفة', 'description': 'إضافة مخالفة جديدة'},
                    {'name': 'تعديل مخالفة', 'description': 'تعديل بيانات المخالفة'},
                    {'name': 'حذف مخالفة', 'description': 'حذف مخالفة'},
                    {'name': 'إدارة أنواع المخالفات', 'description': 'إدارة أنواع المخالفات'},
                ]
            },
            'الكاميرات': {
                'description': 'فحص الكاميرات',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة فحوصات الكاميرات'},
                    {'name': 'إضافة فحص', 'description': 'إضافة فحص كاميرات جديد'},
                    {'name': 'تعديل فحص', 'description': 'تعديل بيانات فحص الكاميرات'},
                    {'name': 'حذف فحص', 'description': 'حذف فحص كاميرات'},
                ]
            },
            'الإيرادات': {
                'description': 'إدارة الإيرادات',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة الإيرادات'},
                    {'name': 'إضافة إيراد', 'description': 'إضافة إيراد جديد'},
                    {'name': 'تعديل إيراد', 'description': 'تعديل بيانات الإيراد'},
                    {'name': 'حذف إيراد', 'description': 'حذف إيراد'},
                    {'name': 'عرض التقارير', 'description': 'عرض تقارير الإيرادات'},
                ]
            },
            'شموس': {
                'description': 'إدارة شموس',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة شموس'},
                    {'name': 'إضافة سجل', 'description': 'إضافة سجل شموس جديد'},
                    {'name': 'تعديل سجل', 'description': 'تعديل بيانات سجل شموس'},
                    {'name': 'حذف سجل', 'description': 'حذف سجل شموس'},
                ]
            },
            'المستخدمين': {
                'description': 'إدارة المستخدمين',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة المستخدمين'},
                    {'name': 'إضافة مستخدم', 'description': 'إضافة مستخدم جديد'},
                    {'name': 'تعديل مستخدم', 'description': 'تعديل بيانات المستخدم'},
                    {'name': 'حذف مستخدم', 'description': 'حذف مستخدم'},
                    {'name': 'إدارة الصلاحيات', 'description': 'إدارة صلاحيات المستخدمين'},
                ]
            },
        }

        # إنشاء الصلاحيات التفصيلية
        for page_name, page_data in pages.items():
            for action in page_data['actions']:
                permission = DetailedPermission(
                    page_name=page_name,
                    page_description=page_data['description'],
                    action_name=action['name'],
                    action_description=action['description'],
                    is_allowed=False
                )
                db.session.add(permission)

            # حفظ التغييرات
            db.session.commit()
            print("تم إنشاء الصلاحيات التفصيلية بنجاح!")
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    create_detailed_permissions()
