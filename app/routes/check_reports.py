from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.facility import FacilityCheck, Facility, FacilityCheckResult
from app.models.camera_check import CameraCheck
from app.models.violation import Violation
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

bp = Blueprint('check_reports', __name__)

@bp.route('/')
@login_required
def index():
    # طباعة جميع تشيكات المرافق والكاميرات في قاعدة البيانات
    all_facility_checks = FacilityCheck.query.all()
    all_camera_checks = CameraCheck.query.all()
    print(f"\n\nALL CHECKS IN DATABASE:")
    print(f"Total facility checks: {len(all_facility_checks)}")
    for check in all_facility_checks:
        print(f"Facility Check ID: {check.id}, Date: {check.check_date}, Facility ID: {check.facility_id}, Violations: {check.violations_count}")
    print(f"\nTotal camera checks: {len(all_camera_checks)}")
    for check in all_camera_checks:
        print(f"Camera Check ID: {check.id}, Date: {check.check_date}, Club ID: {check.club_id}, Violations: {check.violations_count}")
    """
    صفحة تقارير التشيك الرئيسية
    """
    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    # الحصول على الفترة الزمنية (افتراضيًا آخر 30 يوم)
    # إضافة يوم واحد للتأكد من تضمين اليوم الحالي
    end_date = datetime.now().date() + timedelta(days=1)
    start_date = end_date - timedelta(days=31)  # 30 يوم + يوم إضافي

    print(f"\n\nDefault date range: {start_date} to {end_date}")

    # الحصول على الفترة من الطلب إذا كانت موجودة
    if request.args.get('start_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            start_date = datetime.strptime(request.args.get('start_date'), '%d/%m/%Y').date()
            print(f"Custom start date: {start_date}")
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
                print(f"Custom start date (old format): {start_date}")
            except ValueError:
                print(f"Invalid start date format: {request.args.get('start_date')}")
                pass

    if request.args.get('end_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            end_date_parsed = datetime.strptime(request.args.get('end_date'), '%d/%m/%Y').date()
            # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
            end_date = end_date_parsed + timedelta(days=1)
            print(f"Custom end date: {end_date} (added 1 day to include the selected date)")
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                end_date_parsed = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
                # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
                end_date = end_date_parsed + timedelta(days=1)
                print(f"Custom end date (old format): {end_date} (added 1 day to include the selected date)")
            except ValueError:
                print(f"Invalid end date format: {request.args.get('end_date')}")
                pass

    # الحصول على معرف النادي من الطلب إذا كان موجودًا
    club_id = request.args.get('club_id', type=int)

    # إحصائيات التشيك للمرافق
    facility_stats = {}

    # إحصائيات تشيك الكاميرات
    camera_stats = {}

    # إذا تم تحديد نادي معين
    if club_id:
        # التحقق من صلاحية الوصول إلى النادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            return jsonify({'error': 'ليس لديك صلاحية للوصول إلى هذا النادي'}), 403

        # الحصول على إحصائيات التشيك للمرافق
        # الحصول على جميع المرافق للنادي المحدد
        club_facilities = Facility.query.filter_by(club_id=club_id).all()
        club_facility_ids = [facility.id for facility in club_facilities]

        # الحصول على جميع تشيكات المرافق للنادي المحدد
        facility_checks = FacilityCheck.query.filter(
            FacilityCheck.facility_id.in_(club_facility_ids),
            FacilityCheck.check_date >= start_date,
            FacilityCheck.check_date <= end_date
        ).all()

        # طباعة معلومات تشيكات المرافق للتصحيح
        print(f"\n\nFacility Checks for club {club_id} from {start_date} to {end_date}:")
        print(f"Total facility checks found: {len(facility_checks)}")
        for check in facility_checks:
            print(f"Facility Check ID: {check.id}, Date: {check.check_date}, Violations: {check.violations_count}")

        # الحصول على إحصائيات تشيك الكاميرات
        camera_checks = CameraCheck.query.filter(
            CameraCheck.club_id == club_id,
            CameraCheck.check_date >= start_date,
            CameraCheck.check_date <= end_date
        ).all()

        # الحصول على عدد المخالفات النظامية للنادي
        violations = Violation.query.filter(
            Violation.club_id == club_id,
            Violation.violation_date >= start_date,
            Violation.violation_date <= end_date
        ).all()

        # طباعة معلومات تشيكات الكاميرات للتصحيح
        print(f"\nCamera Checks for club {club_id} from {start_date} to {end_date}:")
        print(f"Total camera checks found: {len(camera_checks)}")
        for check in camera_checks:
            print(f"Camera Check ID: {check.id}, Date: {check.check_date}, Violations: {check.violations_count}")

        # طباعة معلومات المخالفات النظامية للتصحيح
        print(f"\nViolations for club {club_id} from {start_date} to {end_date}:")
        print(f"Total violations found: {len(violations)}")

        # حساب عدد التشيكات والمخالفات
        facility_stats = {
            'total_checks': len(facility_checks),
            'total_violations': sum(check.violations_count or 0 for check in facility_checks)
        }

        camera_stats = {
            'total_checks': len(camera_checks),
            'total_violations': sum(check.violations_count or 0 for check in camera_checks),
            'legal_violations': len(violations)  # إضافة عدد المخالفات النظامية
        }

        # طباعة الإحصائيات النهائية بعد الحساب
        print(f"\nFinal Stats after calculation:")
        print(f"Facility Stats: {facility_stats}")
        print(f"Camera Stats: {camera_stats}")

        # طباعة الإحصائيات النهائية
        print(f"\nFinal Stats for club {club_id}:")
        print(f"Facility Stats: {facility_stats}")
        print(f"Camera Stats: {camera_stats}")
    else:
        # الحصول على إحصائيات التشيك للمرافق لجميع النوادي المتاحة
        club_ids = [club.id for club in clubs]

        # الحصول على جميع المرافق للنوادي المتاحة
        all_facilities = Facility.query.filter(Facility.club_id.in_(club_ids)).all()
        all_facility_ids = [facility.id for facility in all_facilities]

        # الحصول على جميع تشيكات المرافق للنوادي المتاحة
        facility_checks = FacilityCheck.query.filter(
            FacilityCheck.facility_id.in_(all_facility_ids),
            FacilityCheck.check_date >= start_date,
            FacilityCheck.check_date <= end_date
        ).all()

        # طباعة معلومات تشيكات المرافق للتصحيح
        print(f"\n\nFacility Checks for all clubs from {start_date} to {end_date}:")
        print(f"Total facility checks found: {len(facility_checks)}")
        for check in facility_checks:
            print(f"Facility Check ID: {check.id}, Date: {check.check_date}, Facility ID: {check.facility_id}, Violations: {check.violations_count}")

        camera_checks = CameraCheck.query.filter(
            CameraCheck.club_id.in_(club_ids),
            CameraCheck.check_date >= start_date,
            CameraCheck.check_date <= end_date
        ).all()

        # الحصول على المخالفات النظامية لجميع النوادي
        violations = Violation.query.filter(
            Violation.club_id.in_(club_ids),
            Violation.violation_date >= start_date,
            Violation.violation_date <= end_date
        ).all()

        # طباعة معلومات المخالفات النظامية للتصحيح
        print(f"\nViolations for all clubs from {start_date} to {end_date}:")
        print(f"Total violations found: {len(violations)}")

        # حساب إحصائيات لكل نادي
        for club in clubs:
            club_facility_checks = [check for check in facility_checks if check.facility.club_id == club.id]
            club_camera_checks = [check for check in camera_checks if check.club_id == club.id]
            club_violations = [v for v in violations if v.club_id == club.id]

            # طباعة معلومات النادي
            print(f"\nStats for club {club.name} (ID: {club.id}):")
            print(f"Facility checks: {len(club_facility_checks)}")
            print(f"Camera checks: {len(club_camera_checks)}")
            print(f"Legal violations: {len(club_violations)}")

            # حساب المخالفات
            # حساب عدد البنود غير المتطابقة لإجمالي التشيكات للنادي
            # استخدام جدول FacilityCheckResult لحساب عدد البنود غير المتطابقة
            facility_violations = 0
            for check in club_facility_checks:
                # الحصول على نتائج الفحص لهذا التشيك
                failed_results = FacilityCheckResult.query.filter_by(
                    facility_check_id=check.id,
                    status='failed'
                ).count()
                facility_violations += failed_results

            camera_violations = sum(check.violations_count or 0 for check in club_camera_checks)

            print(f"Facility violations: {facility_violations}")
            print(f"Camera violations: {camera_violations}")

            facility_stats[club.id] = {
                'name': club.name,
                'total_checks': len(club_facility_checks),
                'total_violations': facility_violations
            }

            camera_stats[club.id] = {
                'name': club.name,
                'total_checks': len(club_camera_checks),
                'total_violations': camera_violations,
                'legal_violations': len(club_violations)  # إضافة عدد المخالفات النظامية
            }

    # حساب إحصائيات التشيك حسب اليوم
    daily_stats = {}

    # طباعة معلومات للتصحيح
    print("\n\nCalculating daily stats...")

    # تحويل التاريخ إلى سلسلة نصية للمفتاح
    for check in facility_checks:
        date_str = check.check_date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'facility_checks': 0,
                'facility_violations': 0,
                'camera_checks': 0,
                'camera_violations': 0,
                'legal_violations': 0  # إضافة عدد المخالفات النظامية
            }
        daily_stats[date_str]['facility_checks'] += 1

        # استخدام جدول FacilityCheckResult لحساب عدد البنود غير المتطابقة
        failed_results = FacilityCheckResult.query.filter_by(
            facility_check_id=check.id,
            status='failed'
        ).count()

        daily_stats[date_str]['facility_violations'] += failed_results
        print(f"Added facility violations for date {date_str}: {failed_results}")
        print(f"Added facility check for date {date_str}: checks={daily_stats[date_str]['facility_checks']}, violations={daily_stats[date_str]['facility_violations']}")

    for check in camera_checks:
        date_str = check.check_date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'facility_checks': 0,
                'facility_violations': 0,
                'camera_checks': 0,
                'camera_violations': 0,
                'legal_violations': 0  # إضافة عدد المخالفات النظامية
            }
        daily_stats[date_str]['camera_checks'] += 1
        violations_count = check.violations_count or 0
        daily_stats[date_str]['camera_violations'] += violations_count
        print(f"Added camera violations for date {date_str}: {violations_count}")
        print(f"Added camera check for date {date_str}: checks={daily_stats[date_str]['camera_checks']}, violations={daily_stats[date_str]['camera_violations']}")

    # إضافة المخالفات النظامية إلى الإحصائيات اليومية
    for violation in violations:
        date_str = violation.violation_date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'facility_checks': 0,
                'facility_violations': 0,
                'camera_checks': 0,
                'camera_violations': 0,
                'legal_violations': 0
            }
        daily_stats[date_str]['legal_violations'] += 1
        print(f"Added legal violation for date {date_str}")

    # تحويل daily_stats إلى قائمة مرتبة حسب التاريخ
    daily_stats_list = [{'date': date, **stats} for date, stats in daily_stats.items()]
    daily_stats_list.sort(key=lambda x: x['date'])

    # طباعة الإحصائيات اليومية النهائية
    print("\nFinal daily stats:")
    for day in daily_stats_list:
        print(f"Date: {day['date']}, Facility Checks: {day['facility_checks']}, Facility Violations: {day['facility_violations']}, Camera Checks: {day['camera_checks']}, Camera Violations: {day['camera_violations']}")

    # طباعة المتغيرات التي سيتم تمريرها إلى القالب
    print("\n\nVariables being passed to template:")
    print(f"clubs: {clubs}")
    print(f"selected_club_id: {club_id}")
    print(f"start_date: {start_date.strftime('%Y-%m-%d')}")
    print(f"end_date: {end_date.strftime('%Y-%m-%d')}")
    print(f"facility_stats: {facility_stats}")
    print(f"camera_stats: {camera_stats}")
    print(f"daily_stats_list: {daily_stats_list}")

    # إرجاع تاريخ النهاية إلى اليوم السابق لعرضه في القالب
    display_end_date = end_date - timedelta(days=1)

    # طباعة التواريخ النهائية التي سيتم عرضها
    print(f"\n\nDates being displayed in template:")
    print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
    print(f"End date: {display_end_date.strftime('%Y-%m-%d')} (actual end date used in queries: {end_date.strftime('%Y-%m-%d')})")

    # تحديد ما إذا كانت التواريخ محددة من قبل المستخدم
    has_date_filter = 'start_date' in request.args or 'end_date' in request.args

    # إذا لم يتم تحديد التواريخ، نجعلها فارغة
    start_date_str = start_date.strftime('%d/%m/%Y') if has_date_filter else ''
    end_date_str = display_end_date.strftime('%d/%m/%Y') if has_date_filter else ''

    print(f"Start date string: {start_date_str}")
    print(f"End date string: {end_date_str}")

    return render_template('check_reports/index.html',
                           title='تقارير التشيك',
                           clubs=clubs,
                           selected_club_id=club_id,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           facility_stats=facility_stats,
                           camera_stats=camera_stats,
                           daily_stats=daily_stats_list)

