from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional

class VisitForm(FlaskForm):
    """
    نموذج زيارة الفرع
    """
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    visit_date = DateTimeField('تاريخ ووقت الزيارة', validators=[
        DataRequired(message='يرجى إدخال تاريخ ووقت الزيارة')
    ], format='%Y-%m-%d %H:%M')
    purpose = StringField('الغرض من الزيارة', validators=[
        DataRequired(message='يرجى إدخال الغرض من الزيارة'),
        Length(max=255, message='يجب أن يكون الغرض من الزيارة أقل من 255 حرف')
    ])
    notes = TextAreaField('ملاحظات', validators=[Optional()])
    submit = SubmitField('حفظ')
