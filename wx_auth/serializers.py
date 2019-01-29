from rest_framework import serializers
from wx_auth.models import User

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'wx_nickname', 'wx_avatar')

class UserFullSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
