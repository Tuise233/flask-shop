from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # 判断用户状态
            if user.status == "ban":
                flash("你的账户被封禁")
                return redirect(url_for("auth.login"))
            login_user(user)
            return redirect(url_for("shop.home"))
        else:
            flash("用户名或密码有误, 请核对后重试")
    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 判断用户名是否被占用
        if User.query.filter_by(username=username).first():
            flash("用户名已被占用")
            return redirect(url_for("auth.register"))
        user = User(username=username)
        user.set_password(password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("register.html")
