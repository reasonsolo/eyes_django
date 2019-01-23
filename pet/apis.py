from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.core.files.storage import FileSystemStorage

from pet.models import *
from pet.serializers import *

from PIL import Image, ImageOps
import mimetypes
import io
import uuid
mimetypes.init()

# Create your views here.

COORDINATE_RANGE=0.1  # this is about 11 KM

class PetLostViewSet(viewsets.ModelViewSet):
    queryset = PetLost.objects.filter(flag=True)
    serializer_class = PetLostSerializer

    def list(self, request):
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        place = request.GET.get('place', None)
        lost_queryset = PetLost.objects
        if latitude != None and longitude != None:
            lost_queryset = lost_queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                         .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                         .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                         .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        elif place != None:
            lost_queryset = lost_queryset.filter(place_id=int(place))

        lost_list = lost_queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])


    def detail(self, request, pk=None):
        pet_lost = get_object_or_404(queryset, pk=pk)
        return Response(serializer(pet_lost).data)

    def update(self, request, pk=None):
        pet_lost = get_object_or_404(queryset, pk=pk)
        pass

class ImageUploadParser(FileUploadParser):
    media_type = 'Image/*'

class MaterialUploadView(views.APIView):
    parser_classes = (ImageUploadParser,)

    def gen_filename(self, mime):
        ext = mimetypes.guess_extension(mime)
        if ext == '.jpe':
            ext = '.jpg'
        return str(uuid.uuid1()) + ext, ext

    def put(self, request, format=None):
        file_obj = request.FILES['file']
        mime = request.META.get('Content-Type', 'image/jpeg')

        user_profile = None
        if request.user is not None and not request.user.is_anonymous:
            user_profile = request.user.profile

        fs = FileSystemStorage()
        filename, ext = self.gen_filename(mime)
        filepath = fs.save(filename, file_obj)
        uploaded_url = fs.url(filepath)

        image = Image.open(file_obj)
        thumb = ImageOps.fit(image, settings.THUMB_SIZE, Image.ANTIALIAS)

        thumb_io = io.BytesIO()
        thumb.save(thumb_io, 'JPEG')
        thumb_io.seek(0)
        thumb_filename = 'thumb_' + filename
        thumb_filepath = fs.save(thumb_filename, thumb_io)
        thumb_url = fs.url(thumb_filepath)

        material = PetMaterial(mime_type=mime, size=file_obj.size,
                            url=uploaded_url, thumb_url=thumb_url,
                            create_by=user_profile, last_update_by=user_profile)
        material.save()
        ret = {'id': material.id, 'url': material.url, 'thumbnail_url': material.thumb_url}
        return Response(ret)



