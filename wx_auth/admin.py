from django.contrib import admin
from wx_auth.models import *
# Register your models here.


@admin.register(User)
class WxAuthAdmin(admin.ModelAdmin):
    pass
