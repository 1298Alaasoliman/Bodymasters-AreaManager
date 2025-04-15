import pandas as pd
import os

# إنشاء بيانات نموذجية
data = {
    'name': ['عنصر فحص 1', 'عنصر فحص 2', 'عنصر فحص 3'],
    'description': ['وصف العنصر الأول', 'وصف العنصر الثاني', 'وصف العنصر الثالث'],
    'order': [1, 2, 1],
    'is_required': ['نعم', 'لا', 'نعم']
}

# إنشاء DataFrame
df = pd.DataFrame(data)

# إنشاء مجلد للقوالب إذا لم يكن موجوداً
os.makedirs('app/static/templates', exist_ok=True)

# حفظ الملف
excel_path = 'app/static/templates/check_items_template.xlsx'
df.to_excel(excel_path, index=False)

print(f'تم إنشاء قالب Excel بنجاح: {excel_path}')
