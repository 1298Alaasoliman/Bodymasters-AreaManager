from app import db
from datetime import datetime

class FacilityCategory(db.Model):
    """
    نموذج فئة المرافق
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)  # لترتيب الفئات
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    check_items = db.relationship('FacilityCheckItem', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<FacilityCategory {self.name}>'

class Facility(db.Model):
    """
    نموذج المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    facility_type = db.Column(db.String(50), default='general')  # نوع المرفق (عام، مسبح، صالة رياضية، إلخ)
    location = db.Column(db.String(100), nullable=True)  # موقع المرفق داخل النادي
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    check_items = db.relationship('FacilityCheckItem', backref='facility', lazy='dynamic')
    checks = db.relationship('FacilityCheck', backref='facility', lazy='dynamic')

    def __repr__(self):
        return f'<Facility {self.name}>'

class FacilityCheckItem(db.Model):
    """
    نموذج عنصر فحص المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('facility_category.id'), nullable=True)
    order = db.Column(db.Integer, default=0)  # لترتيب عناصر الفحص
    is_required = db.Column(db.Boolean, default=True)  # هل العنصر مطلوب للفحص
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    check_results = db.relationship('FacilityCheckResult', backref='check_item', lazy='dynamic')

    def __repr__(self):
        return f'<FacilityCheckItem {self.name}>'

class FacilityCheck(db.Model):
    """
    نموذج فحص المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    check_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    violations_count = db.Column(db.Integer, default=0)  # عدد المخالفات

    # العلاقات
    results = db.relationship('FacilityCheckResult', backref='facility_check', lazy='dynamic')

    def __repr__(self):
        return f'<FacilityCheck {self.id} on {self.check_date}>'

class FacilityCheckResult(db.Model):
    """
    نموذج نتيجة فحص عنصر المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    facility_check_id = db.Column(db.Integer, db.ForeignKey('facility_check.id'))
    check_item_id = db.Column(db.Integer, db.ForeignKey('facility_check_item.id'))
    status = db.Column(db.String(20), default='not_checked')  # not_checked, passed, failed, na
    value = db.Column(db.String(100), nullable=True)  # قيمة القياس إن وجدت
    notes = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)  # مسار الصورة إن وجدت
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FacilityCheckResult {self.id} status={self.status}>'
