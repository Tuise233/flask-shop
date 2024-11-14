from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Product
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