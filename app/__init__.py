from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 数据库初始化一下
    db.init_app(app)
    
    # flask_login
    login_manager.init_app(app)

    from app.routes import auth, shop, cart
    app.register_blueprint(auth.bp)
    app.register_blueprint(shop.bp)
    app.register_blueprint(cart.bp)

    with app.app_context():
        db.create_all()

    return app
