import os
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix

# إنشاء كائنات التطبيق
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
csrf = CSRFProtect()
sess = Session()

def create_app(config_class=Config):
    """
    دالة إنشاء التطبيق
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # إعداد التسجيل
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # إعداد ProxyFix لتحسين التعامل مع الطلبات
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # إضافة رؤوس أمان HTTP
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data:;"
        return response

    # تهيئة الإضافات مع التطبيق
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    sess.init_app(app)

    # إضافة دالة min إلى بيئة Jinja2
    app.jinja_env.globals.update(min=min)

    # تسجيل البلوبرنت (Blueprints)
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.clubs import bp as clubs_bp
    app.register_blueprint(clubs_bp, url_prefix='/clubs')

    from app.routes.facilities import bp as facilities_bp
    app.register_blueprint(facilities_bp, url_prefix='/facilities')

    from app.routes.facility_types import facility_types_bp
    app.register_blueprint(facility_types_bp)

    from app.routes.facility_type_items import facility_type_items_bp
    app.register_blueprint(facility_type_items_bp)

    from app.routes.employees import bp as employees_bp
    app.register_blueprint(employees_bp, url_prefix='/employees')

    # المسارات التالية سيتم تفعيلها لاحقًا عند إنشاء الملفات
    from app.routes.issues import bp as issues_bp
    app.register_blueprint(issues_bp, url_prefix='/issues')

    try:
        from app.routes.create_issue import bp as create_issue_bp
        app.register_blueprint(create_issue_bp, url_prefix='/issues')
        print("Successfully registered create_issue blueprint")
    except Exception as e:
        print(f"Error registering create_issue blueprint: {str(e)}")
    from app.routes.violations import violations_bp
    app.register_blueprint(violations_bp)
    # from app.routes.cameras import bp as cameras_bp
    # app.register_blueprint(cameras_bp, url_prefix='/cameras')
    #
    # from app.routes.visits import bp as visits_bp
    # app.register_blueprint(visits_bp, url_prefix='/visits')
    #
    # from app.routes.suggestions import bp as suggestions_bp
    # app.register_blueprint(suggestions_bp, url_prefix='/suggestions')
    #
    from app.routes.revenue import bp as revenue_bp
    app.register_blueprint(revenue_bp, url_prefix='/revenue')

    from app.routes.daily_revenue import bp as daily_revenue_bp
    app.register_blueprint(daily_revenue_bp, url_prefix='/daily_revenue')

    from app.routes.schedules import bp as schedules_bp
    app.register_blueprint(schedules_bp, url_prefix='/schedules')

    from app.routes.camera_checks import bp as camera_checks_bp
    app.register_blueprint(camera_checks_bp, url_prefix='/camera_checks')

    from app.routes.check_reports import bp as check_reports_bp
    app.register_blueprint(check_reports_bp, url_prefix='/check_reports')

    from app.routes.facility_quality import bp as facility_quality_bp
    app.register_blueprint(facility_quality_bp, url_prefix='/facility_quality')

    from app.routes.shomoos import bp as shomoos_bp
    app.register_blueprint(shomoos_bp, url_prefix='/shomoos')

    # إنشاء جميع الجداول في قاعدة البيانات إذا لم تكن موجودة
    with app.app_context():
        db.create_all()

    # إنشاء مجلدات الصور
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(os.path.join(uploads_dir, 'checks'), exist_ok=True)

    return app

# استيراد نماذج قاعدة البيانات
from app.models import user, club, facility, employee, work_tracking, schedule, violation

