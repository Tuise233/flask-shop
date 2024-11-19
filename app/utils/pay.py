from flask import url_for
from alipay import AliPay, DCAliPay, ISVAliPay
import os

ALIPAY_SETTING = {
    'ALIPAY_APP_ID': '9021000142600082',
    'ALIPAY_DEBUG': True,
    'ALIPAY_GATEWAY': 'https://openapi-sandbox.dl.alipaydev.com/gateway.do',
    'ALIPAY_RETURN_URL': 'http://127.0.0.1:5000/alipay_return',
    'ALIPAY_NOTIFY_URL': 'http://127.0.0.1:5000/alipay_notify',
    'APP_PRIVATE_KEY_STRING': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/private.pem'),
    'ALIPAY_PUBLIC_KEY_STRING': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/public.pem'),
    'SIGN_TYPE': 'RSA2',
}

def alipay_obj():
    alipay = AliPay(
        appid=ALIPAY_SETTING.get('ALIPAY_APP_ID'),
        app_notify_url=None,
        app_private_key_string=open(ALIPAY_SETTING.get('APP_PRIVATE_KEY_STRING')).read(),
        alipay_public_key_string=open(ALIPAY_SETTING.get('ALIPAY_PUBLIC_KEY_STRING')).read(),
        sign_type=ALIPAY_SETTING.get('SIGN_TYPE'),
        debug=ALIPAY_SETTING.get('ALIPAY_DEBUG'),
        verbose=False
    )
    return alipay