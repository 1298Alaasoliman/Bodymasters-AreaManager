from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Optional

class CameraCheckForm(FlaskForm):
    """
    نموذج فحص الكاميرات
    """
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    check_time = DateTimeField('وقت الفحص', validators=[
        DataRequired(message='يرجى إدخال وقت الفحص')
    ], format='%Y-%m-%d %H:%M')
    status = BooleanField('تعمل بشكل صحيح')
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')
