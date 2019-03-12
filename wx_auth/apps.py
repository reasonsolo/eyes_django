from os import environ

class WxAuthConfig:
    name = 'wx_auth'
    # JWT
    ISS = environ.get('ISS', 'iss')
    AUDIENCE = environ.get('AUDIENCE', 'audience')

    # 微信 小程序账号信息
    WXAPP_ID = environ.get('WXAPP_ID', 'wxc9005a5b8f18e404')
    WXAPP_SECRET = environ.get('WXAPP_SECRET', '88dd56352d2712c0946519f10b226a09')
    # SMS
    SMSAPP_ID = environ.get('SMSAPP_ID', '1400185060')
    SMSAPP_KEY = environ.get('SMSAPP_KEY', 'eb61ec1022c9ccec0d86d28206a5c061')
    # DB
    DB_USER = environ.get('DB_USER', 'dbuser')
    DB_PASSWORD = environ.get('DB_PASSWORD', 'Naibadbuser_060')
    DB_HOST = environ.get('DB_HOST', 'localhost')
    DB_PORT = environ.get('DB_PORT', '3306')
    DB_DATABASE = environ.get('DB_DATABASE', 'naiba_eyes')
