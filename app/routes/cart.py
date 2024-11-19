from flask import Blueprint, redirect, url_for, flash, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Cart, Product
from app import db
from app.utils.pay import alipay_obj, ALIPAY_SETTING
import uuid

bp = Blueprint("cart", __name__)


@bp.route("/cart")
@login_required
def cart():
    carts = current_user.carts
    total_price = sum(item.amount * item.product.price for item in carts)
    return render_template("cart.html", carts=carts, total_price=total_price)


@bp.route("/add_to_cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash("商品已经没有库存了")
        return redirect(url_for("shop.home"))

    cart = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart:
        cart.amount += 1
        flash(f"已将 {product.name} 的数量加1")
    else:
        cart = Cart(user_id=current_user.id, product_id=product_id, amount=1)
        db.session.add(cart)
        flash(f"已将 {product.name} 加入购物车")

    product.stock -= 1
    db.session.commit()
    return redirect(url_for("shop.home"))


@bp.route("/update_cart/<int:cart_id>", methods=["POST"])
@login_required
def update_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.user_id != current_user.id:
        flash("无权操作此购物车")
        return redirect(url_for("cart.cart"))

    new_amount = int(request.form.get("amount", 1))
    if new_amount <= 0:
        db.session.delete(cart)
        flash("商品已从购物车中移除")
    else:
        # 计算库存变化
        amount_diff = new_amount - cart.amount
        if amount_diff > cart.product.stock:
            flash("库存不足")
            return redirect(url_for("cart.cart"))

        cart.product.stock -= amount_diff
        cart.amount = new_amount
        flash("购物车已更新")

    db.session.commit()
    return redirect(url_for("cart.cart"))


@bp.route("/remove_from_cart/<int:cart_id>")
@login_required
def remove_from_cart(cart_id):
    cart = Cart.query.get_or_404(cart_id)
    if cart.user_id != current_user.id:
        flash("无权操作此购物车")
        return redirect(url_for("cart.cart"))

    cart.product.stock += cart.amount
    db.session.delete(cart)
    db.session.commit()
    flash("商品已从购物车中移除")
    return redirect(url_for("cart.cart"))


@bp.route("/buy")
@login_required
def buy():
    carts = current_user.carts
    if not carts:
        flash("购物车是空的")
        return redirect(url_for("shop.home"))

    total_amount = str(sum(item.amount * item.product.price for item in carts))
    
    alipay = alipay_obj()
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(uuid.uuid4()),
        total_amount=total_amount,
        subject="购物车订单",
        return_url=ALIPAY_SETTING.get("ALIPAY_RETURN_URL"),
        notify_url=ALIPAY_SETTING.get("ALIPAY_NOTIFY_URL"),
    )
    
    pay_url = f"{ALIPAY_SETTING.get('ALIPAY_GATEWAY')}?{order_string}"
    return redirect(pay_url)


@bp.route("/alipay_return")
@login_required
def alipay_return():
    data = request.args.to_dict()
    signature = data.pop("sign")

    success = False
    error_message = ""
    amount = 0

    try:
        alipay = alipay_obj()
        success = alipay.verify(data, signature)
        if success:
            amount = float(data.get("total_amount", 0))
            carts = current_user.carts
            for item in carts:
                db.session.delete(item)
            db.session.commit()
        else:
            error_message = "支付签名验证失败"
    except Exception as e:
        success = False
        error_message = f"支付处理异常: {str(e)}"

    return render_template(
        "payment_result.html",
        payment_success=success,
        amount=amount,
        error_message=error_message,
    )


@bp.route("/alipay_notify", methods=['POST'])
def alipay_notify():
    data = request.form.to_dict()
    signature = data.pop("sign")

    try:
        alipay = alipay_obj()
        success = alipay.verify(data, signature)
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            carts = Cart.query.filter_by(user_id=data.get("buyer_id")).all()
            for item in carts:
                db.session.delete(item)
            db.session.commit()
            return 'success'
        else:
            return 'failure'
    except Exception as e:
        return 'failure'
