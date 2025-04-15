from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, Club, Permission, DetailedPermission
from datetime import datetime
from app.forms.auth import LoginForm, RegistrationForm, ChangePasswordForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    صفحة تسجيل الدخول
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # تسجيل بيانات النموذج للتشخيص
        print(f"\n\nمحاولة تسجيل الدخول باسم المستخدم: {form.username.data}")

        user = User.query.filter_by(username=form.username.data).first()

        if user is None:
            print(f"لم يتم العثور على مستخدم باسم {form.username.data}")
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))

        # التحقق من كلمة المرور
        password_check = user.check_password(form.password.data)
        print(f"التحقق من كلمة المرور: {password_check}")
        print(f"كلمة المرور المدخلة: {form.password.data}")
        print(f"كلمة المرور المخزنة: {user.password_hash}")

        if not password_check:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('هذا الحساب غير نشط. يرجى الاتصال بالمسؤول.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        # تحديث وقت آخر تسجيل دخول
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)

    return render_template('auth/login.html', title='تسجيل الدخول', form=form)

@bp.route('/logout')
def logout():
    """
    تسجيل الخروج
    """
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    تسجيل مستخدم جديد (متاح فقط للمسؤولين)
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    # تحميل قائمة الأندية للاختيار
    clubs = Club.query.filter_by(is_active=True).all()
    form.clubs.choices = [(club.id, club.name) for club in clubs]

    # تهيئة قائمة فارغة للأندية المحددة
    if form.clubs.data is None:
        form.clubs.data = []

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            employee_number=form.employee_number.data,
            role=form.role.data
        )
        user.set_password(form.password.data)

        # إضافة الأندية المحددة للمستخدم
        selected_clubs = Club.query.filter(Club.id.in_(form.clubs.data)).all()
        user.clubs = selected_clubs

        db.session.add(user)
        db.session.commit()

        flash(f'تم إنشاء المستخدم {form.username.data} بنجاح!', 'success')
        return redirect(url_for('auth.users'))

    return render_template('auth/register.html', title='تسجيل مستخدم جديد', form=form)

@bp.route('/test_clubs/<int:user_id>')
@login_required
def test_clubs(user_id):
    """
    اختبار قائمة الأندية
    """
    user = User.query.get_or_404(user_id)
    all_clubs = Club.query.all()
    user_club_ids = [club.id for club in user.clubs]

    return render_template('auth/test_clubs.html', title='اختبار قائمة الأندية', user=user, all_clubs=all_clubs, user_club_ids=user_club_ids)


