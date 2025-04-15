@echo off
echo === تشغيل نظام إدارة النوادي الرياضية ===

REM التحقق من وجود البيئة الافتراضية
if not exist venv (
    echo إنشاء البيئة الافتراضية...
    python -m venv venv
)

REM تفعيل البيئة الافتراضية
call venv\Scripts\activate

REM تثبيت المتطلبات
echo تثبيت المتطلبات...
pip install -r requirements.txt

REM تشغيل التطبيق
echo تشغيل التطبيق...
python run.py

pause
