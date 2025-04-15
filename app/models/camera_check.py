from app import db
from datetime import datetime

class CameraCheck(db.Model):
    """
    نموذج فحص الكاميرات
    """
    __tablename__ = 'camera_checks'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    opening_check = db.Column(db.Boolean, default=False)
    check_12 = db.Column(db.Boolean, default=False)
    check_2 = db.Column(db.Boolean, default=False)
    check_3 = db.Column(db.Boolean, default=False)
    check_5 = db.Column(db.Boolean, default=False)
    check_8 = db.Column(db.Boolean, default=False)
    check_10 = db.Column(db.Boolean, default=False)
    check_11 = db.Column(db.Boolean, default=False)
    check_1150 = db.Column(db.Boolean, default=False)
    violations_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    # العلاقات
    club_rel = db.relationship('Club', foreign_keys=[club_id])
    user_rel = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<CameraCheck {self.id} for Club {self.club_id}>'
