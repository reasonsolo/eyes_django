from wx_auth import auth
from django.contrib.auth import get_user_model

class AuthBackend:
    def __init__(self):
        pass

    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        account = auth.verify_password(username, password)
        request.user = account
        return account

    def authenticate(self, request, token=None):
        if token is None and request is None:
            print('no token and request object is available')
            return None
        if token is None:
           authorization = request.META.get('HTTP_AUTHORIZATION', None)
           if authorization is None:
               return None
           try:
               authorization_type, token_t = authorization.split(' ')
           except:
               return None

        if token_t is not None:
            result, account_id = auth.verify_auth('jwt ' + token_t)
            if result == False:
                return None
            else:
                user = auth.get_user_by_id(account_id)
                request.user = user
                return user
        return None

    def get_user(self, user_id):
        return auth.get_user_by_id(user_id)
