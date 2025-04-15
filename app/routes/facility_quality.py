from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.facility_quality import FacilityQuality
from app.models.facility import Facility, FacilityCheck, FacilityCheckResult
from app.models.facility_type import FacilityType, FacilityTypeItem, club_facility_types
from app.models.user import User
from app.utils.decorators import admin_required
from datetime import datetime, timedelta

bp = Blueprint('facility_quality', __name__)

@bp.route('/')
@login_required
def index():
    """
    عرض تحليل جودة المرافق للنوادي
    """
    # الحصول على قائمة المستخدمين
    if current_user.role == 'admin':
        # الحصول على جميع المستخدمين من نوع user
        users = User.query.filter(User.role == 'user').all()
        print(f"DEBUG: عدد المستخدمين: {len(users)}")
        for user in users:
            print(f"DEBUG: المستخدم: {user.id} - {user.email}")
    else:
        users = [current_user]

    # الحصول على المستخدم المحدد
    selected_user_id = request.args.get('user_id', type=int)
    selected_user = None

    if selected_user_id:
        selected_user = User.query.get(selected_user_id)
        # التحقق من صلاحية الوصول إلى المستخدم المحدد
        if current_user.role != 'admin' and selected_user.id != current_user.id:
            selected_user = current_user

    # الحصول على النوادي المتاحة للمستخدم
    if current_user.role == 'admin':
        if selected_user:
            clubs = selected_user.clubs
        else:
            clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs

    # الحصول على معرف النادي المحدد من الاستعلام
    selected_club_id = request.args.get('club_id', type=int)
    selected_club_ids = [selected_club_id] if selected_club_id else []

    # تحديد تاريخ البداية والنهاية
    end_date_str = request.args.get('end_date', datetime.now().strftime('%d/%m/%Y'))
    start_date_str = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))

    # تحويل التواريخ إلى كائنات datetime
    try:
        end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
        # إضافة يوم واحد لتضمين اليوم المحدد في النتائج
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        end_date = datetime.now().replace(hour=23, minute=59, second=59)
        end_date_str = end_date.strftime('%d/%m/%Y')

    try:
        start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
        start_date = start_date.replace(hour=0, minute=0, second=0)
    except ValueError:
        start_date = (datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0)
        start_date_str = start_date.strftime('%d/%m/%Y')

    # الحصول على أنواع المرافق النشطة من قاعدة البيانات بالترتيب
    facility_types_db = FacilityType.query.filter_by(is_active=True).order_by(FacilityType.order).all()
    facility_types = [ft.name for ft in facility_types_db]

    print(f"DEBUG: تم العثور على {len(facility_types)} نوع مرفق من قاعدة البيانات: {facility_types}")

    # إذا لم توجد أنواع مرافق في قاعدة البيانات، نستخدم قائمة افتراضية بناءً على الصورة المرفقة
    if not facility_types:
        facility_types = [
            'الحصص الجماعية',  # 1
            'القسم الصحي',  # 2
            'المسبح',  # 3
            'الملاعب',  # 5
            'المهام الإدارية',  # 6
            'صالة الترقية',  # 7
            'صالة التمارين الوظيفية',  # 8
            'صالة الحديد',  # 9
            'صالة السائل الهوائية',  # 10
            'صالة الكارديو',  # 11
            'عام',  # 12
            'غرفة غسيل الملابس',  # 13
            'مدخل النادي ومنطقة الاستقبال'  # 14
        ]
        print(f"DEBUG: استخدام قائمة افتراضية لأنواع المرافق: {facility_types}")

    # بيانات جودة المرافق
    quality_data = {}

    # إذا تم تحديد نوادي معينة
    if selected_club_ids:
        # التحقق من صلاحية الوصول إلى النوادي المحددة
        for club_id in selected_club_ids:
            if current_user.role != 'admin' and not current_user.has_club_access(club_id):
                continue  # تخطي النوادي التي لا يملك المستخدم صلاحية الوصول إليها

            # الحصول على بيانات جودة المرافق للنادي المحدد
            club = Club.query.get(club_id)
            if club:
                quality_data[club.id] = {
                    'name': club.name,
                    'facilities': {}
                }

                # حساب نسبة الجودة لكل نوع مرفق
                for facility_type in facility_types:
                    quality_result = calculate_quality_percentage(club.id, facility_type, start_date, end_date)
                    quality_data[club.id]['facilities'][facility_type] = quality_result
    else:
        # الحصول على بيانات جودة المرافق لجميع النوادي المتاحة
        for club in clubs:
            quality_data[club.id] = {
                'name': club.name,
                'facilities': {}
            }

            # حساب نسبة الجودة لكل نوع مرفق
            print(f"\nDEBUG: حساب نسبة الجودة للنادي {club.name} (ID: {club.id})")
            for facility_type in facility_types:
                print(f"DEBUG: حساب نسبة الجودة للمرفق {facility_type}")
                quality_result = calculate_quality_percentage(club.id, facility_type, start_date, end_date)
                quality_data[club.id]['facilities'][facility_type] = quality_result
                print(f"DEBUG: نتيجة حساب الجودة: {quality_result['average_quality']}% (موجود: {quality_result.get('facility_exists', True)})")

    # حساب متوسط الجودة لكل نوع مرفق عبر جميع النوادي
    averages = {}
    for facility_type in facility_types:
        total = 0
        count = 0
        for club_id, club_data in quality_data.items():
            if facility_type in club_data['facilities']:
                # استبعاد المرافق غير الموجودة
                if club_data['facilities'][facility_type]['average_quality'] != -1:
                    total += club_data['facilities'][facility_type]['average_quality']
                    count += 1

        if count > 0:
            averages[facility_type] = round(total / count)
        else:
            averages[facility_type] = 75  # قيمة افتراضية مقبولة

    # حساب متوسط الجودة لكل نادي
    for club_id, club_data in quality_data.items():
        total = 0
        count = 0
        for facility_type, quality_result in club_data['facilities'].items():
            # استبعاد المرافق غير الموجودة
            if quality_result['average_quality'] != -1:
                total += quality_result['average_quality']
                count += 1

        if count > 0:
            club_data['average'] = round(total / count)
        else:
            club_data['average'] = 75  # قيمة افتراضية مقبولة

    # حساب المتوسط العام
    total_average = 0
    if quality_data:
        valid_averages = [club_data['average'] for club_data in quality_data.values()]
        if valid_averages:
            total_average = round(sum(valid_averages) / len(valid_averages))
        else:
            total_average = 75  # قيمة افتراضية مقبولة

    return render_template('facility_quality/index.html',
                           title='تحليل جودة المرافق',
                           clubs=clubs,
                           users=users,
                           selected_user=selected_user,
                           selected_club_id=selected_club_id,
                           selected_club_ids=selected_club_ids,
                           start_date=start_date_str,
                           end_date=end_date_str,
                           facility_types=facility_types,
                           quality_data=quality_data,
                           averages=averages,
                           total_average=total_average)

