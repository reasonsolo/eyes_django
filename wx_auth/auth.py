from wx_auth.apps import WxAuthConfig
from wx_auth.models import UserProfile

def get_value(data, key, default):
    return data[key] if data.has_key(key) else default

def get_user_info(request):
    authorization = request.headers.get('Authorization')
    openid = None
    account = None
    result = False
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    if authorization:
        result, account_id = verify_auth(authorization)
        account = UserProfile.objects.get(id=account_id)

    if result == False:
        openid = verify_wxapp(body['encrypted_data'], body['iv'], body['code'])
    if openid:
        account = UserProfile.get_by_wxapp(openid)
        if not account:
            # create new account
            account = UserProfile.objects.create(wx_openid=openid,
                        wx_nickname=get_value(body, 'wx_nickname', None),
                        wx_avatar=get_value(body, 'wx_avatar', None),
                        wx_gender=get_value(body, 'wx_gender', 0),
                        wx_country=get_value(body, 'wx_country', None),
                        wx_province=get_value(body, 'wx_province', None),
                        wx_city=get_value(body, 'wx_city', None))
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
        return account
    raise Unauthorized('invalid_wxapp_code {0}'.format(code))

def create_token(account):
    payload = {
        "iss": WxAuthConfig.ISS,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400 * 7,
        "aud": WxAuthConfig.AUDIENCE,
        "sub": str(account.id),
        "nickname": account.nickname,
        "scopes": ['open']
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return {'access_token': token, 'nickname': account.wx_nickname, 'account_id': str(account.id)}
