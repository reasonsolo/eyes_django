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

class LostFoundTagSerializer(serializers.ModelSerializer):
    def save(self, data):
        return LostFoundTag(**data)

    class Meta:
        model = LostFoundTag
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
        fields = ('id', 'url')
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class PetLostSerializer(serializers.ModelSerializer):
    # publisher = UserBriefSerializer(read_only=True)
    materials = ValidSlugField(many=True, slug_field='url')
    tags = LostFoundTagSerializer(many=True)
    species = PetSpeciesSerializer(read_only=True)
    materials = PetMaterialSerializer(many=True)

    def create(self, data):
        materials_data = data.pop('materials')
        tags_str = data.pop('tags')

        lost = PetLost.objects.create(**data)
        user = self.context['request'].user.profile.first()

        lost.publisher = user
        lost.create_by = user
        lost.last_update_by = user

        for tag_str in tags_str:
            tag, _ = LostFoundTag.objects.get_or_create(name=tag_data)
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
                            'medical_status', 'case_status', 'audit_status', 'publish_charge_status')
        depth = 1


class LostFoundTagSerializer(serializers.ModelSerializer):

    def validate(self, data):
        pass

    class Meta:
        model = LostFoundTag
        fields = ('name', 'count')

