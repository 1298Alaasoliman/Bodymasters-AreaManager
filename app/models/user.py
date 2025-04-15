from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# جدول العلاقة بين المستخدمين والنوادي (علاقة متعددة إلى متعددة)
user_club = db.Table('user_club',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

# جدول العلاقة بين المستخدمين والصلاحيات (علاقة متعددة إلى متعددة)
user_permission = db.Table('user_permission',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

# جدول العلاقة بين المستخدمين والصلاحيات التفصيلية (علاقة متعددة إلى متعددة)
user_detailed_permission = db.Table('user_detailed_permission',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('detailed_permission_id', db.Integer, db.ForeignKey('detailed_permission.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """
    نموذج المستخدم
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    employee_number = db.Column(db.String(20), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # العلاقات
    clubs = db.relationship('Club', secondary=user_club, backref=db.backref('users', lazy='dynamic'))
    permissions = db.relationship('Permission', secondary=user_permission, backref=db.backref('users', lazy='dynamic'))
    detailed_permissions = db.relationship('DetailedPermission', secondary=user_detailed_permission, backref=db.backref('users', lazy='dynamic'))
    facility_checks = db.relationship('FacilityCheck', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """
        تعيين كلمة المرور المشفرة
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        التحقق من كلمة المرور
        """
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission_name, action):
        """
        التحقق مما إذا كان المستخدم لديه صلاحية معينة
        """
        if self.role == 'admin':
            return True

        # التحقق من الصلاحيات القديمة
        for permission in self.permissions:
            if permission.name == permission_name and getattr(permission, action, False):
                return True

        # التحقق من الصلاحيات التفصيلية
        for permission in self.detailed_permissions:
            if permission.page_name == permission_name and permission.action_name == action and permission.is_allowed:
                return True

        return False

    def has_button_permission(self, page_name, button_name):
        """
        التحقق مما إذا كان المستخدم لديه صلاحية لزر معين في صفحة معينة
        """
        if self.role == 'admin':
            return True

        for permission in self.detailed_permissions:
            if permission.page_name == page_name and permission.action_name == button_name and permission.is_allowed:
                return True

        return False

    def has_club_access(self, club_id):
        """
        التحقق مما إذا كان المستخدم لديه وصول إلى نادٍ معين
        """
        if self.role == 'admin':
            return True

        for club in self.clubs:
            if club.id == club_id:
                return True

        return False

class Permission(db.Model):
    """
    نموذج الصلاحيات
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    can_view = db.Column(db.Boolean, default=False)
    can_create = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Permission {self.name}>'

class DetailedPermission(db.Model):
    """
    نموذج الصلاحيات التفصيلية
    """
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(64))  # اسم الصفحة
    page_description = db.Column(db.String(255))  # وصف الصفحة
    action_name = db.Column(db.String(64))  # اسم الإجراء أو الزر
    action_description = db.Column(db.String(255))  # وصف الإجراء
    is_allowed = db.Column(db.Boolean, default=False)  # هل مسموح بهذا الإجراء

    def __repr__(self):
        return f'<DetailedPermission {self.page_name}:{self.action_name}>'

@login.user_loader
def load_user(id):
    """
    تحميل المستخدم لمكتبة Flask-Login
    """
    return User.query.get(int(id))
