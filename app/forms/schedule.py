from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, TimeField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from datetime import time

class ScheduleForm(FlaskForm):
    """
    نموذج جدول الدوامات
    """
    # أيام الدوام
    saturday = BooleanField('السبت')
    sunday = BooleanField('الأحد')
    monday = BooleanField('الإثنين')
    tuesday = BooleanField('الثلاثاء')
    wednesday = BooleanField('الأربعاء')
    thursday = BooleanField('الخميس')
    friday = BooleanField('الجمعة')

    # نوع الدوام
    shift_type = SelectField('نوع الدوام', choices=[
        ('single', 'فترة واحدة'),
        ('double', 'فترتين'),
        ('7hours', 'دوام 7 ساعات'),
        ('8hours', 'دوام 8 ساعات')
    ], validators=[DataRequired(message='يرجى اختيار نوع الدوام')])

    # قائمة خيارات أوقات الدوام
    TIME_CHOICES = [
        ('', '-- اختر الوقت --'),
        ('06:00', '06:00 صباحاً'),
        ('07:00', '07:00 صباحاً'),
        ('08:00', '08:00 صباحاً'),
        ('09:00', '09:00 صباحاً'),
        ('10:00', '10:00 صباحاً'),
        ('11:00', '11:00 صباحاً'),
        ('12:00', '12:00 ظهراً'),
        ('13:00', '01:00 مساءً'),
        ('14:00', '02:00 مساءً'),
        ('15:00', '03:00 مساءً'),
        ('16:00', '04:00 مساءً'),
        ('17:00', '05:00 مساءً'),
        ('18:00', '06:00 مساءً'),
        ('19:00', '07:00 مساءً'),
        ('20:00', '08:00 مساءً'),
        ('21:00', '09:00 مساءً'),
        ('22:00', '10:00 مساءً'),
        ('23:00', '11:00 مساءً'),
        ('00:00', '12:00 منتصف الليل')
    ]

    # الفترة الأولى
    shift1_start = SelectField('بداية الفترة الأولى', choices=TIME_CHOICES, validators=[Optional()])
    shift1_end = SelectField('نهاية الفترة الأولى', choices=TIME_CHOICES, validators=[Optional()])

    # الفترة الثانية
    shift2_start = SelectField('بداية الفترة الثانية', choices=TIME_CHOICES, validators=[Optional()])
    shift2_end = SelectField('نهاية الفترة الثانية', choices=TIME_CHOICES, validators=[Optional()])

    # يوم التخصيص
    DAYS_CHOICES = [
        ('', '-- اختر اليوم --'),
        ('السبت', 'السبت'),
        ('الأحد', 'الأحد'),
        ('الإثنين', 'الإثنين'),
        ('الثلاثاء', 'الثلاثاء'),
        ('الأربعاء', 'الأربعاء'),
        ('الخميس', 'الخميس'),
        ('الجمعة', 'الجمعة')
    ]

    specific_day = SelectField('يوم التخصيص', choices=DAYS_CHOICES, validators=[Optional()])
    specific_day_start = SelectField('بداية الدوام', choices=TIME_CHOICES, validators=[Optional()])
    specific_day_end = SelectField('نهاية الدوام', choices=TIME_CHOICES, validators=[Optional()])

    # ملاحظات
    notes = TextAreaField('ملاحظات', validators=[Optional()])

    submit = SubmitField('حفظ')
