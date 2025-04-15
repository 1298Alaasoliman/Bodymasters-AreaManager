from app import db
from datetime import datetime

class Schedule(db.Model):
    """
    نموذج جدول الدوامات
    """
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    # أيام الدوام
    saturday = db.Column(db.Boolean, default=False)
    sunday = db.Column(db.Boolean, default=False)
    monday = db.Column(db.Boolean, default=False)
    tuesday = db.Column(db.Boolean, default=False)
    wednesday = db.Column(db.Boolean, default=False)
    thursday = db.Column(db.Boolean, default=False)
    friday = db.Column(db.Boolean, default=False)

    # فترات الدوام
    shift_type = db.Column(db.String(20), default='single')  # single, double, 7hours, 8hours

    # الفترة الأولى
    shift1_start = db.Column(db.Time, nullable=True)
    shift1_end = db.Column(db.Time, nullable=True)

    # الفترة الثانية (في حالة الدوام بفترتين)
    shift2_start = db.Column(db.Time, nullable=True)
    shift2_end = db.Column(db.Time, nullable=True)

    # يوم التخصيص (في حالة وجود يوم مخصص للموظف)
    specific_day = db.Column(db.String(100), nullable=True)
    specific_day_start = db.Column(db.Time, nullable=True)
    specific_day_end = db.Column(db.Time, nullable=True)

    # معلومات إضافية
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    employee = db.relationship('Employee', backref='schedules')
    club = db.relationship('Club', backref='schedules')

    def __repr__(self):
        return f'<Schedule {self.id} for Employee {self.employee_id}>'
