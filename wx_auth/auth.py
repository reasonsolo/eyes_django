from wx_auth.apps import WxAuthConfig
from wx_auth.models import User
from django.contrib.auth.hashers import check_password

def register(request):
    account, token = get_user_info(request)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    account.phone = body.get('phone', None)
    if account.phone is None:
        return False, account, token
    else:
        account.save()
        return True, account, token

def verify_password(username, password):
    try:
        user = User.objects.get(username=username).first()
    except User.DoesNotExist:
        return None
    pwd_valid = check_password(password, user.password)
    if pwd_valid:
        return user
    return None

def get_user_by_name(name):
    return User.get_by_name(name)

def get_user_info(request):
    authorization = request.headers.get('Authorization')
    openid = None
    account = None
    result = False
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    if authorization:
        result, account_id = verify_auth(authorization)
    if result == False:
        openid = verify_wxapp(body['encrypted_data'], body['iv'], body['code'])
    else:
        account = User.objects.get(id=account_id)

    if openid:
        account = User.get_by_wxapp(openid)
        if not account:
            # create new account
            account = User.objects.create(wx_openid=openid,
                        wx_nickname=body.get('wx_nickname', None),
                        wx_avatar=body.get('wx_avatar', None),
                        wx_gender=body.get('wx_gender', 0),
                        wx_country=body.get('wx_country', None),
                        wx_province=body.get('wx_province', None),
                        wx_city=body.get('wx_city', None))
            account.save()
    token = create_token(account)
    return account, token

def get_wxapp_userinfo(encrypted_data, iv, code):
    from weixin.lib.wxcrypt import WXBizDataCrypt
    from weixin import WXAPPAPI
    from weixin.oauth2 import OAuth2AuthExchangeError
    appid = WxAuthConfig.WXAPP_ID
    secret = WxAuthConfig.WXAPP_SECRET
    api = WXAPPAPI(appid=appid, app_secret=secret)
    try:
        session_info = api.exchange_code_for_session_key(code=code)
    except OAuth2AuthExchangeError as e:
        raise Unauthorized(e.code, e.description)
    session_key = session_info.get('session_key')
    crypt = WXBizDataCrypt(appid, session_key)
    user_info = crypt.decrypt(encrypted_data, iv)
    return user_info

def verify_auth(token):
    try:
        authorization_type, token = authorization.split(' ')
        payload = jwt.decode(token, 'secret',
                             audience=Config.AUDIENCE,
                             algorithms=['HS256'])
    except ExpiredSignatureError:
        return False, 0
    if payload:
        return True, int(payload["sub"])
    return False, 0

def verify_wxapp(encrypted_data, iv, code):
    user_info = get_wxapp_userinfo(encrypted_data, iv, code)
    return user_info.get('openId', None)

def create_token(account):
    payload = {
        "iss": WxAuthConfig.ISS,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,
        "aud": WxAuthConfig.AUDIENCE,
        "sub": str(account.id),
        "nickname": account.wx_nickname,
        "scopes": ['open']
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return {'access_token': token, 'nickname': account.wx_nickname, 'account_id': str(account.id)}
