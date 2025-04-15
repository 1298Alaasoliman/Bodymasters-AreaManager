from app import db
from datetime import datetime, date

class RevenueCategory(db.Model):
    """
    نموذج فئة الإيرادات
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات
    revenues = db.relationship('Revenue', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<RevenueCategory {self.name}>'

class MonthlyTarget(db.Model):
    """
    نموذج التارجت الشهري
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    month = db.Column(db.Integer)  # رقم الشهر (1-12)
    year = db.Column(db.Integer)  # السنة
    target_amount = db.Column(db.Float)  # مبلغ التارجت
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    club = db.relationship('Club', backref=db.backref('monthly_targets', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('created_targets', lazy='dynamic'))

    def __repr__(self):
        return f'<MonthlyTarget club_id={self.club_id} {self.month}/{self.year} amount={self.target_amount}>'

    @property
    def month_name(self):
        """الحصول على اسم الشهر بالعربي"""
        months = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        return months[self.month - 1] if 1 <= self.month <= 12 else ''

class DailyRevenue(db.Model):
    """
    نموذج الإيراد اليومي
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    date = db.Column(db.Date, default=date.today)
    amount = db.Column(db.Float)  # مبلغ الإيراد اليومي
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    club = db.relationship('Club', backref=db.backref('daily_revenues', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('recorded_revenues', lazy='dynamic'))

    def __repr__(self):
        return f'<DailyRevenue club_id={self.club_id} {self.date} amount={self.amount}>'

class Revenue(db.Model):
    """
    نموذج الإيرادات
    """
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('revenue_category.id'))
    date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Float)
    description = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Revenue {self.id} amount={self.amount}>'
