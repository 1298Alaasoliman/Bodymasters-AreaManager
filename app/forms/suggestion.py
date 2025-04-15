from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class SuggestionForm(FlaskForm):
    """
    نموذج الاقتراح
    """
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    type = SelectField('النوع', choices=[
        ('improvement', 'اقتراح تطوير'),
        ('negative', 'ملاحظة سلبية'),
        ('positive', 'ملاحظة إيجابية'),
        ('other', 'أخرى')
    ], validators=[DataRequired(message='يرجى اختيار النوع')])
    title = StringField('العنوان', validators=[
        DataRequired(message='يرجى إدخال العنوان'),
        Length(max=255, message='يجب أن يكون العنوان أقل من 255 حرف')
    ])
    content = TextAreaField('المحتوى', validators=[
        DataRequired(message='يرجى إدخال المحتوى')
    ])
    submit = SubmitField('إرسال')

class SuggestionResponseForm(FlaskForm):
    """
    نموذج الرد على الاقتراح
    """
    status = SelectField('الحالة', choices=[
        ('pending', 'قيد الانتظار'),
        ('in_review', 'قيد المراجعة'),
        ('implemented', 'تم التنفيذ'),
        ('rejected', 'مرفوض')
    ], validators=[DataRequired(message='يرجى اختيار الحالة')])
    response = TextAreaField('الرد', validators=[
        DataRequired(message='يرجى إدخال الرد')
    ])
    submit = SubmitField('حفظ الرد')
