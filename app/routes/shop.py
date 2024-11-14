from flask import Blueprint, render_template
from app.models import Product

bp = Blueprint('shop', __name__)

@bp.route('/')
def home():
    products = Product.query.filter_by(status=True).all()
    return render_template('home.html', products=products) 