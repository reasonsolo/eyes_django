from rest_framework import serializers
from pet.models import *
from wx_auth.serializer import UserBriefSerializer

class ValidSlugField(serialzier.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        super(ValidSlugField, self).__init__(*args, **kwargs)
        self.model = kwargs['model']

    def get_queryset(self):
        return super(ValidSlugField, self).get_queryset().filter(flag=True)


class PetLostSerializer(serializers.ModelSerializer):
    publisher = UserBriefSerializer(read_only=True)
    materials = ValidSlugField(many=True, read_only=True, slug_field='url')
    valid_tags = LostFoundTag.objects.filter()
    tags = ValidSlugField(many=True, slug_field='name')

    class Meta:
        model = PetLost
        fields = ('publisher', 'species', 'pet_type', 'gender',
                  'color', 'description', 'materials', 'tags', )


