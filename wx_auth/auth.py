from wx_auth.apps import WxAuthConfig
from wx_auth.models import User
from django.contrib.auth.hashers import check_password
from weixin.lib.wxcrypt import WXBizDataCrypt
from weixin import WXAPPAPI
from weixin.oauth2 import OAuth2AuthExchangeError
import json
import time
import jwt

def get_phone_by_code(request):
    appid = WxAuthConfig.WXAPP_ID
    session_key = request.GET.get('session_key', None)
    encrypted_data = request.GET.get('encrypted_phone', None) 
    iv = request.GET.get('iv', None)
    if session_key is None or encrypted_data is None or iv is None:
        return None
    crypt = WXBizDataCrypt(appid, session_key)
    phone_info = crypt.decrypt(encrypted_data, iv)
    return phone_info.get('phoneNumber', None)

def is_openid_registered(request):
    openid = request.GET.get('openid', None)
    return is_openid_registered_impl(openid)

def get_openid_by_code(request):
    code = request.GET.get('code', None)
    appid = WxAuthConfig.WXAPP_ID
    secret = WxAuthConfig.WXAPP_SECRET
    api = WXAPPAPI(appid=appid, app_secret=secret)
    try:
        session_info = api.exchange_code_for_session_key(code=code)
    except OAuth2AuthExchangeError as e:
        return False, None, None
    session_key = session_info.get('session_key', None)
    openid = session_info.get('openid', None)
    reg_status = is_openid_registered_impl(openid)
    return True, openid, reg_status

def is_openid_registered_impl(openid):
    if openid is None:
        return None
    try:
        user = User.objects.get(wx_openid=openid)
    except User.DoesNotExist:
        return False
    return user.is_register

def register(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    phone = body.get('phone', None)
    if phone is None:
        phone = get_phone_by_code(request)

    if phone is not None:
        account, token = get_user_info(request)
        account.phone = phone
        account.is_register = True
        account.username = body.get('nickname', account.wx_nickname)
        account.gender = body.get('gender', account.wx_gender)
        account.birthday = body.get('birthday', None)
        account.save()
        return True, account, token
    else:
        return False, None, None

def verify_password(username, password):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    pwd_valid = check_password(password, user.password)
    if pwd_valid:
        return user
    return None

def get_user_info(request):
    #authorization = request.headers.get('Authorization', None)
    authorization = request.META.get('HTTP_AUTHORIZATION', None)
    openid = None
    account = None
    account_id = None
    result = False
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    if authorization is not None:
        result, account_id = verify_auth(authorization)
    if result == False:
        openid = body.get('openid', None)
    else:
        account = User.objects.get(id=account_id)

    if openid:
        try:
            account = User.objects.get(wx_openid=openid)
        except User.DoesNotExist:
            # create new account
            account = User.objects.create(wx_openid=openid,
                        wx_nickname=body.get('wx_nickname', None),
                        username=body.get('username', None),
                        wx_avatar=body.get('wx_avatar', None),
                        wx_gender=body.get('wx_gender', 0),
                        wx_country=body.get('wx_country', None),
                        wx_province=body.get('wx_province', None),
                        wx_city=body.get('wx_city', None),
                        phone=body.get('phone', None))
            account.save()
    token = create_token(account)
    return account, token

def get_wxapp_userinfo(encrypted_data, iv, code):
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
        authorization_type, token = token.split(' ')
        payload = jwt.decode(token, 'secret',
                             audience=WxAuthConfig.AUDIENCE,
                             algorithms=['HS256'])
    except Exception as e:
        print(e)
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
    return token.decode('ascii')
