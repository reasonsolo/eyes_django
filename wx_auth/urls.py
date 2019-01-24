from django.conf.urls import url
import wx_auth.auth
urlpatterns = [
url(r'^get_user_info$', auth.user_info, name="user_info"),
]
