from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, IntegerField, RadioField, FieldList, FormField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class FacilityCategoryForm(FlaskForm):
    """
    نموذج فئة المرافق
    """
    name = StringField('اسم الفئة', validators=[
        DataRequired(message='يرجى إدخال اسم الفئة'),
        Length(max=100, message='يجب أن يكون اسم الفئة أقل من 100 حرف')
    ])
    description = TextAreaField('الوصف', validators=[Optional()])
    order = IntegerField('الترتيب', default=0, validators=[
        Optional(),
        NumberRange(min=0, message='يجب أن يكون الترتيب رقماً موجباً')
    ])
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

class FacilityForm(FlaskForm):
    """
    نموذج المرفق
    """
    name = StringField('اسم المرفق', validators=[
        DataRequired(message='يرجى إدخال اسم المرفق'),
        Length(max=100, message='يجب أن يكون اسم المرفق أقل من 100 حرف')
    ])
    description = TextAreaField('الوصف', validators=[Optional()])
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    facility_type = SelectField('نوع المرفق', choices=[
        ('general', 'عام'),
        ('pool', 'مسبح'),
        ('gym', 'صالة رياضية'),
        ('playground', 'ملعب'),
        ('restaurant', 'مطعم'),
        ('other', 'أخرى')
    ], validators=[DataRequired(message='يرجى اختيار نوع المرفق')])
    location = StringField('الموقع داخل النادي', validators=[Optional()])
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

class FacilityTypeForm(FlaskForm):
    """
    نموذج نوع المرفق
    """
    name = StringField('اسم نوع المرفق', validators=[
        DataRequired(message='يرجى إدخال اسم نوع المرفق'),
        Length(max=100, message='يجب أن يكون اسم نوع المرفق أقل من 100 حرف')
    ])
    # تم إزالة حقول الوصف والأيقونة والترتيب بناءً على طلب المستخدم
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

class FacilityCheckItemForm(FlaskForm):
    """
    نموذج عنصر فحص المرفق
    """
    name = StringField('اسم العنصر', validators=[
        DataRequired(message='يرجى إدخال اسم العنصر'),
        Length(max=100, message='يجب أن يكون اسم العنصر أقل من 100 حرف')
    ])
    # تم إزالة حقلي الوصف والترتيب بناءً على طلب المستخدم
    # تم إخفاء حقل الفئة ولكن لا نزال نحتفظ به للتوافق مع قاعدة البيانات
    category_id = SelectField('الفئة', coerce=int, validators=[Optional()], render_kw={'style': 'display: none;'})
    is_required = BooleanField('مطلوب للفحص', default=True)
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

class FacilityCheckResultForm(FlaskForm):
    """
    نموذج نتيجة فحص عنصر
    """
    status = SelectField('الحالة', choices=[
        ('not_checked', 'لم يتم الفحص'),
        ('passed', 'مطابق'),
        ('failed', 'غير مطابق'),
        ('na', 'لا ينطبق')
    ])
    value = StringField('القيمة', validators=[Optional()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    image = FileField('صورة', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'يجب أن تكون الصورة بصيغة JPG أو PNG')
    ])

class FacilityCheckForm(FlaskForm):
    """
    نموذج فحص المرفق
    """
    notes = TextAreaField('ملاحظات عامة', validators=[Optional()])
    submit = SubmitField('حفظ نتائج الفحص')

class FacilityTypeItemForm(FlaskForm):
    """
    نموذج بند نوع المرفق
    """
    name = StringField('اسم البند', validators=[
        DataRequired(message='يرجى إدخال اسم البند'),
        Length(max=100, message='يجب أن يكون اسم البند أقل من 100 حرف')
    ])
    description = TextAreaField('الوصف', validators=[Optional()])
    is_required = BooleanField('مطلوب للفحص', default=True)
    is_active = BooleanField('نشط', default=True)
    submit = SubmitField('حفظ')

class FacilityTypeItemImportForm(FlaskForm):
    """
    نموذج استيراد بنود نوع المرفق من ملف إكسيل
    """
    excel_file = FileField('ملف الإكسيل', validators=[
        DataRequired(message='يرجى اختيار ملف إكسيل'),
        FileAllowed(['xlsx', 'xls'], 'يجب أن يكون الملف بصيغة Excel (.xlsx أو .xls)')
    ])
    submit = SubmitField('استيراد')
