from app import db
from datetime import datetime

class Shomoos(db.Model):
    """
    نموذج شموس
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    new_number = db.Column(db.Integer, default=0)  # العدد الحالي بنظام شموس
    previous_total = db.Column(db.Integer, default=0)  # الفارق
    total = db.Column(db.Integer, default=0)  # الإجمالي
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    club = db.relationship('Club', backref=db.backref('shomoos_records', lazy='dynamic'))

    def __repr__(self):
        return f'<Shomoos {self.id} - Club {self.club_id}>'
