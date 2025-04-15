from app import db
from datetime import datetime

class FacilityType(db.Model):
    """
    نموذج نوع المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)  # اسم أيقونة Font Awesome
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقة مع المرافق - تم تعطيلها مؤقتًا
    # facilities = db.relationship('Facility', backref='facility_type', lazy='dynamic')

    # العلاقة مع بنود نوع المرفق
    items = db.relationship('FacilityTypeItem', backref='facility_type', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FacilityType {self.name}>'


class FacilityTypeItem(db.Model):
    """
    نموذج بند نوع المرفق
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    facility_type_id = db.Column(db.Integer, db.ForeignKey('facility_type.id'), nullable=False)
    order = db.Column(db.Integer, default=0)  # لترتيب البنود
    is_required = db.Column(db.Boolean, default=True)  # هل البند مطلوب للفحص
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<FacilityTypeItem {self.name}>'


# جدول العلاقة بين النوادي وأنواع المرافق
club_facility_types = db.Table('club_facility_types',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('facility_type_id', db.Integer, db.ForeignKey('facility_type.id'), primary_key=True)
)


class ClubFacilityTypeItem(db.Model):
    """
    نموذج ربط بنود المرافق بالنوادي مع حالة التفعيل
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    facility_type_item_id = db.Column(db.Integer, db.ForeignKey('facility_type_item.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    club = db.relationship('Club', backref=db.backref('facility_type_items_assoc', lazy='dynamic'))
    facility_type_item = db.relationship('FacilityTypeItem', backref=db.backref('clubs_assoc', lazy='dynamic'))

    def __repr__(self):
        return f'<ClubFacilityTypeItem club_id={self.club_id} item_id={self.facility_type_item_id} active={self.is_active}>'
