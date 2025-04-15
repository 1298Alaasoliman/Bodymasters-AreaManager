from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, FileField, SubmitField, RadioField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileAllowed

class ViolationTypeForm(FlaskForm):
    """
    نموذج نوع المخالفة
    """
    name = StringField('اسم نوع المخالفة', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('حفظ')

class ViolationSourceForm(FlaskForm):
    """
    نموذج مصدر المخالفة
    """
    name = StringField('اسم مصدر المخالفة', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('حفظ')

class ViolationForm(FlaskForm):
    """
    نموذج المخالفة
    """
    club_id = SelectField('النادي', validators=[Optional()], coerce=int, validate_choice=False)
    employee_id = StringField('الرقم الوظيفي', validators=[DataRequired()])
    employee_name = StringField('اسم الموظف', render_kw={'readonly': True})
    job_role = StringField('الدور الوظيفي', render_kw={'readonly': True})
    employee_club = StringField('النادي التابع له', render_kw={'readonly': True})
    violation_type_id = SelectField('نوع المخالفة', validators=[DataRequired()], coerce=lambda x: int(x) if x else None, validate_choice=False)
    violation_source_id = SelectField('مصدر المخالفة', validators=[Optional()], coerce=int, validate_choice=False)
    violation_number = StringField('رقم المخالفة للموظف', render_kw={'readonly': True})
    violation_date = DateField('تاريخ المخالفة', validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    employee_signature = RadioField('توقيع الموظف على المخالفة', choices=[('yes', 'نعم'), ('no', 'لا')], validators=[DataRequired()])
    source = SelectField(
        'مصدر المخالفة',
        choices=[
            ('', 'اختر--'),
            ('clubs_manager', 'مدير الأندية'),
            ('area_manager', 'مدبر المنطقه'),
            ('club_manager', 'مدير النادي'),
            ('camera_monitor', 'مراقب الكاميرات')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('حفظ')

class ImportViolationTypesForm(FlaskForm):
    """
    نموذج استيراد أنواع المخالفات من ملف Excel
    """
    file = FileField('ملف Excel', validators=[
        DataRequired(),
        FileAllowed(['xlsx', 'xls'], 'يجب أن يكون الملف بصيغة Excel')
    ])
    submit = SubmitField('استيراد')

class ImportViolationSourcesForm(FlaskForm):
    """
    نموذج استيراد مصادر المخالفات من ملف Excel
    """
    file = FileField('ملف Excel', validators=[
        DataRequired(),
        FileAllowed(['xlsx', 'xls'], 'يجب أن يكون الملف بصيغة Excel')
    ])
    submit = SubmitField('استيراد')