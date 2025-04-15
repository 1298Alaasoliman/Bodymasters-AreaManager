from app import db
from datetime import datetime

class ViolationType(db.Model):
    """
    نموذج نوع المخالفة
    """
    __tablename__ = 'violation_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # العلاقات
    violations = db.relationship('Violation', backref='violation_type', lazy='dynamic')

    def __repr__(self):
        return f'<ViolationType {self.id}: {self.name}>'

class ViolationSource(db.Model):
    """
    نموذج مصدر المخالفة
    """
    __tablename__ = 'violation_source'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # العلاقات
    violations = db.relationship('Violation', backref='violation_source', lazy='dynamic')

    def __repr__(self):
        return f'<ViolationSource {self.id}: {self.name}>'

class Violation(db.Model):
    """
    نموذج المخالفة
    """
    __tablename__ = 'violation'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    violation_type_id = db.Column(db.Integer, db.ForeignKey('violation_type.id'), nullable=False)
    violation_source_id = db.Column(db.Integer, db.ForeignKey('violation_source.id'), nullable=True)
    violation_number = db.Column(db.Integer, nullable=False)  # رقم المخالفة للموظف
    violation_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    notes = db.Column(db.Text, nullable=True)
    employee_signature = db.Column(db.String(10), nullable=False)  # yes or no
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # العلاقات
    employee_rel = db.relationship('Employee', foreign_keys=[employee_id])
    club_rel = db.relationship('Club', foreign_keys=[club_id])
    user_rel = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Violation {self.id} for Employee {self.employee_id}>'
