from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Product, User
from app import db

bp = Blueprint('admin', __name__)

@bp.route('/admin/products')
@login_required
def products():
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@bp.route('/admin/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        status = True if request.form.get('status') else False
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            status=status
        )
        db.session.add(product)
        db.session.commit()
        flash('商品创建成功')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/create_product.html')

@bp.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.status = True if request.form.get('status') else False
        
        db.session.commit()
        flash('商品更新成功')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/edit_product.html', product=product)

@bp.route('/admin/products/<int:id>/delete')
@login_required
def delete_product(id):
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('商品删除成功')
    return redirect(url_for('admin.products'))

@bp.route('/admin/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/admin/users/<int:id>/toggle_status')
@login_required
def toggle_user_status(id):
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    user = User.query.get_or_404(id)
    
    # 不能封禁自己
    if user.id == current_user.id:
        flash('不能修改自己的状态')
        return redirect(url_for('admin.users'))
        
    # 切换用户状态
    user.status = 'ban' if user.status == 'active' else 'active'
    db.session.commit()
    flash(f'用户 {user.username} 状态已更新')
    return redirect(url_for('admin.users'))

@bp.route('/admin/users/<int:id>/toggle_admin')
@login_required
def toggle_user_admin(id):
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    user = User.query.get_or_404(id)
    
    # 不能修改自己的管理员状态
    if user.id == current_user.id:
        flash('不能修改自己的管理员状态')
        return redirect(url_for('admin.users'))
        
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'用户 {user.username} 管理员权限已更新')
    return redirect(url_for('admin.users'))

@bp.route('/admin/users/<int:id>/delete')
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('你没有管理员权限')
        return redirect(url_for('shop.home'))
        
    user = User.query.get_or_404(id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账号')
        return redirect(url_for('admin.users'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f'用户 {user.username} 已删除')
    return redirect(url_for('admin.users')) 