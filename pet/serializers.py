# encoding: utf-8
from eyes1000.settings import get_absolute_url
from rest_framework import serializers
from pet.models import *
from wx_auth.serializers import UserBriefSerializer


class PetSpeciesSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()

    def get_img(self, species):
        if species.img is not None:
            return get_absolute_url(species.img.url)
        else:
            return ''

    class Meta:
        model = PetSpecies
        fields = ('id', 'pet_type', 'name', 'count', 'pinyin', 'img')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": True,
            },
        }

class PetSpeciesCollectionsSerrializer(serializers.Serializer):
    top = PetSpeciesSerializer(many=True, read_only=True)
    ordered = PetSpeciesSerializer(many=True, read_only=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('count', 'name')


class RecommendedTagSerializer(serializers.Serializer):
    top_tags = TagSerializer(many=True, read_only=True)
    user_tags = TagSerializer(many=True, read_only=True)


class PetMaterialSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    thumb_url = serializers.SerializerMethodField()

    def get_thumb_url(self, material):
        if material.thumb_url is not None:
            return get_absolute_url(material.thumb_url)
        else:
            return ''

    def get_url(self, material):
        if material.url is not None:
            return get_absolute_url(material.url)
        else:
            return ''

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
    publisher = UserBriefSerializer(read_only=True)
    material_set = PetMaterialSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects)
    species = PetSpeciesSerializer()
    comment_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    def get_comment_count(self, instance):
        return instance.comment_set.count()

    def get_liked(self, instance):
        if 'request' not in self.context:
            return False
        user = self.context['request'].user
        if user is not None and not user.is_anonymous:
            return LikeLog.objects.filter(user=user, lost=instance).count() != 0
        else:
            return False


    def create(self, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else {}
        instance = PetLost.objects.create(**data)

        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_material_set(instance, material_set)
        self.set_species(instance, species_id)

        instance.save()
        return instance

    def update(self, instance, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else {}

        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_material_set(instance, material_set)
        self.set_species(instance, species_id)

        instance.save()
        return instance

    def set_material_set(self, instance, material_set):
        instance.material_set.clear()
        material_ids = [material['id'] for material in material_set]
        PetMaterial.objects.filter(id__in=material_ids, publisher=self.user).update(lost=instance)

    def set_tags(self, instance, tags_str):
        instance.tags.clear()
        for tag_str in tags_str:
            tag, create = Tag.objects.get_or_create(name=tag_str)
            instance.tags.add(tag)
            tag_user, create = TagUsage.objects.get_or_create(tag=tag, user=self.user)

    def set_user(self, instance):
        if 'request' in self.context:
            self.user = self.context['request'].user
            instance.publisher = self.user
            instance.create_by = self.user
            instance.last_update_by = self.user

    def set_species(self, instance, species_id):
        species = PetSpecies.objects.filter(id=int(species_id["id"])).first()
        instance.pet_type = species.pet_type
        instance.species = species


    class Meta:
        model = PetLost
        fields = ('id', 'publisher', 'species', 'species_str', 'pet_type', 'gender', 'birthday', 'lost_time',
                  'color', 'description', 'material_set', 'tags', 'medical_status', 'place', 'reward', 'nickname',
                  'longitude', 'latitude', 'view_count', 'repost_count', 'like_count', 'comment_count',
                  'case_status', 'audit_status', 'publish_charge_status',
                  'create_time', 'last_update_time', 'liked', 'love_help_count', 'love_concern_count')
        read_only_fields = ('view_count', 'repost_count', 'like_count', 'comment_count',
                            'case_status', 'audit_status', 'publish_charge_status',
                            'create_time', 'last_update_time', 'liked', 'love_help_count', 'love_concern_count')
        depth = 1


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'count')


class PetFoundSerializer(serializers.ModelSerializer):
    publisher = UserBriefSerializer(read_only=True)
    material_set = PetMaterialSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects)
    species = PetSpeciesSerializer(required=False)

    comment_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    def get_comment_count(self, instance):
        return instance.comment_set.count()

    def get_liked(self, instance):
        if 'request' not in self.context:
            return False
        user = self.context['request'].user
        if user is not None and not user.is_anonymous:
            return LikeLog.objects.filter(user=user, found=instance).count() != 0
        else:
            return False

    def set_user(self, instance):
        if 'request' in self.context:
            self.user = self.context['request'].user
            instance.publisher = self.user
            instance.create_by = self.user
            instance.last_update_by = self.user

    def create(self, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else {}

        instance = PetFound.objects.create(**data)
        self.set_species(instance, species_id)
        self.set_user(instance)
        self.set_tags(instance, tags_str)
        self.set_material_set(instance, material_set)

        instance.save()
        return instance

    def update(self, instance, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else {}

        self.set_user(instance)
        self.set_species(instance, species_id)
        self.set_tags(instance, tags_str)
        self.set_material_set(instance, material_set)

        instance.save()
        return instance

    def set_species(self, instance, species_id):
        if 'id' in species_id:
            species = PetSpecies.objects.filter(id=int(species_id["id"])).first()
            instance.pet_type = species.pet_type
            instance.species = species

    def set_material_set(self, instance, material_set):
        instance.material_set.clear()
        material_ids = [material['id'] for material in material_set]
        PetMaterial.objects.filter(id__in=material_ids, publisher=self.user).update(found=instance)

    def set_tags(self, instance, tags_str):
        instance.tags.clear()
        for tag_str in tags_str:
            tag, create = Tag.objects.get_or_create(name=tag_str)
            instance.tags.add(tag)
            tag_user, create = TagUsage.objects.get_or_create(tag=tag, user=self.user)

    class Meta:
        model = PetFound
        fields = ('id', 'publisher', 'species', 'pet_type', 'color', 'tags', 'found_time', 'gender',
                  'description', 'place', 'latitude', 'longitude', 'found_status', 'case_status', 'audit_status',
                  'view_count', 'like_count', 'repost_count', 'material_set', 'comment_count',
                  'create_time', 'last_update_time', 'liked', 'love_help_count', 'love_concern_count')
        read_only_fields = ('view_count', 'repost_count', 'like_count', 'comment_count'
                            'found_status', 'case_status', 'audit_status',
                            'create_time', 'last_update_time', 'liked', 'love_help_count', 'love_concern_count')
        depth = 1


class TimelineSerializer(serializers.Serializer):
    found = PetFoundSerializer(many=True)
    lost = PetLostSerializer(many=True)


class LikeFeedsSerializer(serializers.ModelSerializer):
    found = PetFoundSerializer()
    lost = PetLostSerializer()

    class Meta:
        model = LikeLog
        fields = ('id', 'lost', 'found')
        depth = 2


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(required=False)
    receiver = UserBriefSerializer(required=False)

    class Meta:
        model = Message
        fields = ('id', 'content', 'create_time', 'receiver', 'sender', 'lost', 'found')
        read_only_fields = ('create_time', 'sender', 'receiver')


class MessageThreadSerializer(serializers.ModelSerializer):
    last_msg = MessageSerializer(read_only=True)
    #messages = MessageSerializer(many=True, read_only=True)
    peer = UserBriefSerializer()
    class Meta:
        model = MessageThread
        fields = ('id', 'msg_type', 'peer', 'read', 'new', 'last_msg', 'msg_type')#, 'messages')
        depth = 1


class MessageAndThreadSerializer(serializers.Serializer):
    msgs = MessageSerializer(many=True, read_only=True)
    thread = MessageThreadSerializer(read_only=True)
    user = UserBriefSerializer(read_only=True)
    peer = UserBriefSerializer(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    publisher = UserBriefSerializer(read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.filter(flag=1), required=False)

    class Meta:
        model = Comment
        fields = ('id', 'publisher', 'reply_to', 'create_time',  'content',
                  'last_update_time')
        depth = 1

class PetCaseCloseSerializer(serializers.ModelSerializer):
    lost = PetLostSerializer(read_only=True)
    found = PetLostSerializer(read_only=True)
    material_set = PetMaterialSerializer(many=True)

    def create(self, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []

        instance = PetCaseClose.objects.create(**data)
        self.set_user(instance)
        self.set_material_set(instance, material_set)

        instance.save()
        return instance

    def set_material_set(self, instance, material_set):
        instance.material_set.clear()
        material_ids = [material['id'] for material in material_set]
        PetMaterial.objects.filter(id__in=material_ids, publisher=self.user).update(close=instance)

    class Meta:
        model = PetCaseClose
        fields = ('id', 'lost', 'found', 'description', 'material_set')


class LoveHelpRecordSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    class Meta:
        model = LoveHelpRecord
        fields = ('id', 'lost', 'found', 'count', 'user', 'concern_count')



class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'img', 'start_time', 'end_time', 'banner_type', 'click_url')
