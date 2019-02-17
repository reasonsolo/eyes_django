from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
# Create your models here.

SHORT_CHAR=5
MID_CHAR=50
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

class DictableModel:
    def to_dict(self):
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
        return d


class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_register', True)
        return self._create_user(username, password, **extra_fields)


class User(DictableModel, AbstractBaseUser, PermissionsMixin):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    username = models.CharField(max_length=MID_CHAR, default=None, null=True, unique=True)
    #password = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    avatar = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    avatar_thumb = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    phone = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    is_register = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
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
    objects = UserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return '%d:%s' % (self.id, self.wx_nickname)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @classmethod
    def get_by_wxapp(cls, openid):
        account = cls.objects.get(wx_openid=openid).first()
        return account

    @classmethod
    def get_by_name(cls, name):
        account = cls.objects.get(username=name).first()
        return account
