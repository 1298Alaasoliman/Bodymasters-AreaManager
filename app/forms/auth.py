from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from app.models import User, Club

# تعريف حقل مخصص لعرض مربعات الاختيار
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LoginForm(FlaskForm):
    """
    نموذج تسجيل الدخول
    """
    username = StringField('اسم المستخدم', validators=[DataRequired(message='يرجى إدخال اسم المستخدم')])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='يرجى إدخال كلمة المرور')])
    remember_me = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

class RegistrationForm(FlaskForm):
    """
    نموذج تسجيل مستخدم جديد
    """
    username = StringField('الرقم الوظيفي', validators=[
        DataRequired(message='يرجى إدخال الرقم الوظيفي'),
        Length(min=3, max=64, message='يجب أن يكون الرقم الوظيفي بين 3 و 64 حرفًا')
    ])
    email = StringField('الاسم', validators=[
        DataRequired(message='يرجى إدخال الاسم'),
        Length(max=120, message='يجب أن يكون الاسم أقل من 120 حرفًا')
    ])
    employee_number = StringField('رقم الهاتف', validators=[
        DataRequired(message='يرجى إدخال رقم الهاتف'),
        Length(max=20, message='يجب أن يكون رقم الهاتف أقل من 20 حرفًا')
    ])
    clubs = MultiCheckboxField('الأندية', coerce=int, validators=[
        DataRequired(message='يرجى اختيار الأندية')
    ])
    password = PasswordField('كلمة المرور', validators=[
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])

    def __init__(self, *args, **kwargs):
        # استخراج المستخدم الحالي من المعاملات إن وجد
        self.obj = kwargs.get('obj', None)

        super(RegistrationForm, self).__init__(*args, **kwargs)
        # إذا كان النموذج يستخدم للتسجيل الجديد، نجعل حقل كلمة المرور مطلوبًا
        if not self.password.flags.optional and not self.obj:
            self.password.validators.insert(0, DataRequired(message='يرجى إدخال كلمة المرور'))
            self.password2.validators.insert(0, DataRequired(message='يرجى تأكيد كلمة المرور'))
    role = SelectField('الدور', choices=[
        ('admin', 'مسؤول'),
        ('manager', 'مدير'),
        ('user', 'مستخدم')
    ], validators=[DataRequired(message='يرجى اختيار الدور')])
    submit = SubmitField('تسجيل')

    def validate_username(self, username):
        """
        التحقق من عدم وجود اسم مستخدم مكرر
        """
        # إذا كان هناك مستخدم حالي (تعديل) ولم يتغير الرقم الوظيفي
        if self.obj and self.obj.username == username.data:
            return

        # التحقق من عدم وجود مستخدم آخر بنفس الرقم الوظيفي
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('يرجى استخدام رقم وظيفي مختلف')

    def validate_email(self, email):
        """
        التحقق من عدم وجود اسم مكرر
        """
        # لا نحتاج للتحقق من تكرار الاسم
        pass

    def validate_employee_number(self, employee_number):
        """
        التحقق من عدم وجود رقم هاتف مكرر
        """
        # إذا كان هناك مستخدم حالي (تعديل) ولم يتغير رقم الهاتف
        if self.obj and self.obj.employee_number == employee_number.data:
            return

        # التحقق من عدم وجود مستخدم آخر بنفس رقم الهاتف
        user = User.query.filter_by(employee_number=employee_number.data).first()
        if user is not None:
            raise ValidationError('هذا الرقم مستخدم بالفعل')

class EditUserForm(FlaskForm):
    """
    نموذج تعديل بيانات المستخدم
    """
    username = StringField('الرقم الوظيفي', validators=[
        DataRequired(message='يرجى إدخال الرقم الوظيفي'),
        Length(min=3, max=64, message='يجب أن يكون الرقم الوظيفي بين 3 و 64 حرفًا')
    ])
    email = StringField('الاسم', validators=[
        DataRequired(message='يرجى إدخال الاسم'),
        Length(max=120, message='يجب أن يكون الاسم أقل من 120 حرفًا')
    ])
    employee_number = StringField('رقم الهاتف', validators=[
        DataRequired(message='يرجى إدخال رقم الهاتف'),
        Length(max=20, message='يجب أن يكون رقم الهاتف أقل من 20 حرفًا')
    ])
    clubs = MultiCheckboxField('الأندية', coerce=int, validators=[
        DataRequired(message='يرجى اختيار الأندية')
    ])
    password = PasswordField('كلمة المرور', validators=[
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    password2 = PasswordField('تأكيد كلمة المرور', validators=[
        EqualTo('password', message='كلمات المرور غير متطابقة')
    ])
    role = SelectField('الدور', choices=[
        ('admin', 'مسؤول'),
        ('manager', 'مدير'),
        ('user', 'مستخدم')
    ], validators=[DataRequired(message='يرجى اختيار الدور')])
    submit = SubmitField('حفظ التغييرات')

    def __init__(self, original_username=None, original_employee_number=None, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_employee_number = original_employee_number

    def validate_username(self, username):
        """
        التحقق من عدم وجود رقم وظيفي مكرر
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('يرجى استخدام رقم وظيفي مختلف')

    def validate_employee_number(self, employee_number):
        """
        التحقق من عدم وجود رقم هاتف مكرر
        """
        if employee_number.data != self.original_employee_number:
            user = User.query.filter_by(employee_number=employee_number.data).first()
            if user is not None:
                raise ValidationError('هذا الرقم مستخدم بالفعل')

class ChangePasswordForm(FlaskForm):
    """
    نموذج تغيير كلمة المرور
    """
    current_password = PasswordField('كلمة المرور الحالية', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور الحالية')
    ])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[
        DataRequired(message='يرجى إدخال كلمة المرور الجديدة'),
        Length(min=8, message='يجب أن تكون كلمة المرور 8 أحرف على الأقل')
    ])
    new_password2 = PasswordField('تأكيد كلمة المرور الجديدة', validators=[
        DataRequired(message='يرجى تأكيد كلمة المرور الجديدة'),
        EqualTo('new_password', message='كلمات المرور غير متطابقة')
    ])
    submit = SubmitField('تغيير كلمة المرور')
