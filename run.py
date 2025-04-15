from app import create_app, db
from app.models.user import User
import locale
import os

# تعيين اللغة الإنجليزية للتاريخ
try:
    # تعيين اللغة الإنجليزية للتاريخ
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    os.environ['LC_TIME'] = 'en_US.UTF-8'
    print(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
except Exception as e:
    print(f"Error setting locale: {e}")
    try:
        # محاولة تعيين اللغة الإنجليزية للتاريخ
        locale.setlocale(locale.LC_TIME, 'English_United States.1252')
        print(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
    except Exception as e:
        print(f"Error setting locale: {e}")

# تم تعطيل استيراد init_db لأنه يعتمد على مكتبة click
# import init_db

app = create_app()
# init_db.init_app(app)

@app.shell_context_processor
def make_shell_context():
    """
    توفير سياق للصدفة التفاعلية
    """
    return {'db': db, 'User': User}

if __name__ == '__main__':
    # استخدام متغير بيئي للتحكم في وضع التصحيح
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, port=int(os.environ.get('PORT', 8080)), host='0.0.0.0', threaded=True)
