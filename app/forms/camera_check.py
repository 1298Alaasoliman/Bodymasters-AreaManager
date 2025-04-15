from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class CameraCheckForm(FlaskForm):
    """
    نموذج فحص الكاميرات
    """
    club_id = SelectField('النادي', validators=[DataRequired()])

    opening_check = BooleanField('الافتتاح')
    check_12 = BooleanField('12:00')
    check_2 = BooleanField('02:00')
    check_3 = BooleanField('03:00')
    check_5 = BooleanField('05:00')
    check_8 = BooleanField('08:00')
    check_10 = BooleanField('10:00')
    check_11 = BooleanField('11:00')
    check_1150 = BooleanField('11:50')

    violations_count = IntegerField('عدد المخالفات', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('ملاحظات', validators=[Optional()])

    submit = SubmitField('حفظ')