@bp.route('/api/chart-data')
@login_required
def chart_data():
    """
    API لبيانات الرسم البياني
    """
    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    club_ids = [club.id for club in clubs]

    # الحصول على الفترة الزمنية (افتراضيًا آخر 30 يوم)
    # إضافة يوم واحد للتأكد من تضمين اليوم الحالي
    end_date = datetime.now().date() + timedelta(days=1)
    start_date = end_date - timedelta(days=31)  # 30 يوم + يوم إضافي

    print(f"\n\nChart data - Default date range: {start_date} to {end_date}")

    # الحصول على الفترة من الطلب إذا كانت موجودة
    if request.args.get('start_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            start_date = datetime.strptime(request.args.get('start_date'), '%d/%m/%Y').date()
            print(f"Chart data - Custom start date: {start_date}")
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
                print(f"Chart data - Custom start date (old format): {start_date}")
            except ValueError:
                print(f"Chart data - Invalid start date format: {request.args.get('start_date')}")
                pass

    if request.args.get('end_date'):
        try:
            # محاولة تحليل التاريخ بتنسيق dd/mm/yyyy
            end_date_parsed = datetime.strptime(request.args.get('end_date'), '%d/%m/%Y').date()
            # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
            end_date = end_date_parsed + timedelta(days=1)
            print(f"Chart data - Custom end date: {end_date} (added 1 day to include the selected date)")
        except ValueError:
            try:
                # محاولة تحليل التاريخ بتنسيق yyyy-mm-dd (للتوافق مع الطلبات القديمة)
                end_date_parsed = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
                # إضافة يوم واحد للتأكد من تضمين اليوم المحدد
                end_date = end_date_parsed + timedelta(days=1)
                print(f"Chart data - Custom end date (old format): {end_date} (added 1 day to include the selected date)")
            except ValueError:
                print(f"Chart data - Invalid end date format: {request.args.get('end_date')}")
                pass

    # الحصول على معرف النادي من الطلب إذا كان موجودًا
    club_id = request.args.get('club_id', type=int)

    # تحديد النوادي المطلوبة
    if club_id:
        # التحقق من صلاحية الوصول إلى النادي
        if current_user.role != 'admin' and not current_user.has_club_access(club_id):
            return jsonify({'error': 'ليس لديك صلاحية للوصول إلى هذا النادي'}), 403

        selected_club_ids = [club_id]
    else:
        selected_club_ids = club_ids

    # الحصول على بيانات التشيك للمرافق
    # الحصول على جميع المرافق للنوادي المحددة
    selected_facilities = Facility.query.filter(Facility.club_id.in_(selected_club_ids)).all()
    selected_facility_ids = [facility.id for facility in selected_facilities]

    # الحصول على جميع تشيكات المرافق للنوادي المحددة
    facility_checks = FacilityCheck.query.filter(
        FacilityCheck.facility_id.in_(selected_facility_ids),
        FacilityCheck.check_date >= start_date,
        FacilityCheck.check_date <= end_date
    ).all()

    # طباعة معلومات تشيكات المرافق للتصحيح
    print(f"\n\nFacility Checks for chart data from {start_date} to {end_date}:")
    print(f"Total facility checks found: {len(facility_checks)}")
    for check in facility_checks:
        print(f"Facility Check ID: {check.id}, Date: {check.check_date}, Facility ID: {check.facility_id}, Violations: {check.violations_count}")

    # الحصول على بيانات تشيك الكاميرات
    camera_checks = CameraCheck.query.filter(
        CameraCheck.club_id.in_(selected_club_ids),
        CameraCheck.check_date >= start_date,
        CameraCheck.check_date <= end_date
    ).all()

    # الحصول على بيانات المخالفات النظامية
    violations = Violation.query.filter(
        Violation.club_id.in_(selected_club_ids),
        Violation.violation_date >= start_date,
        Violation.violation_date <= end_date
    ).all()

    print(f"Found {len(violations)} violations")
    for violation in violations:
        print(f"Violation ID: {violation.id}, Employee: {violation.employee_id}, Club: {violation.club_id}")

    # إعداد بيانات الرسم البياني
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    # إعداد بيانات التشيك للمرافق
    facility_data = {date: 0 for date in dates}
    facility_violations_data = {date: 0 for date in dates}

    for check in facility_checks:
        date_str = check.check_date.strftime('%Y-%m-%d')
        if date_str in facility_data:
            facility_data[date_str] += 1
            facility_violations_data[date_str] += check.violations_count or 0

    # إعداد بيانات تشيك الكاميرات
    camera_data = {date: 0 for date in dates}
    camera_violations_data = {date: 0 for date in dates}

    for check in camera_checks:
        date_str = check.check_date.strftime('%Y-%m-%d')
        if date_str in camera_data:
            camera_data[date_str] += 1
            camera_violations_data[date_str] += check.violations_count or 0

    # إعداد بيانات المخالفات النظامية
    legal_violations_data = {date: 0 for date in dates}

    for violation in violations:
        date_str = violation.violation_date.strftime('%Y-%m-%d')
        if date_str in legal_violations_data:
            legal_violations_data[date_str] += 1

    # تحويل البيانات إلى قوائم للرسم البياني
    chart_data = {
        'labels': dates,
        'datasets': [
            {
                'label': 'تشيك المرافق',
                'data': list(facility_data.values()),
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            },
            {
                'label': 'مخالفات المرافق',
                'data': list(facility_violations_data.values()),
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            },
            {
                'label': 'الإجراءات النظامية',
                'data': list(legal_violations_data.values()),
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            },
            {
                'label': 'مخالفات الكاميرات',
                'data': list(camera_violations_data.values()),
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                'borderColor': 'rgba(255, 206, 86, 1)',
                'borderWidth': 1
            }
        ]
    }

    return jsonify(chart_data)
