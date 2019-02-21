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
                "required": False,
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

    def create(self, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else 0
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
        species_id = data.pop('species') if 'species' in data else 0

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
        self.user = self.context['request'].user
        instance.publisher = self.user
        instance.create_by = self.user
        instance.last_update_by = self.user

    def set_species(self, instance, species_id):
        species = PetSpecies.objects.filter(id=int(species_id["id"])).first()
        instance.species = species


    class Meta:
        model = PetLost
        fields = ('id', 'publisher', 'species', 'species_str', 'pet_type', 'gender', 'birthday', 'lost_time',
                  'color', 'description', 'material_set', 'tags', 'medical_status', 'place',
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
    publisher = UserBriefSerializer(read_only=True)
    material_set = PetMaterialSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects)
    species = PetSpeciesSerializer()

    def set_user(self, instance):
        self.user = self.context['request'].user
        instance.publisher = self.user
        instance.create_by = self.user
        instance.last_update_by = self.user

    def create(self, data):
        material_set = data.pop('material_set') if 'material_set' in data else []
        tags_str = data.pop('tags') if 'tags' in data else []
        species_id = data.pop('species') if 'species' in data else 0

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
        species_id = data.pop('species') if 'species' in data else 0

        self.set_user(instance)
        self.set_species(instance, species_id)
        self.set_tags(instance, tags_str)
        self.set_material_set(instance, material_set)

        instance.save()
        return instance

    def set_species(self, instance, species_id):
        species = PetSpecies.objects.filter(id=int(species_id["id"])).first()
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
        fields = ('id', 'publisher', 'species', 'pet_type', 'color', 'tags', 'found_time',
                  'description', 'place', 'latitude', 'longitude',
                  'found_status', 'case_status', 'audit_status',
                  'view_count', 'like_count', 'repost_count', 'material_set')
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

    def save(self, data):
        user = self.context['request'].user
        data['sender'] = user
        return Message(**data)

    class Meta:
        model = Message
        fields = ('id', 'content', 'read_status', 'create_time', 'msg_thread', 'receiver', 'sender')
        read_only_fields = ('create_time', 'read_status', 'sender')


class MessageThreadSerializer(serializers.ModelSerializer):
    last_msg = MessageSerializer(read_only=True)

    def validate(self, data):
        user = self.context['request'].user
        if data['user_a'] == data['user_b'] or\
            (data['user_a'] != user and data['user_b'] != user):
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


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'img', 'start_time', 'end_time', 'banner_type', 'click_url')
