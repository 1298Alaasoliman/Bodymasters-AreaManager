@echo off
echo === بدء تشغيل وفحص النظام ===

REM إيقاف كافة عمليات Python
echo تنظيف العمليات السابقة...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak > nul

REM التحقق من المنفذ 5000
echo فحص المنفذ 5000...
netstat -ano | findstr :5000 > nul
if %errorlevel% equ 0 (
    echo تحرير المنفذ 5000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do taskkill /F /PID %%a
)

REM تفعيل البيئة الافتراضية
echo تفعيل البيئة الافتراضية...
call venv\Scripts\activate

REM تثبيت المتطلبات
echo تثبيت المتطلبات...
pip install -r requirements.txt

REM تعيين متغيرات البيئة
echo تعيين متغيرات البيئة...
set FLASK_APP=app
set FLASK_ENV=development
set FLASK_DEBUG=1

REM تشغيل التطبيق مباشرة (بدون start)
echo جاري تشغيل التطبيق...
python -m flask run --host=0.0.0.0 --port=5000

