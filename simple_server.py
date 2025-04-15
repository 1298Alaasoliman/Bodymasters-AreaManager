from app import create_app
import logging
import os
import locale
import sys

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# تعيين اللغة الإنجليزية للتاريخ
try:
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    os.environ['LC_TIME'] = 'en_US.UTF-8'
    logger.info(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
except Exception as e:
    logger.error(f"Error setting locale: {e}")
    try:
        locale.setlocale(locale.LC_TIME, 'English_United States.1252')
        logger.info(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
    except Exception as e:
        logger.error(f"Error setting locale: {e}")

# إنشاء التطبيق
app = create_app()

if __name__ == '__main__':
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    logger.info(f"Starting Flask development server on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True, threaded=False, processes=1)

