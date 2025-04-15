#!/bin/bash
echo "=== إعداد نظام إدارة النوادي الرياضية ==="

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

# تشغيل برنامج الإعداد
echo "تشغيل برنامج الإعداد..."
python setup.py
