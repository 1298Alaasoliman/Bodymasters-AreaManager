from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from datetime import datetime

class RevenueCategoryForm(FlaskForm):
    """
    نموذج فئة الإيرادات
    """
    name = StringField('اسم الفئة', validators=[
        DataRequired(message='يرجى إدخال اسم الفئة'),
        Length(max=100, message='يجب أن يكون اسم الفئة أقل من 100 حرف')
    ])
    description = TextAreaField('الوصف', validators=[Optional()])
    submit = SubmitField('حفظ')

class MonthlyTargetForm(FlaskForm):
    """
    نموذج إدخال التارجت الشهري
    """
    club_id = SelectField('النادي', validators=[DataRequired(message='يرجى اختيار النادي')], coerce=int)
    month = SelectField('الشهر', validators=[DataRequired(message='يرجى اختيار الشهر')], coerce=int, choices=[
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ], default=datetime.now().month)
    year = StringField('السنة', validators=[DataRequired(message='يرجى إدخال السنة')],
                        default=str(datetime.now().year), render_kw={"readonly": True, "inputmode": "numeric", "pattern": "[0-9]*", "dir": "ltr", "class": "text-center"})
    target_amount = FloatField('مبلغ التارجت', validators=[DataRequired(message='يرجى إدخال مبلغ التارجت'), NumberRange(min=0, message='يجب أن يكون المبلغ أكبر من أو يساوي صفر')])
    submit = SubmitField('حفظ')

class DailyRevenueForm(FlaskForm):
    """
    نموذج إدخال الإيراد اليومي
    """
    club_id = SelectField('النادي', validators=[DataRequired(message='يرجى اختيار النادي')], coerce=int)
    date = DateField('التاريخ', validators=[DataRequired(message='يرجى إدخال التاريخ')], format='%d/%m/%Y',
                     default=datetime.now().date())
    amount = FloatField('المبلغ', validators=[DataRequired(message='يرجى إدخال المبلغ'), NumberRange(min=0, message='يجب أن يكون المبلغ أكبر من أو يساوي صفر')])
    submit = SubmitField('حفظ')

    def validate_date(self, field):
        # التحقق من أن التاريخ لا يكون أكبر من تاريخ اليوم
        today = datetime.now().date()
        if field.data > today:
            raise ValidationError('لا يمكن تسجيل إيراد بتاريخ مستقبلي')

class RevenueForm(FlaskForm):
    """
    نموذج الإيرادات
    """
    club_id = SelectField('النادي', coerce=int, validators=[
        DataRequired(message='يرجى اختيار النادي')
    ])
    category_id = SelectField('الفئة', coerce=int, validators=[
        DataRequired(message='يرجى اختيار الفئة')
    ])
    date = DateField('التاريخ', validators=[
        DataRequired(message='يرجى إدخال التاريخ')
    ], format='%Y-%m-%d')
    amount = FloatField('المبلغ', validators=[
        DataRequired(message='يرجى إدخال المبلغ'),
        NumberRange(min=0, message='يجب أن يكون المبلغ أكبر من أو يساوي صفر')
    ])
    description = TextAreaField('الوصف', validators=[Optional()])
    submit = SubmitField('حفظ')
