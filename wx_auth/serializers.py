from rest_framework import serializers
from wx_auth.models import User

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar_thumb', 'nickname')

class UserFullSerialiser(serializers.ModelSerializer):
    pass
