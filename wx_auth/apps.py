from django.apps import AppConfig
from os import environ

class WxAuthConfig(AppConfig):
    name = 'wx_auth'
    # JWT
    ISS = environ.get('ISS', 'iss')
    AUDIENCE = environ.get('AUDIENCE', 'audience')

    # 微信 小程序账号信息
    WXAPP_ID = environ.get('WXAPP_ID', 'wxc9005a5b8f18e404')
    WXAPP_SECRET = environ.get('WXAPP_SECRET', '88dd56352d2712c0946519f10b226a09')
    # SMS
    SMSAPP_ID = environ.get('SMSAPP_ID', '1400186429')
    SMSAPP_KEY = environ.get('SMSAPP_KEY', '91034299f8e5d0021b38b92ac5f750cf')

