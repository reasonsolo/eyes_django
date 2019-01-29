from django.conf.urls import url
import wx_auth.views
urlpatterns = [
    url(r'^login$', wx_auth.views.login, name="login"),
    url(r'^register$', wx_auth.views.register, name="register"),
]
