from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.club import Club
from app.models.revenue import Revenue, RevenueCategory
from app.forms.revenue import RevenueForm, RevenueCategoryForm

bp = Blueprint('revenue', __name__)

@bp.route('/')
@login_required
def index():
    """
    صفحة الإيرادات الرئيسية
    """
    # الحصول على الإيرادات
    revenues = Revenue.query.order_by(Revenue.date.desc()).all()
    
    # الحصول على فئات الإيرادات
    categories = RevenueCategory.query.all()
    
    return render_template('revenue/index.html', 
                           title='الإيرادات',
                           revenues=revenues,
                           categories=categories)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    إنشاء إيراد جديد
    """
    form = RevenueForm()
    
    # تعبئة قائمة الأندية
    if current_user.role == 'admin':
        clubs = Club.query.filter_by(is_active=True).all()
    else:
        clubs = current_user.clubs
        
    form.club_id.choices = [(club.id, club.name) for club in clubs]
    
    # تعبئة قائمة الفئات
    categories = RevenueCategory.query.all()
    form.category_id.choices = [(cat.id, cat.name) for cat in categories]
    
    if form.validate_on_submit():
        revenue = Revenue(
            club_id=form.club_id.data,
            category_id=form.category_id.data,
            date=form.date.data,
            amount=form.amount.data,
            description=form.description.data,
            recorded_by=current_user.id
        )
        db.session.add(revenue)
        db.session.commit()
        flash('تم إضافة الإيراد بنجاح', 'success')
        return redirect(url_for('revenue.index'))
    
    return render_template('revenue/create.html',
                           title='إضافة إيراد',
                           form=form)

@bp.route('/categories')
@login_required
def categories():
    """
    عرض فئات الإيرادات
    """
    categories = RevenueCategory.query.all()
    return render_template('revenue/categories.html',
                           title='فئات الإيرادات',
                           categories=categories)

@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    """
    إنشاء فئة إيرادات جديدة
    """
    form = RevenueCategoryForm()
    
    if form.validate_on_submit():
        category = RevenueCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('تم إضافة فئة الإيرادات بنجاح', 'success')
        return redirect(url_for('revenue.categories'))
    
    return render_template('revenue/create_category.html',
                           title='إضافة فئة إيرادات',
                           form=form)
