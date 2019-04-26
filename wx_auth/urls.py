from django.conf.urls import url
import wx_auth.views
urlpatterns = [
    url(r'^login$', wx_auth.views.login, name="login"),
    url(r'^register$', wx_auth.views.register, name="register"),
    url(r'^is_openid_registered$', wx_auth.views.is_openid_registered, name="is_openid_registered"),
    url(r'^get_openid_by_code$', wx_auth.views.get_openid_by_code, name="get_openid_by_code"),
    url(r'^get_miniprogram_qrcode$', wx_auth.views.get_miniprogram_qrcode, name="get_miniprogram_qrcode"),
    url(r'^get_raw_miniprogram_qrcode$', wx_auth.views.get_raw_miniprogram_qrcode, name="get_raw_miniprogram_qrcode"),
    url(r'^get_location$', wx_auth.views.get_location, name='get_location'),
    url(r'^convert_avatar_url$', wx_auth.views.convert_user_avatar_url, name='convert_user_avatar_url'),
]
