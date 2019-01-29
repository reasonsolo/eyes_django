import wx_auth.auth
from django.contrib.auth import get_user_model

class AuthBackend:
    def __init__(self):
        pass

    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        account = auth.verify_password(username, password)
        return account

    def authenticate(self, request, token=None):
        print('auth by token')
        if token is None and request is None:
            return None
        if token is None:
           authorization = request.headers.get('Authorization')
           if authorization is None:
               return None
           authorization_type, token = authorization.split(' ')

        if token is not None:
            result, account_id = auth.verify_auth('jwt ' + token)
            if result == False:
                return None
            else:
                return auth.get_user_by_id(account_id)
        return None

    def get_user(self, user_id):
        return auth.get_user_by_id(user_id)
