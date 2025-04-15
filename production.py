from waitress import serve
from app import create_app
import locale
import os
import logging

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
    # تعيين اللغة الإنجليزية للتاريخ
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    os.environ['LC_TIME'] = 'en_US.UTF-8'
    logger.info(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
except Exception as e:
    logger.error(f"Error setting locale: {e}")
    try:
        # محاولة تعيين اللغة الإنجليزية للتاريخ
        locale.setlocale(locale.LC_TIME, 'English_United States.1252')
        logger.info(f"Locale set to: {locale.getlocale(locale.LC_TIME)}")
    except Exception as e:
        logger.error(f"Error setting locale: {e}")

# إنشاء التطبيق
app = create_app()

def start_server(port=5000):
    try:
        logger.info(f"Starting server with Waitress on http://127.0.0.1:{port}")
        serve(app, host='127.0.0.1', port=port, threads=4,
              connection_limit=100, channel_timeout=60,
              clear_untrusted_proxy_headers=True,
              url_scheme='http', ident='AreaManager')
    except Exception as e:
        logger.error(f"Server error: {e}")
        # محاولة منفذ آخر إذا فشل المنفذ الحالي
        if port == 5000:
            logger.info("Trying alternate port 8000...")
            start_server(8000)
        elif port == 8000:
            logger.info("Trying alternate port 3000...")
            start_server(3000)
        else:
            logger.error("All ports failed. Please check your network configuration.")

if __name__ == '__main__':
    start_server()
