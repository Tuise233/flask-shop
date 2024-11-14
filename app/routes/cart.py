from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user
from app.models import Cart, Product
from app import db

bp = Blueprint('cart', __name__)

@bp.route('/cart')
@login_required
def cart():
    carts = current_user.carts
    total_price = sum(item.amount * item.product.price for item in carts)
    return render_template('cart.html', carts=carts, total_price=total_price)

@bp.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('商品已经没有库存了')
        return redirect(url_for('shop.home'))
        
    cart = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart:
        cart.amount += 1
        flash(f'已将 {product.name} 的数量加1')
    else:
        cart = Cart(user_id=current_user.id, product_id=product_id, amount=1)
        db.session.add(cart)
        flash(f'已将 {product.name} 加入购物车')
        
    product.stock -= 1
    db.session.commit()
    return redirect(url_for('shop.home'))

@bp.route('/update_cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.user_id != current_user.id:
        flash('无权操作此购物车')
        return redirect(url_for('cart.cart'))
    
    new_amount = int(request.form.get('amount', 1))
    if new_amount <= 0:
        db.session.delete(cart)
        flash('商品已从购物车中移除')
    else:
        # 计算库存变化
        amount_diff = new_amount - cart.amount
        if amount_diff > cart.product.stock:
            flash('库存不足')
            return redirect(url_for('cart.cart'))
            
        cart.product.stock -= amount_diff
        cart.amount = new_amount
        flash('购物车已更新')
    
    db.session.commit()
    return redirect(url_for('cart.cart'))

@bp.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.user_id != current_user.id:
        flash('无权操作此购物车')
        return redirect(url_for('cart.cart'))
    
    # 恢复库存
    cart.product.stock += cart.amount
    db.session.delete(cart)
    db.session.commit()
    flash('商品已从购物车中移除')
    return redirect(url_for('cart.cart'))

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