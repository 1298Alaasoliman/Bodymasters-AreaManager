from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget

class ClubForm(FlaskForm):
    """
    نموذج النادي
    """
    name = StringField('اسم النادي', validators=[
        DataRequired(message='يرجى إدخال اسم النادي'),
        Length(max=100, message='يجب أن يكون اسم النادي أقل من 100 حرف')
    ])
    # تم إزالة حقل الموقع بناءً على طلب المستخدم
    manager_name = StringField('اسم المدير', validators=[
        DataRequired(message='يرجى إدخال اسم مدير النادي'),
        Length(max=100, message='يجب أن يكون اسم المدير أقل من 100 حرف')
    ])
    employee_id = StringField('الرقم الوظيفي', validators=[
        Optional(),
        Length(max=10, message='يجب أن يكون الرقم الوظيفي أقل من 10 أرقام')
    ])
    # تم إزالة حقل البريد الإلكتروني بناءً على طلب المستخدم
    # تم إزالة حقل تاريخ الافتتاح بناءً على طلب المستخدم
    is_active = BooleanField('نشط')

    # تم إزالة الحقول المتعلقة بالمرافق المختلفة بناءً على طلب المستخدم

    # حقل لاختيار أنواع المرافق
    facility_types = SelectMultipleField('أنواع المرافق', coerce=int,
                                       widget=ListWidget(prefix_label=False),
                                       option_widget=CheckboxInput(),
                                       validators=[Optional()])

    submit = SubmitField('حفظ')
