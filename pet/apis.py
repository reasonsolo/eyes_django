from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.core.files.storage import FileSystemStorage

from pet.models import *
from pet.serializers import *

import uuid

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


class MaterialUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def gen_filename(self, mime):
        return uuid.uuid1()

    def put(self, request, filename, format=None):
        file_obj = request.FILES['file']
        mime = requests.META.get('Content-Type', 'image/jpeg')
        user = request.user.profile
        fs = FileSystemStorage()
        filepath = fs.save(filename, file_obj)
        uploaded_file_url = fs.url(path)
        material = Material(mime_type=mime, size=file_obj._size, url=uploaded_file_url,
                            full_path=filepath, created_by=user, last_updated_by=user)
        material.save()
        ret = {'id': material.id, 'url': material.url}
        return Response(ret)



