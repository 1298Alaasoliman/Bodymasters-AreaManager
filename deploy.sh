#!/bin/bash

# سكريبت نشر التطبيق

# تحديث الكود من Git
echo "Updating code from Git..."
git pull

# تحديث البيئة الافتراضية
echo "Updating virtual environment..."
source venv/bin/activate
pip install -r requirements.txt

# تحديث قاعدة البيانات
echo "Updating database..."
flask db upgrade

# إعادة تشغيل التطبيق
echo "Restarting application..."
sudo supervisorctl restart areamanagerbag

echo "Deployment completed successfully!"
