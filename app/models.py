from flask_login import UserMixin
from datetime import datetime
import hashlib

from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(10), default='active') # active, ban
    carts = db.relationship('Cart', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password = hashlib.md5(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password == hashlib.md5(password.encode()).hexdigest()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, default=False) # 上下架状态

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='carts', lazy=True)