@bp.route('/users')
@login_required
def users():
    """
    عرض قائمة المستخدمين (متاح فقط للمسؤولين)
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('auth/users.html', title='المستخدمين', users=users)

@bp.route('/user/<int:id>')
@login_required
def user(id):
    """
    عرض تفاصيل المستخدم
    """
    if current_user.role != 'admin' and current_user.id != id:
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    permissions = Permission.query.all()

    # التحقق من وجود صلاحيات تفصيلية
    detailed_permissions_count = DetailedPermission.query.count()

    # إذا لم تكن هناك صلاحيات تفصيلية، قم بإنشائها
    if detailed_permissions_count == 0:
        # قائمة بالصفحات والأزرار
        pages = {
            'الصفحة الرئيسية': {
                'description': 'الصفحة الرئيسية للتطبيق',
                'actions': [
                    {'name': 'عرض الصفحة', 'description': 'عرض الصفحة الرئيسية'},
                    {'name': 'عرض الإحصائيات', 'description': 'عرض إحصائيات النوادي'},
                ]
            },
            'النوادي': {
                'description': 'إدارة النوادي',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة النوادي'},
                    {'name': 'إضافة نادي', 'description': 'إضافة نادي جديد'},
                    {'name': 'تعديل نادي', 'description': 'تعديل بيانات النادي'},
                    {'name': 'حذف نادي', 'description': 'حذف نادي'},
                ]
            },
            'المرافق': {
                'description': 'إدارة المرافق',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة المرافق'},
                    {'name': 'إضافة مرفق', 'description': 'إضافة مرفق جديد'},
                    {'name': 'تعديل مرفق', 'description': 'تعديل بيانات المرفق'},
                    {'name': 'حذف مرفق', 'description': 'حذف مرفق'},
                ]
            },
            'الأعطال': {
                'description': 'إدارة الأعطال',
                'actions': [
                    {'name': 'عرض القائمة', 'description': 'عرض قائمة الأعطال'},
                    {'name': 'إضافة عطل', 'description': 'إضافة عطل جديد'},
                    {'name': 'تعديل عطل', 'description': 'تعديل بيانات العطل'},
                    {'name': 'حذف عطل', 'description': 'حذف عطل'},
                ]
            }
        }

        # إنشاء الصلاحيات التفصيلية
        for page_name, page_data in pages.items():
            for action in page_data['actions']:
                permission = DetailedPermission(
                    page_name=page_name,
                    page_description=page_data['description'],
                    action_name=action['name'],
                    action_description=action['description'],
                    is_allowed=False
                )
                db.session.add(permission)

        # حفظ التغييرات
        db.session.commit()

    # الحصول على الصلاحيات التفصيلية
    detailed_permissions = DetailedPermission.query.all()

    return render_template('auth/user.html', title=f'المستخدم: {user.username}', user=user, permissions=permissions, detailed_permissions=detailed_permissions)

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    تعديل بيانات المستخدم
    """
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    all_clubs = Club.query.all()
    print(f'\n\nعدد الأندية: {len(all_clubs)}')
    for club in all_clubs[:5]:
        print(f'\t- النادي: {club.name}, المعرف: {club.id}')

    if request.method == 'POST':
        # الحصول على البيانات من النموذج
        username = request.form.get('username')
        email = request.form.get('email')
        employee_number = request.form.get('employee_number')
        role = request.form.get('role')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        clubs_data = request.form.getlist('clubs')

        # التحقق من البيانات
        error = False

        # التحقق من تكرار الرقم الوظيفي
        if username != user.username:
            username_exists = User.query.filter(User.username == username, User.id != id).first()
            if username_exists:
                flash('الرقم الوظيفي مستخدم بالفعل', 'danger')
                error = True
                print(f'\n\nتكرار الرقم الوظيفي: {username}')

        # التحقق من تكرار رقم الهاتف
        if employee_number != user.employee_number:
            phone_exists = User.query.filter(User.employee_number == employee_number, User.id != id).first()
            if phone_exists:
                flash('رقم الهاتف مستخدم بالفعل', 'danger')
                error = True
                print(f'\n\nتكرار رقم الهاتف: {employee_number}')

        # التحقق من تطابق كلمات المرور
        if password and password != password2:
            flash('كلمات المرور غير متطابقة', 'danger')
            error = True

        # التحقق من اختيار نادي واحد على الأقل
        if not clubs_data:
            flash('يرجى اختيار نادي واحد على الأقل', 'danger')
            error = True

        # إذا كانت هناك أخطاء، أعد عرض الصفحة
        if error:
            user_club_ids = [club.id for club in user.clubs]
            return render_template('auth/edit_user_final.html', title=f'تعديل المستخدم: {user.username}', user=user, all_clubs=all_clubs, user_club_ids=user_club_ids)

        # إذا لم تكن هناك أخطاء، قم بتحديث البيانات
        user.username = username
        user.email = email
        user.employee_number = employee_number
        user.role = role

        if password:
            user.set_password(password)

        # تحويل قائمة الأندية من سلسلة نصية إلى أرقام صحيحة
        club_ids = [int(club_id) for club_id in clubs_data]

        # تحديث الأندية المحددة للمستخدم
        selected_clubs = Club.query.filter(Club.id.in_(club_ids)).all()
        user.clubs = selected_clubs

        db.session.commit()
        flash(f'تم تحديث بيانات المستخدم {user.username} بنجاح!', 'success')
        return redirect(url_for('auth.users'))

    # في حالة GET
    # استخراج معرفات الأندية المحددة للمستخدم
    user_club_ids = [club.id for club in user.clubs]
    print(f'\n\nالأندية المحددة للمستخدم: {user_club_ids}')
    return render_template('auth/edit_user_final.html', title=f'تعديل المستخدم: {user.username}', user=user, all_clubs=all_clubs, user_club_ids=user_club_ids)



