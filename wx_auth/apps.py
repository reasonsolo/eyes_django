from django.apps import AppConfig
from os import environ

class WxAuthConfig(AppConfig):
    name = 'wx_auth'
    # JWT
    ISS = environ.get('ISS', 'iss')
    AUDIENCE = environ.get('AUDIENCE', 'audience')

    # 微信 小程序账号信息
    WXAPP_ID = environ.get('WXAPP_ID', 'appid')
    WXAPP_SECRET = environ.get('WXAPP_SECRET', 'secret')