def calculate_quality_percentage(club_id, facility_type_name, start_date, end_date):
    """
    حساب نسبة جودة المرفق بناءً على نتائج التشيك
    تعيد قاموس يحتوي على معلومات مفصلة عن نتائج التشيك
    """
    print(f"\n\n==== حساب جودة المرفق {facility_type_name} للنادي {club_id} ====\n")

    # الحصول على النادي
    club = Club.query.get(club_id)
    if not club:
        print(f"DEBUG: لم يتم العثور على النادي بالمعرف {club_id}")
        return {
            'average_quality': -1,
            'check_count': 0,
            'checks': []
        }

    # البحث عن نوع المرفق
    facility_type = FacilityType.query.filter_by(name=facility_type_name).first()
    if not facility_type:
        # إذا لم يوجد نوع المرفق، نعيد قاموس فارغ
        print(f"DEBUG: لم يتم العثور على نوع المرفق: {facility_type_name}")
        return {
            'average_quality': -1,
            'check_count': 0,
            'checks': []
        }

    # التحقق مما إذا كان المرفق موجودًا في النادي
    try:
        # التحقق من وجود المرفق في النادي من خلال جدول club_facility_types
        facility_exists_in_club = db.session.query(club_facility_types).filter(
            club_facility_types.c.club_id == club_id,
            club_facility_types.c.facility_type_id == facility_type.id
        ).first() is not None

        print(f"DEBUG: التحقق من وجود المرفق {facility_type_name} (ID: {facility_type.id}) في النادي {club.name} (ID: {club_id}): {facility_exists_in_club}")

        # طريقة بديلة للتحقق من وجود المرفق في النادي
        facility_exists_in_club_alt = facility_type in club.facility_types.all()
        print(f"DEBUG: التحقق البديل من وجود المرفق {facility_type_name} في النادي {club.name}: {facility_exists_in_club_alt}")

        # استخدام نتيجة التحقق البديل إذا كانت مختلفة
        if facility_exists_in_club != facility_exists_in_club_alt:
            print(f"WARNING: نتائج التحقق مختلفة! سيتم استخدام الطريقة البديلة.")
            facility_exists_in_club = facility_exists_in_club_alt
    except Exception as e:
        print(f"ERROR: حدث خطأ أثناء التحقق من وجود المرفق: {str(e)}")
        # في حالة حدوث خطأ، نفترض أن المرفق موجود
        facility_exists_in_club = True

    if not facility_exists_in_club:
        print(f"DEBUG: المرفق {facility_type_name} غير موجود في النادي {club.name}")
        return {
            'average_quality': -1,
            'check_count': 0,
            'checks': [],
            'facility_exists': False
        }

    # الحصول على المرافق من هذا النوع للنادي المحدد
    print(f"DEBUG: البحث عن مرافق من نوع '{facility_type_name}' للنادي {club_id}")

    # التحقق من جميع أنواع المرافق الموجودة في جدول Facility
    all_facility_types = db.session.query(Facility.facility_type).distinct().all()
    print(f"DEBUG: جميع أنواع المرافق الموجودة في جدول Facility: {[ft[0] for ft in all_facility_types]}")

    # البحث عن المرافق بطريقة أكثر مرونة
    # محاولة المطابقة الدقيقة أولاً
    facilities = Facility.query.filter_by(
        club_id=club_id,
        facility_type=facility_type_name
    ).all()

    # إذا لم يتم العثور على مرافق، نحاول البحث باستخدام المطابقة الجزئية
    if not facilities:
        # البحث عن مرافق تحتوي على اسم النوع في اسمها
        facilities = Facility.query.filter(
            Facility.club_id == club_id,
            Facility.facility_type.like(f'%{facility_type_name}%')
        ).all()

        if facilities:
            print(f"DEBUG: تم العثور على مرافق باستخدام المطابقة الجزئية: {[f.facility_type for f in facilities]}")

    # إذا لم يتم العثور على مرافق، نحاول البحث عن أي مرفق للنادي
    if not facilities:
        # البحث عن أي مرفق للنادي
        facilities = Facility.query.filter_by(club_id=club_id).all()
        print(f"DEBUG: تم العثور على {len(facilities)} مرفق للنادي {club_id}")

        # إذا لم يتم العثور على مرافق، نعتبر أن هذا المرفق غير موجود في النادي
        if not facilities:
            print(f"DEBUG: لم يتم العثور على مرافق من نوع {facility_type_name} للنادي {club_id}")
            # نعيد قيمة خاصة تشير إلى أن المرفق غير موجود
            return {
                'average_quality': -1,  # قيمة خاصة تشير إلى أن المرفق غير موجود
                'check_count': 0,
                'checks': [],
                'facility_exists': False  # مؤشر يشير إلى أن المرفق غير موجود
            }

    # الحصول على فحوصات المرافق في الفترة المحددة
    facility_ids = [facility.id for facility in facilities]
    print(f"DEBUG: معرفات المرافق التي تم العثور عليها: {facility_ids}")

    # طباعة معلومات عن كل مرفق
    for facility in facilities:
        print(f"DEBUG: مرفق {facility.id} - الاسم: {facility.name} - النوع: {facility.facility_type}")

    # توسيع نطاق البحث الزمني إذا لم يتم تحديد تاريخ بداية
    if start_date is None:
        # إذا لم يتم تحديد تاريخ بداية، نستخدم تاريخ قبل سنة
        start_date = datetime.now() - timedelta(days=365)

    # توسيع نطاق البحث الزمني إذا لم يتم تحديد تاريخ نهاية
    if end_date is None:
        # إذا لم يتم تحديد تاريخ نهاية، نستخدم التاريخ الحالي
        end_date = datetime.now()

    print(f"DEBUG: البحث عن فحوصات للمرافق {facility_ids} في الفترة من {start_date} إلى {end_date}")

    # الحصول على جميع عمليات التشيك للمرافق خلال الفترة المحددة
    all_checks = []
    for facility_id in facility_ids:
        # الحصول على جميع عمليات التشيك للمرفق خلال الفترة المحددة
        facility_checks = FacilityCheck.query.filter(
            FacilityCheck.facility_id == facility_id,
            FacilityCheck.check_date >= start_date,
            FacilityCheck.check_date <= end_date
        ).order_by(FacilityCheck.check_date.desc()).all()

        print(f"DEBUG: تم العثور على {len(facility_checks)} عملية تشيك للمرفق {facility_id} في الفترة من {start_date} إلى {end_date}")

        all_checks.extend(facility_checks)

    if not all_checks:
        # إذا لم توجد فحوصات، نحاول توسيع نطاق البحث الزمني أكثر
        extended_start_date = datetime.now() - timedelta(days=730)  # سنتين
        print(f"DEBUG: توسيع نطاق البحث الزمني إلى سنتين: من {extended_start_date} إلى {end_date}")

        for facility_id in facility_ids:
            facility_checks = FacilityCheck.query.filter(
                FacilityCheck.facility_id == facility_id,
                FacilityCheck.check_date >= extended_start_date,
                FacilityCheck.check_date <= end_date
            ).order_by(FacilityCheck.check_date.desc()).all()

            print(f"DEBUG: تم العثور على {len(facility_checks)} عملية تشيك للمرفق {facility_id} بعد توسيع نطاق البحث")

            all_checks.extend(facility_checks)

    # إذا كانت هناك مرافق ولكن لا توجد فحوصات، نعيد قيمة افتراضية
    if not all_checks and facilities:
        print(f"DEBUG: تم العثور على مرافق ولكن لا توجد فحوصات لها")
        return {
            'average_quality': 75,  # قيمة افتراضية للمرافق التي لا توجد لها فحوصات
            'check_count': 0,
            'checks': []
        }

    # إذا لم توجد مرافق أو فحوصات، نعتبر المرفق غير موجود
    if not all_checks and not facilities:
        print(f"DEBUG: لم يتم العثور على مرافق أو فحوصات")
        return {
            'average_quality': -1,  # قيمة خاصة تشير إلى أن المرفق غير موجود
            'check_count': 0,
            'checks': [],
            'facility_exists': False
        }

    # حساب نسبة الجودة لكل عملية تشيك
    check_details = []  # لتخزين تفاصيل كل عملية تشيك

    # استخدام جميع التشيكات خلال الفترة المحددة لحساب نسبة الجودة
    if all_checks:
        print(f"DEBUG: عدد التشيكات خلال الفترة المحددة: {len(all_checks)}")

        # تجميع جميع نتائج الفحص لجميع التشيكات
        all_facility_type_results = []

        for check in all_checks:
            # الحصول على نتائج الفحص
            results = FacilityCheckResult.query.filter_by(facility_check_id=check.id).all()
            print(f"DEBUG: عدد نتائج الفحص للتشيك {check.id}: {len(results)}")

            # تصفية النتائج للحصول على نتائج المرفق المطلوب فقط
            for result in results:
                # الحصول على بند الفحص
                check_item = FacilityTypeItem.query.get(result.check_item_id)
                if check_item and check_item.facility_type_id:
                    # الحصول على نوع المرفق المرتبط بالبند
                    item_facility_type = FacilityType.query.get(check_item.facility_type_id)
                    if item_facility_type and item_facility_type.name == facility_type_name:
                        all_facility_type_results.append(result)

            # إضافة تفاصيل التشيك إلى القائمة
            check_details.append({
                'facility_id': check.facility_id,
                'check_id': check.id,
                'check_date': check.check_date,
                'facility_name': Facility.query.get(check.facility_id).name if Facility.query.get(check.facility_id) else ''
            })

        # حساب عدد البنود المطابقة وغير المطابقة لجميع التشيكات
        passed_count = len([r for r in all_facility_type_results if r.status == 'passed'])
        total_count = len([r for r in all_facility_type_results if r.status != 'na'])

        print(f"DEBUG: نتائج المرفق {facility_type_name} لجميع التشيكات: إجمالي البنود: {total_count}, البنود المطابقة: {passed_count}")

        # حساب نسبة الجودة لجميع التشيكات
        if total_count > 0:
            average_quality = round((passed_count / total_count) * 100)
            print(f"DEBUG: نسبة الجودة لجميع التشيكات: {average_quality}%")

            return {
                'average_quality': average_quality,
                'check_count': len(all_checks),
                'checks': check_details
            }
        else:
            print(f"DEBUG: لا توجد بنود للمرفق {facility_type_name}")

    # إذا لم يتم العثور على نتائج أو لم يكن هناك تشيك
    print(f"DEBUG: لم يتم العثور على نتائج للمرفق {facility_type_name}")

    # إذا لم يتم العثور على نتائج، نعيد قيمة افتراضية
    average_quality = 75  # قيمة افتراضية للمرافق التي لا توجد لها نتائج

    # تخزين نسبة الجودة في قاعدة البيانات للاستخدام المستقبلي
    quality = FacilityQuality.query.filter_by(
        club_id=club_id,
        facility_type=facility_type_name
    ).first()

    if quality:
        quality.quality_percentage = average_quality
        quality.updated_at = datetime.now()
    else:
        quality = FacilityQuality(
            club_id=club_id,
            facility_type=facility_type_name,
            quality_percentage=average_quality,
            updated_at=datetime.now()
        )
        db.session.add(quality)

    db.session.commit()

    # إرجاع قاموس يحتوي على جميع المعلومات
    return {
        'average_quality': average_quality,
        'check_count': 0,
        'checks': []
    }

@bp.route('/update', methods=['POST'])
@login_required
@admin_required
def update_quality():
    """
    تحديث نسبة جودة المرفق
    """
    club_id = request.form.get('club_id', type=int)
    facility_type = request.form.get('facility_type')
    quality_percentage = request.form.get('quality_percentage', type=int)

    if not club_id or not facility_type or quality_percentage is None:
        flash('بيانات غير صحيحة', 'danger')
        return redirect(url_for('facility_quality.index'))

    # التحقق من وجود سجل سابق
    quality = FacilityQuality.query.filter_by(
        club_id=club_id,
        facility_type=facility_type
    ).first()

    if quality:
        # تحديث السجل الموجود
        quality.quality_percentage = quality_percentage
        quality.updated_at = datetime.now()
    else:
        # إنشاء سجل جديد
        quality = FacilityQuality(
            club_id=club_id,
            facility_type=facility_type,
            quality_percentage=quality_percentage
        )
        db.session.add(quality)

    db.session.commit()

    flash('تم تحديث نسبة الجودة بنجاح', 'success')
    return redirect(url_for('facility_quality.index', club_id=club_id))