@bp.route('/check_username', methods=['GET'])
def check_username():
    """
    التحقق من تكرار الرقم الوظيفي
    """
    username = request.args.get('username')
    user_id = request.args.get('user_id', 0, type=int)

    user = User.query.filter(User.username == username, User.id != user_id).first()
    return jsonify({'exists': user is not None})

@bp.route('/check_employee_number', methods=['GET'])
def check_employee_number():
    """
    التحقق من تكرار رقم الهاتف
    """
    employee_number = request.args.get('employee_number')
    user_id = request.args.get('user_id', 0, type=int)

    user = User.query.filter(User.employee_number == employee_number, User.id != user_id).first()
    return jsonify({'exists': user is not None})

@bp.route('/save_permissions/<int:id>', methods=['POST'])
@login_required
def save_permissions(id):
    """
    حفظ صلاحيات المستخدم
    """
    # التحقق من صلاحية الوصول
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    permissions_data = request.form.to_dict()

    # حذف جميع صلاحيات المستخدم الحالية
    user.permissions = []

    # معالجة بيانات الصلاحيات
    # الحصول على جميع الصلاحيات
    all_permissions = Permission.query.all()

    for permission in all_permissions:
        # التحقق من وجود الصلاحيات في النموذج
        view_key = f'permissions[{permission.id}][view]'
        create_key = f'permissions[{permission.id}][create]'
        edit_key = f'permissions[{permission.id}][edit]'
        delete_key = f'permissions[{permission.id}][delete]'

        # التحقق من وجود أي صلاحية محددة
        has_view = view_key in permissions_data
        has_create = create_key in permissions_data
        has_edit = edit_key in permissions_data
        has_delete = delete_key in permissions_data

        # إذا كانت أي من الصلاحيات محددة، أضف الصلاحية للمستخدم
        if has_view or has_create or has_edit or has_delete:
            # إنشاء نسخة جديدة من الصلاحية للمستخدم
            user_permission = Permission.query.get(permission.id)
            user_permission.can_view = has_view
            user_permission.can_create = has_create
            user_permission.can_edit = has_edit
            user_permission.can_delete = has_delete

            # إضافة الصلاحية للمستخدم
            user.permissions.append(user_permission)

    # حفظ التغييرات
    db.session.commit()
    flash('تم حفظ صلاحيات المستخدم بنجاح!', 'success')
    return redirect(url_for('auth.user', id=id))

@bp.route('/save_detailed_permissions/<int:id>', methods=['POST'])
@login_required
def save_detailed_permissions(id):
    """
    حفظ الصلاحيات التفصيلية للمستخدم
    """
    # التحقق من صلاحية الوصول
    if current_user.role != 'admin':
        flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(id)
    permissions_data = request.form.to_dict()

    # حذف جميع صلاحيات المستخدم التفصيلية الحالية
    user.detailed_permissions = []

    # معالجة بيانات الصلاحيات التفصيلية
    all_permissions = DetailedPermission.query.all()

    for permission in all_permissions:
        # التحقق من وجود الصلاحية في النموذج
        permission_key = f'detailed_permissions[{permission.id}]'

        # إذا كانت الصلاحية محددة، أضفها للمستخدم
        if permission_key in permissions_data:
            # تحديث حالة الصلاحية
            permission.is_allowed = True

            # إضافة الصلاحية للمستخدم
            user.detailed_permissions.append(permission)
        else:
            # إذا لم تكن محددة، تأكد من أنها غير مسموحة
            permission.is_allowed = False

    # حفظ التغييرات
    db.session.commit()
    flash('تم حفظ صلاحيات المستخدم بنجاح!', 'success')
    return redirect(url_for('auth.user', id=id))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    تغيير كلمة المرور
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('كلمة المرور الحالية غير صحيحة', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/change_password.html', title='تغيير كلمة المرور', form=form)
