from rest_framework import serializers
from pet.models import *
#from wx_auth.serializer import UserBriefSerializer

class ValidSlugField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        super(ValidSlugField, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(ValidSlugField, self).get_queryset()#.filter(flag=True)


class PetSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetSpecies
        fields = ('id', 'pet_type', 'name')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }

class TagSerializer(serializers.ModelSerializer):
    def save(self, data):
        return Tag(**data)

    class Meta:
        model = Tag
        fields = ('id', 'count', 'name')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


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
    materials = ValidSlugField(many=True, slug_field='url')
    tags = TagSerializer(many=True)
    species = PetSpeciesSerializer(read_only=True)
    materials = PetMaterialSerializer(many=True)

    def create(self, data):
        materials_data = data.pop('materials')
        tags_str = data.pop('tags')

        lost = PetLost.objects.create(**data)
        user = self.context['request'].user.profile.first()

        user_profile = None if user is None or user.is_anonymous else user.profile

        lost.publisher = user_profile
        lost.create_by = user_profile
        lost.last_update_by = user_profile

        for tag_str in tags_str:
            tag, create = LostFoundTag.objects.get_or_create(name=tag_data)
            if create:
                tag.save()
            lost.tags.add(tag)

        return lost


    def save(self):
        data = self.validated_data
        lost = super(PetLostSerializer, self).save()
        ids = [m['id'] for m in data['materials']]
        materials = PetMaterial.objects.filter(id__in=ids).all()
        for mat in materials:
            mat.lost = lost
            mat.save()

        return lost

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
    materials = ValidSlugField(many=True, slug_field='url')
    tags = TagSerializer(many=True)
    species = PetSpeciesSerializer(read_only=True)
    materials = PetMaterialSerializer(many=True)

    def create(self, data):
        materials_data = data.pop('materials')
        tags_str = data.pop('tags')

        found = PetFound.objects.create(**data)
        user = self.context['request'].user
        user_profile = None if user is None or user.is_anonymous else user.profile

        found.publisher = user_profile
        found.create_by = user_profile
        found.last_update_by = user_profile

        for tag_str in tags_str:
            tag, create = Tag.objects.get_or_create(name=tag_data)
            if create:
                tag.save()
            found.tags.add(tag)

        return found

    def save(self):
        data = self.validated_data
        found = super(PetFoundSerializer, self).save()
        ids = [m['id'] for m in data['materials']]
        materials = PetMaterial.objects.filter(id__in=ids).all()
        for mat in materials:
            mat.found = found
            mat.save()

        return found

    class Meta:
        model = PetFound
        fields = ('id', 'publisher', 'species', 'pet_type', 'color', 'tags',
                  'description', 'region_id', 'place', 'latitude', 'longitude',
                  'found_status', 'case_status', 'audit_status',
                  'view_count', 'like_count', 'repost_count', 'materials')
        read_only_fields = ('view_count', 'repost_count', 'like_count',
                            'found_status', 'case_status', 'audit_status',)
        depth = 1



