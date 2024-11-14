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
    
    def set_password(self, password):
        self.password = hashlib.md5(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password == hashlib.md5(password.encode()).hexdigest()

