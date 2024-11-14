from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models import Cart, Product
from app import db

bp = Blueprint('cart', __name__)

@bp.route('/cart')
@login_required
def cart():
    return render_template('cart.html', carts=current_user.carts)

@bp.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('商品已经没有库存了')
        return redirect(url_for('shop.home'))
        
    carts = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if carts:
        carts.amount += 1
        flash(f'已将 {product.name} 的数量加1')
    else:
        carts = Cart(user_id=current_user.id, product_id=product_id, amount=1)
        db.session.add(carts)
        flash(f'已将 {product.name} 加入购物车')
        
    product.stock -= 1
    db.session.commit()
    return redirect(url_for('shop.home'))

@bp.route('/buy')
@login_required
def buy():
    carts = current_user.carts
    if not carts:
        flash('购物车是空的')
        return redirect(url_for('shop.home'))
        
    for item in carts:
        db.session.delete(item)
    db.session.commit()
    flash('购买成功！')
    return redirect(url_for('shop.home'))