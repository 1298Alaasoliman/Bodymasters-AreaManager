from app import db
from datetime import datetime

class Issue(db.Model):
    """
    نموذج العطل
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=True)

    # العلاقات
    club = db.relationship('Club', foreign_keys=[club_id], backref=db.backref('issues', lazy='dynamic'))
    facility = db.relationship('Facility', foreign_keys=[facility_id], backref=db.backref('issues', lazy='dynamic'))
    request_number = db.Column(db.Integer)
    request_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='open')  # open, closed, pending
    notes = db.Column(db.Text, nullable=True)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Issue {self.id} request_number={self.request_number} status={self.status}>'

    @property
    def is_overdue(self):
        """
        التحقق مما إذا كان العطل متأخرًا
        """
        if self.status == 'closed':
            return False

        now = datetime.now().date()

        if now > self.due_date:
            return True

        return False
