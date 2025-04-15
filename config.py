import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env إذا كان موجودًا
load_dotenv()

class Config:
    """
    فئة التكوين الأساسية للتطبيق
    """
    # مفتاح سري للتطبيق (يستخدم في توقيع الجلسات وغيرها)
    # استخدام مفتاح سري قوي في الإنتاج
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a8e7d1c6b3f9e2a5d8c7b4f1e0a3d6c9b2e5f8a7d4c1b0e3f6a9d2c5b8e1f4a7'

    # تكوين قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # إعدادات لزيادة استقرار الاتصال
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_timeout': 100,
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False},
        'echo': False
    }
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 30

    # إعدادات الجلسة
    PERMANENT_SESSION_LIFETIME = 3600  # مدة الجلسة بالثواني (1 ساعة)
    SESSION_TYPE = 'filesystem'
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = True

    # تكوين البريد الإلكتروني (إذا كان مطلوبًا لإعادة تعيين كلمة المرور)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['admin@example.com']  # قائمة البريد الإلكتروني للمسؤولين
