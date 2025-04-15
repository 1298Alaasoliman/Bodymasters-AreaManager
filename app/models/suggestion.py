from app import db
from datetime import datetime

class Suggestion(db.Model):
    """
    نموذج الاقتراح
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50))  # اقتراح تطوير، ملاحظة سلبية، إلخ
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, in_review, implemented, rejected
    response = db.Column(db.Text, nullable=True)
    responded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    response_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Suggestion {self.id} status={self.status}>'
