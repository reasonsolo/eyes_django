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
GENDER_CHOICE = (
    (0, 'Unknown'),
    (1, 'Male'),
    (2, 'Female'),
)
class JsonableModel(models.Model):
    def toJSON(self):
        fields = []
        for field in self._meta.fields:
            fields.append(field.name)
    
        d = {}
        import datetime
        for attr in fields:
            if isinstance(getattr(self, attr),datetime.datetime):
                d[attr] = getattr(self, attr).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(getattr(self, attr),datetime.date):
                d[attr] = getattr(self, attr).strftime('%Y-%m-%d')
            else:
                d[attr] = getattr(self, attr)
    
        import json
        return json.dumps(d)

class UserProfile(JsonableModel):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    nickname = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    avatar = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    avatar_thumb = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    phone = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    is_register = models.BooleanField(default=False)
    birthday = models.DateField(null=True)
    address = models.URLField(max_length=50, blank=True, null=True)
    member_score = models.IntegerField(default=0)
    credit_score = models.IntegerField(default=0)
    wx_openid = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_nickname = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_gender = models.IntegerField(choices=GENDER_CHOICE, default=0)
    wx_avatar = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    wx_country = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_province = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    wx_city = models.URLField(max_length=MID_CHAR, blank=True, null=True)
    last_ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)
    join_ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)

    def __str__(self):
        return '%d:%s' % (self.id, self.nickname)

    @classmethod
    def get_by_wxapp(cls, openid):
        account = cls.objects(wx_openid=openid).first()
        return account

