from django.db import models
from django.contrib.auth import models as auth_models

# Create your models here.

SHORT_CHAR=5
MID_CHAR=20
LONG_CHAR=200

FLAG_CHOICE = (
    (0, 'No'),
    (1, 'Yes'),
)

class UserProfile(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    account = models.OneToOneField(auth_models.User, on_delete=models.SET_NULL, blank=True, null=True, related_name='profile')

    nickname = models.CharField(max_length=MID_CHAR)
    avatar = models.URLField(max_length=LONG_CHAR)
    avatar_thumb = models.URLField(max_length=LONG_CHAR)
    bio  = models.CharField(max_length=LONG_CHAR)
    open_bio = models.BooleanField(default=True)

    wx_openid = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_nickname = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_avatar = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    last_ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)
    join_ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)

    def __str__(self):
        return '%d:%s' % (self.id, self.nickname)
