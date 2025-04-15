#!/bin/bash
echo "=== تشغيل نظام إدارة النوادي الرياضية ==="

# التحقق من وجود البيئة الافتراضية
if [ ! -d "venv" ]; then
    echo "إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تثبيت المتطلبات
echo "تثبيت المتطلبات..."
pip install -r requirements.txt

# تشغيل التطبيق
echo "تشغيل التطبيق..."
python run.py
