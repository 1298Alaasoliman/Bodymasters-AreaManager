from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
import traceback

class IssueForm(FlaskForm):
    """
    نموذج العطل
    """
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    facility_id = SelectField('المرفق', validators=[
        Optional()
    ], coerce=lambda x: int(x) if x and str(x).strip() and str(x).strip() != '0' else None)
    request_number = IntegerField('رقم الطلب', validators=[
        DataRequired(message='يرجى إدخال رقم الطلب'),
        NumberRange(min=1, message='يجب أن يكون رقم الطلب أكبر من 0')
    ], render_kw={'dir': 'ltr', 'lang': 'en-US', 'inputmode': 'numeric', 'pattern': '[0-9]*'})
    request_date = DateField('تاريخ الطلب', validators=[
        DataRequired(message='يرجى إدخال تاريخ الطلب')
    ], format='%d/%m/%Y')
    due_date = DateField('تاريخ الاستحقاق', validators=[
        DataRequired(message='يرجى إدخال تاريخ الاستحقاق')
    ], format='%d/%m/%Y')
    status = SelectField('حالة الطلب', choices=[
        ('overdue', 'تخطت تاريخ الاستحقاق'),
        ('closed_without_maintenance', 'اغلاق الطلب بدون صيانة'),
        ('pending', 'معلقة')
    ], validators=[DataRequired(message='يرجى اختيار حالة الطلب')])
    notes = TextAreaField('الملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')

class IssueUpdateForm(FlaskForm):
    """
    نموذج تحديث حالة العطل
    """
    status = SelectField('حالة الطلب', choices=[
        ('overdue', 'تخطت تاريخ الاستحقاق'),
        ('closed_without_maintenance', 'اغلاق الطلب بدون صيانة'),
        ('pending', 'معلقة')
    ], validators=[DataRequired(message='يرجى اختيار حالة الطلب')])
    notes = TextAreaField('ملاحظات', validators=[
        Optional()
    ])
    submit = SubmitField('تحديث الحالة')
