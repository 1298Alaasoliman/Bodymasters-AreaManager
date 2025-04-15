from app import db
from datetime import datetime

class FacilityQuality(db.Model):
    """
    نموذج جودة المرافق
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    facility_type = db.Column(db.String(100))  # نوع المرفق
    quality_percentage = db.Column(db.Integer)  # نسبة الجودة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    club = db.relationship('Club', backref=db.backref('facility_qualities', lazy='dynamic'))

    def __repr__(self):
        return f'<FacilityQuality {self.club.name} - {self.facility_type}: {self.quality_percentage}%>'
