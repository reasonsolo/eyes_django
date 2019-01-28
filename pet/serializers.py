# encoding: utf-8
from rest_framework import serializers
from pet.models import *
#from wx_auth.serializer import UserBriefSerializer


class PetSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetSpecies
        fields = ('id', 'pet_type', 'name')
        #extra_kwargs = {
        #    "id": {
        #        "read_only": False,
        #        "required": False,
        #    },
        #}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('count', 'name')


class RecommendedTagSerializer(serializers.Serializer):
    top_tags = TagSerializer(many=True, read_only=True)
    user_tags = TagSerializer(many=True, read_only=True)


class PetMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetMaterial
        fields = ('id', 'url', 'thumb_url')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class PetLostSerializer(serializers.ModelSerializer):
    # publisher = UserBriefSerializer(read_only=True)
    materials = PetMaterialSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects)
    species = PetSpeciesSerializer(read_only=True)

    def create(self, data):
        materials = data.pop('materials') if 'materials' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []

        instance = PetLost.objects.create(**data)
        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_materials(instance, materials)

        instance.save()
        return instance

    def update(self, instance, data):
        materials = data.pop('materials') if 'materials' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []

        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_materials(instance, materials)

        instance.save()
        return instance

    def set_materials(self, instance, materials):
        instance.material_set.clear()
        material_ids = [material['id'] for material in materials]
        PetMaterial.objects.filter(id__in=material_ids).update(lost=instance)

    def set_tags(self, instance, tags_str):
        instance.tags.clear()
        for tag_str in tags_str:
            tag, create = Tag.objects.get_or_create(name=tag_str)
            instance.tags.add(tag)
            tag_user, create = TagUsage.objects.get_or_create(tag=tag, user=self.user_profile)

    def set_user(self, instance):
        self.user = self.context['request'].user
        self.user_profile = None if self.user is None or self.user.is_anonymous else self.user.profile
        instance.publisher = self.user_profile
        instance.create_by = self.user_profile
        instance.last_update_by = self.user_profile

    class Meta:
        model = PetLost
        fields = ('id', 'publisher', 'species', 'pet_type', 'gender',
                  'color', 'description', 'materials', 'tags', 'medical_status',
                  'longitude', 'latitude', 'view_count', 'repost_count', 'like_count',
                  'case_status', 'audit_status', 'publish_charge_status')
        read_only_fields = ('view_count', 'repost_count', 'like_count',
                            'case_status', 'audit_status', 'publish_charge_status')
        depth = 1


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'count')


class PetSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetSpecies
        fields = ('id', 'name', 'pet_type')


class PetFoundSerializer(serializers.ModelSerializer):
    materials = PetMaterialSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects)
    species = PetSpeciesSerializer(read_only=True)

    def set_user(self, instance):
        self.user = self.context['request'].user
        self.user_profile = None if self.user is None or self.user.is_anonymous else self.user.profile
        instance.publisher = self.user_profile
        instance.create_by = self.user_profile
        instance.last_update_by = self.user_profile

    def create(self, data):
        materials = data.pop('materials') if 'materials' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []

        instance = PetFound.objects.create(**data)
        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_materials(instance, materials)

        instance.save()
        return instance

    def update(self, instance, data):
        materials = data.pop('materials') if 'materials' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []

        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_materials(instance, materials)

        instance.save()
        return instance

    def set_materials(self, instance, materials):
        instance.material_set.clear()
        material_ids = [material['id'] for material in materials]
        PetMaterial.objects.filter(id__in=material_ids).update(found=instance)

    def set_tags(self, instance, tags_str):
        instance.tags.clear()
        for tag_str in tags_str:
            tag, create = Tag.objects.get_or_create(name=tag_str)
            instance.tags.add(tag)
            tag_user, create = TagUsage.objects.get_or_create(tag=tag, user=self.user_profile)

    class Meta:
        model = PetFound
        fields = ('id', 'publisher', 'species', 'pet_type', 'color', 'tags',
                  'description', 'region_id', 'place', 'latitude', 'longitude',
                  'found_status', 'case_status', 'audit_status',
                  'view_count', 'like_count', 'repost_count', 'materials')
        read_only_fields = ('view_count', 'repost_count', 'like_count',
                            'found_status', 'case_status', 'audit_status',)
        depth = 1


class TimelineSerializer(serializers.Serializer):
    found = PetFoundSerializer(many=True)
    lost = PetLostSerializer(many=True)


class FollowFeedsSerializer(serializers.ModelSerializer):
    found = PetFoundSerializer()
    lost = PetLostSerializer()

    class Meta:
        model = FollowLog
        fields = ('id', 'lost', 'found')
        depth = 2


class MessageSerializer(serializers.ModelSerializer):

    def validate(self, data):
        user_profile = self.context['sender']
        if user_profile is None or user_profile == data['receiver']:
            raise serializers.ValidationError(u'用户未登录/不匹配')
        return data

    def save(self, data):
        user_profile = self.context['request'].user.profile
        data['sender'] = user_profile
        return Message(**data)

    class Meta:
        model = Message
        fields = ('id', 'content', 'read_status', 'create_time', 'msg_thread', 'receiver', 'sender')
        read_only_fields = ('create_time', 'read_status', 'sender')


class MessageThreadSerializer(serializers.ModelSerializer):
    last_msg = MessageSerializer(read_only=True)

    def validate(self, data):
        user_profile = self.context['request'].user.profile
        if data['user_a'] == data['user_b'] or\
            (data['user_a'] != user_profile and data['user_b'] != user_profile):
            raise serializers.ValidationError(u'发信用户错误')
        return data

    class Meta:
        model = MessageThread
        fields = ('id', 'user_a', 'user_b', 'message_type', 'last_msg')
        read_only_fields = ('message_type',)


class MessageAndThreadSerializer(serializers.Serializer):
    msg_thread = MessageThreadSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.filter(flag=1), required=False)

    class Meta:
        model = Comment
        fields = ('id', 'publisher', 'reply_to', 'create_time',  'content',
                  'last_update_time')
        depth = 1
