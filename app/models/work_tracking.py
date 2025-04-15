from app import db
from datetime import datetime, timedelta

class WorkTracking(db.Model):
    """
    نموذج متابعة العمل
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
        return f'<WorkTracking {self.id} for {self.employee_id} on {self.date}>'
    
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
