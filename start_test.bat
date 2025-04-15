@echo off
echo === بدء إعداد وتشغيل النظام ===

REM إعداد البيئة أولاً
if not exist venv (
    echo إنشاء البيئة الافتراضية...
    python -m venv venv
)

REM تفعيل البيئة الافتراضية
call venv\Scripts\activate

REM تثبيت المتطلبات
pip install -r requirements.txt

REM تشغيل الخادم البسيط
python simple_server.py

REM فتح صفحة الاختبار
start test.html
