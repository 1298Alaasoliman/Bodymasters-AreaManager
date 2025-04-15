from app import db
from datetime import datetime

class Visit(db.Model):
    """
    نموذج زيارة الفرع
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    purpose = db.Column(db.String(255))
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Visit {self.id} on {self.visit_date}>'
