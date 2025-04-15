from app import db
from app.models.user import Permission
# سيتم استيراد النماذج التالية لاحقًا عند إنشائها
# from app.models.revenue import RevenueCategory
# from app.models.violation import ViolationType, ActionType
def init_db_command():
    """تهيئة قاعدة البيانات بالبيانات الأساسية"""
    # إنشاء الصلاحيات
    permissions = [
        {'name': 'clubs', 'description': 'إدارة النوادي'},
        {'name': 'facilities', 'description': 'إدارة المرافق'},
        {'name': 'employees', 'description': 'إدارة الموظفين'},
        {'name': 'issues', 'description': 'إدارة الأعطال'},
        {'name': 'violations', 'description': 'إدارة المخالفات'},
        {'name': 'cameras', 'description': 'فحص الكاميرات'},
        {'name': 'visits', 'description': 'زيارات الفروع'},
        {'name': 'suggestions', 'description': 'الاقتراحات والملاحظات'},
        {'name': 'revenue', 'description': 'إدارة الإيرادات'}
    ]

    for perm_data in permissions:
        # التحقق من عدم وجود الصلاحية مسبقًا
        existing = Permission.query.filter_by(name=perm_data['name']).first()
        if not existing:
            permission = Permission(
                name=perm_data['name'],
                description=perm_data['description'],
                can_view=True,
                can_create=False,
                can_edit=False,
                can_delete=False
            )
            db.session.add(permission)

    # سيتم تفعيل الأكواد التالية لاحقًا عند إنشاء النماذج المطلوبة

    # # إنشاء فئات الإيرادات
    # revenue_categories = [
    #     {'name': 'اشتراكات', 'description': 'إيرادات الاشتراكات الشهرية والسنوية'},
    #     {'name': 'منتجات', 'description': 'إيرادات بيع المنتجات'},
    #     {'name': 'خدمات إضافية', 'description': 'إيرادات الخدمات الإضافية'},
    #     {'name': 'تأجير مرافق', 'description': 'إيرادات تأجير المرافق'},
    #     {'name': 'أخرى', 'description': 'إيرادات أخرى'}
    # ]
    #
    # for cat_data in revenue_categories:
    #     # التحقق من عدم وجود الفئة مسبقًا
    #     existing = RevenueCategory.query.filter_by(name=cat_data['name']).first()
    #     if not existing:
    #         category = RevenueCategory(
    #             name=cat_data['name'],
    #             description=cat_data['description']
    #         )
    #         db.session.add(category)
    #
    # # إنشاء أنواع المخالفات
    # violation_types = [
    #     {'name': 'تأخير', 'description': 'التأخر عن موعد العمل', 'severity': 'low'},
    #     {'name': 'غياب', 'description': 'الغياب بدون إذن', 'severity': 'medium'},
    #     {'name': 'إهمال', 'description': 'إهمال في العمل', 'severity': 'medium'},
    #     {'name': 'سلوك', 'description': 'سلوك غير لائق', 'severity': 'high'},
    #     {'name': 'مخالفة أنظمة', 'description': 'مخالفة أنظمة العمل', 'severity': 'high'}
    # ]
    #
    # for vt_data in violation_types:
    #     # التحقق من عدم وجود نوع المخالفة مسبقًا
    #     existing = ViolationType.query.filter_by(name=vt_data['name']).first()
    #     if not existing:
    #         violation_type = ViolationType(
    #             name=vt_data['name'],
    #             description=vt_data['description'],
    #             severity=vt_data['severity']
    #         )
    #         db.session.add(violation_type)
    #
    # # إنشاء أنواع الإجراءات
    # action_types = [
    #     {'name': 'تنبيه شفهي', 'description': 'تنبيه شفهي للموظف'},
    #     {'name': 'إنذار كتابي', 'description': 'إنذار كتابي للموظف'},
    #     {'name': 'خصم', 'description': 'خصم من الراتب'},
    #     {'name': 'إيقاف مؤقت', 'description': 'إيقاف مؤقت عن العمل'},
    #     {'name': 'فصل', 'description': 'فصل من العمل'}
    # ]
    #
    # for at_data in action_types:
    #     # التحقق من عدم وجود نوع الإجراء مسبقًا
    #     existing = ActionType.query.filter_by(name=at_data['name']).first()
    #     if not existing:
    #         action_type = ActionType(
    #             name=at_data['name'],
    #             description=at_data['description']
    #         )
    #         db.session.add(action_type)

    # حفظ التغييرات
    db.session.commit()

    print('تم تهيئة قاعدة البيانات بالبيانات الأساسية بنجاح')

def init_app(app):
    """تسجيل الأمر مع التطبيق"""
    # تم تعطيل هذا السطر لأنه يعتمد على مكتبة click
    # app.cli.add_command(init_db_command)
