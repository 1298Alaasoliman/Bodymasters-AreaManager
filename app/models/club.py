from app import db
from datetime import datetime
from app.models.facility_type import club_facility_types

class Club(db.Model):
    """
    نموذج النادي
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    location = db.Column(db.String(255))
    manager_name = db.Column(db.String(100))
    employee_id = db.Column(db.String(10))
    email = db.Column(db.String(120))
    opening_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # الحقول الجديدة المطلوبة
    club_entrance = db.Column(db.Boolean, default=False)  # مدخل النادي ومنطقة الاستقبال
    reception_area = db.Column(db.Boolean, default=False)  # منطقة الاستقبال
    training_area = db.Column(db.Boolean, default=False)  # صالة التدريب
    group_classes = db.Column(db.Boolean, default=False)  # الحصص الجماعية
    ladies_area = db.Column(db.Boolean, default=False)  # صالة تدريب السيدات
    cardio_area = db.Column(db.Boolean, default=False)  # صالة الكارديو
    weights_area = db.Column(db.Boolean, default=False)  # منطقة الأوزان الحرة
    locker_rooms = db.Column(db.Boolean, default=False)  # غرف تبديل الملابس
    showers = db.Column(db.Boolean, default=False)  # الدشات
    swimming_pool = db.Column(db.Boolean, default=False)  # المسبح

    # عدد الموظفين المتوقع (تم إزالته لتجنب مشاكل قاعدة البيانات)
    # expected_employees_count = db.Column(db.Integer, default=13)  # العدد المتوقع للموظفين
    sauna = db.Column(db.Boolean, default=False)  # الساونا
    admin_tasks = db.Column(db.Boolean, default=False)  # المهام الإدارية

    # العلاقات
    facilities = db.relationship('Facility', backref='club', lazy='dynamic')
    employees = db.relationship('Employee', backref='club', lazy='dynamic')
    # العلاقة مع الأعطال معرفة في نموذج Issue
    # issues = db.relationship('Issue', backref='club', lazy='dynamic')
    camera_checks = db.relationship('CameraCheck', backref='club', lazy='dynamic')
    visits = db.relationship('Visit', backref='club', lazy='dynamic')
    suggestions = db.relationship('Suggestion', backref='club', lazy='dynamic')
    revenues = db.relationship('Revenue', backref='club', lazy='dynamic')

    # العلاقة مع فحوصات المرافق (من خلال المرافق)
    @property
    def facility_checks(self):
        from app.models.facility import FacilityCheck
        return FacilityCheck.query.join(
            FacilityCheck.facility
        ).filter(
            FacilityCheck.facility.has(club_id=self.id)
        )

    # العلاقة مع أنواع المرافق
    facility_types = db.relationship('FacilityType', secondary=club_facility_types,
                                   lazy='dynamic', backref=db.backref('clubs', lazy='dynamic'))

    def __repr__(self):
        return f'<Club {self.name}>'
