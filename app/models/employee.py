from app import db
from datetime import datetime

class Employee(db.Model):
    """
    نموذج الموظف
    """
    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(20), index=True, unique=True)
    name = db.Column(db.String(100), index=True)
    position = db.Column(db.String(100))
    role = db.Column(db.String(50), default='موظف')  # الدور: مدير، مشرف، موظف، إلخ
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    hire_date = db.Column(db.Date, nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    work_records = db.relationship('WorkRecord', backref='employee', lazy='dynamic')
    violations = db.relationship('Violation', backref='employee', lazy='dynamic')

    def __repr__(self):
        return f'<Employee {self.name}>'

class WorkRecord(db.Model):
    """
    نموذج سجل العمل
    """
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    date = db.Column(db.Date, default=datetime.utcnow)
    time_in = db.Column(db.Time, nullable=True)
    time_out = db.Column(db.Time, nullable=True)
    hours_worked = db.Column(db.Float, nullable=True)
    is_leave = db.Column(db.Boolean, default=False)
    leave_type = db.Column(db.String(50), nullable=True)  # إجازة سنوية، مرضية، إلخ
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<WorkRecord {self.id} for {self.employee_id} on {self.date}>'

    def calculate_hours(self):
        """
        حساب ساعات العمل
        """
        if self.time_in and self.time_out:
            time_in_dt = datetime.combine(self.date, self.time_in)
            time_out_dt = datetime.combine(self.date, self.time_out)

            # إذا كان وقت الخروج قبل وقت الدخول، فهذا يعني أن الموظف خرج في اليوم التالي
            if time_out_dt < time_in_dt:
                time_out_dt = datetime.combine(self.date + timedelta(days=1), self.time_out)

            delta = time_out_dt - time_in_dt
            self.hours_worked = delta.total_seconds() / 3600  # تحويل الثواني إلى ساعات
