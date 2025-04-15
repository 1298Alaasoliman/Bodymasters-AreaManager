import pandas as pd
from app import db

def import_from_excel(file, model_class, columns_mapping=None, unique_field=None):
    """
    استيراد بيانات من ملف Excel إلى قاعدة البيانات
    
    Args:
        file: ملف Excel
        model_class: فئة النموذج المراد استيراد البيانات إليه
        columns_mapping: قاموس يحتوي على تعيين أعمدة Excel إلى حقول النموذج
        unique_field: اسم الحقل الذي يجب أن يكون فريدًا
        
    Returns:
        عدد السجلات التي تم استيرادها
    """
    try:
        # قراءة ملف Excel
        df = pd.read_excel(file)
        
        # التحقق من وجود الأعمدة المطلوبة
        if columns_mapping:
            excel_columns = list(columns_mapping.keys())
            if not all(col in df.columns for col in excel_columns):
                missing_columns = [col for col in excel_columns if col not in df.columns]
                raise ValueError(f"الأعمدة التالية مفقودة في الملف: {', '.join(missing_columns)}")
        
        # استيراد البيانات
        count = 0
        for _, row in df.iterrows():
            # إنشاء قاموس البيانات
            data = {}
            if columns_mapping:
                for excel_col, model_field in columns_mapping.items():
                    if excel_col in df.columns:
                        value = row[excel_col]
                        # التعامل مع القيم الفارغة
                        if pd.isna(value):
                            value = None
                        data[model_field] = value
            else:
                # استخدام أسماء الأعمدة كما هي
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        value = None
                    data[col] = value
            
            # التحقق من عدم وجود السجل مسبقًا
            if unique_field and unique_field in data and data[unique_field]:
                existing = model_class.query.filter_by(**{unique_field: data[unique_field]}).first()
                if existing:
                    continue
            
            # إنشاء كائن جديد وإضافته إلى قاعدة البيانات
            new_record = model_class(**data)
            db.session.add(new_record)
            count += 1
        
        # حفظ التغييرات
        db.session.commit()
        
        return count
    except Exception as e:
        # التراجع عن التغييرات في حالة حدوث خطأ
        db.session.rollback()
        raise e
