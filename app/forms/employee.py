from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional

class EmployeeForm(FlaskForm):
    """
    نموذج الموظف
    """
    employee_number = StringField('الرقم الوظيفي', validators=[
        DataRequired(message='يرجى إدخال الرقم الوظيفي'),
        Length(max=20, message='يجب أن يكون الرقم الوظيفي أقل من 20 حرف')
    ])
    name = StringField('اسم الموظف', validators=[
        DataRequired(message='يرجى إدخال اسم الموظف'),
        Length(max=100, message='يجب أن يكون اسم الموظف أقل من 100 حرف')
    ])
    position = SelectField('المسمى الوظيفي', choices=[
        ('مدير النادي', 'مدير النادي'),
        ('خدمة عملاء', 'خدمة عملاء'),
        ('مدرب', 'مدرب'),
        ('عامل', 'عامل')
    ], validators=[
        DataRequired(message='يرجى اختيار المسمى الوظيفي')
    ])
    role = SelectField('الدور الوظيفي', validators=[
        DataRequired(message='يرجى اختيار الدور الوظيفي')
    ])
    # تم إزالة حقل القسم لأنه غير مطلوب في المتطلبات الجديدة
    # تم إزالة حقل رقم الهاتف لأنه غير مطلوب في المتطلبات الجديدة
    # تم إزالة حقل البريد الإلكتروني لأنه غير مطلوب في المتطلبات الجديدة
    # تم إزالة حقل تاريخ التعيين لأنه غير مطلوب في المتطلبات الجديدة
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    is_active = SelectField('الحالة', choices=[
        ('1', 'يعمل'),
        ('0', 'مجاز')
    ], default='1', validators=[DataRequired(message='يرجى اختيار الحالة')])
    submit = SubmitField('حفظ')

class WorkRecordForm(FlaskForm):
    """
    نموذج سجل العمل
    """
    date = DateField('التاريخ', validators=[
        DataRequired(message='يرجى إدخال التاريخ')
    ], format='%Y-%m-%d')
    time_in = TimeField('وقت الدخول', validators=[Optional()], format='%H:%M')
    time_out = TimeField('وقت الخروج', validators=[Optional()], format='%H:%M')
    is_leave = BooleanField('إجازة')
    leave_type = SelectField('نوع الإجازة', choices=[
        ('', 'اختر نوع الإجازة'),
        ('annual', 'إجازة سنوية'),
        ('sick', 'إجازة مرضية'),
        ('emergency', 'إجازة طارئة'),
        ('other', 'أخرى')
    ], validators=[Optional()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')
