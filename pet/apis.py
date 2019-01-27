from django.shortcuts import render
from django.conf import settings
from django.db.models.query import QuerySet, EmptyQuerySet
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage

from rest_framework import viewsets, views, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser

from pet.models import *
from pet.serializers import *

from datetime import datetime, timedelta
from PIL import Image, ImageOps
from collections import namedtuple
import mimetypes
import io
import uuid
mimetypes.init()

# Create your views here.

def get_user_profile(request):
    user_profile = None
    if request.user is not None and not request.user.is_anonymous:
        user_profile = request.user.profile
    else:
        raise PermissionDenied
    return user_profile

class PetLostViewSet(viewsets.ModelViewSet):
    queryset = PetLost.objects.filter(flag=1)
    serializer_class = PetLostSerializer
    COORDINATE_RANGE=0.1  # this is about 11 KM

    def list(self, request):
        pet_type = request.GET.get('pet_type', None)
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        date_range = request.GET.get('date_range', None)
        place = request.GET.get('place', None)
        lost_queryset = PetLost.objects.filter(flag=1)
        if latitude != None and longitude != None:
            lost_queryset = lost_queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                         .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                         .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                         .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        elif place != None:
            lost_queryset = lost_queryset.filter(place=int(place))
        if pet_type != None:
            lost_queryset.filter(pet_type=int(pet_type))
        if date_range != None:
            start_time = datetime.now() - timedelta(days=date_range)
            lost_queryset.filter(create_time__gte=start_time)

        lost_list = lost_queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        user_profile = get_user_profile(self.request)
        if user_profile is not None:
            instance.last_update_by = user_profile
            instance.save()

    def perform_create(self, serializer):
        instance = serializer.save()
        user_profile = get_user_profile(self.request)
        if user_profile is not None:
            instance.create_by = user_profile
            instance.save()

    def perform_destroy(self, instance):
        instance.flag = 0
        user_profile = get_user_profile(self.request)
        instance.last_update_by = user_profile
        instance.save()

    @action(detail=True)
    def match_found(self, request, pk=None):
        COORDINATE_RANGE=0.1  # this is about 11 KM
        instance = self.get_object()
        place = instance.place
        latitude, longitude = instance.latitude, instance.longitude
        create_time = instance.create_time
        pet_type = instance.pet_type

        start_time = create_time - timedelta(days=30)
        end_time = create_time + timedelta(days=30)

        queryset = PetFound.objects.filter(flag=1, audit_status=1, case_status=0, pet_type=pet_type)\
                                   .filter(create_time__gte=start_time)\
                                   .filter(create_time__lte=end_time)
        place_queryset = PetFound.objects.none()
        if place is not None:
            place_queryset = queryset.filter(place=place)
        if latitude is not None and longitude is not None:
            coord_queryset = queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
            place_queryset = place_queryset | coord_queryset

        if isinstance(place_queryset, EmptyQuerySet):
            found_list = queryset.all()
        else:
            found_list = place_queryset.all()
        page = self.paginate_queryset(found_list)
        if page is not None:
            serializer = PetFoundSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])



class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


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

    def destroy(self, request, pk=None):
        instance = PetMaterial.objects.get(pk)
        if instance is None:
            raise Http404
        instance.flag = 0
        instance.save()
        return Response({})


class SpeciesListView(viewsets.ReadOnlyModelViewSet):
    queryset = PetSpecies.objects.filter(flag=1)
    serializer_class = PetSpeciesSerializer

    def list(self, request):
        species_list = PetSpecies.objects.filter(flag=1)
        serializer = self.get_serializer(species_list, many=True)
        return Response(serializer.data)

class PetFoundViewSet(viewsets.ModelViewSet):
    COORDINATE_RANGE=0.1  # this is about 11 KM
    queryset = PetFound.objects.filter(flag=1)
    serializer_class = PetFoundSerializer

    def list(self, request):
        pet_type = request.GET.get('pet_type', None)
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        date_range = request.GET.get('date_range', None)
        place = request.GET.get('place', None)
        queryset = PetFound.objects.filter(flag=1)
        if latitude != None and longitude != None:
            queryset = found_queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        elif place != None:
            queryset = queryset.filter(place=int(place))
        if pet_type != None:
            queryset.filter(pet_type=int(pet_type))
        if date_range != None:
            start_time = datetime.now() - timedelta(days=date_range)
            queryset.filter(create_time__gte=start_time)

        found_list = queryset.all()
        page = self.paginate_queryset(found_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])

    def retrieve(self, request, pk=None):
        instance = self.get_object(pk)
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        user_profile = get_user_profile(self.request)
        if user_profile is not None:
            instance.last_update_by = user_profile
            instance.save()

    def perform_create(self, serializer):
        instance = serializer.save()
        user_profile = get_user_profile(self.request)
        if user_profile is not None:
            instance.create_by = user_profile
            instance.save()

    def perform_destroy(self, instance):
        instance.flag = 0
        user_profile = get_user_profile(self.request)
        instance.last_update_by = user_profile
        instance.save()

    @action(detail=True)
    def match_lost(self, request, pk=None):
        instance = self.get_object(pk)
        place = instance.place
        latitude, longitude = instance.latitude, instance.longitude
        create_time = instance.create_time
        pet_type = instance.pet_type

        start_time = create_time - timedelta(days=30)
        end_time = create_time + timedelta(days=30)

        queryset = PetLost.objects.filter(flag=1, audit_status=1, case_status=0, pet_type=pet_type)\
                                  .filter(create_time__gte=start_time)\
                                  .filter(create_time__lte=end_time)
        place_queryset = PetLost.objects.none()
        if place is not None:
            place_queryset = queryset.filter(place=place)
        if latitude is not None and longitude is not None:
            coord_queryset = queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
            place_queryset = place_queryset | coord_queryset

        if place_queryset is None:
            lost_list = queryset.all()
        else:
            lost_list = place_queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            serializer = PetLostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])


class ActionLogAPIView(views.APIView):
    obj_mapping = {
        'lost': PetLost,
        'found': PetFound,
    }

    def get_object(self, obj, pk):
        try:
            obj_model = ActionLogAPIView.obj_mapping[obj]
            instance = obj_model.objects.get(pk=pk)
            return instance
        except:
            raise Http404

    def get(self, request, action, obj, pk):
        if action == 'like':
            return self.like(request, obj, pk)
        if action == 'follow':
            return self.follow(request, obj, pk)
        if action == 'like':
            return self.repost(request, obj, pk)

    def like(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = request.user
        if user is None or user.is_anonymous or user.profile is None:
            print(user.is_anonymous, user.profile)
            raise PermissionDenied
        profile = user.profile
        like_log, create = LikeLog.objects.get_or_create(**{'user':profile, obj:instance})

        if cancel == 1:
            if not create and like_log.flag:
                instance.like_count -= 1
                instance.save()
        else:
            if create or not like_log.flag:
                instance.like_count += 1
                instance.save()

        like_log.flag = False if cancel == 1 else True
        like_log.save()
        return Response({'count': instance.like_count})

    def follow(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = request.user
        if user is None or user.is_anonymous or user.profile is None:
            raise PermissionDenied
        profile = user.profile
        follow_log, create = FollowLog.objects.get_or_create(**{'user':profile, obj:instance})
        if cancel == 1:
            if not create and follow_log.flag:
                instance.follow_count -= 1
                instance.save()
        else:
            if create or not follow_log.flag:
                instance.follow_count += 1
                instance.save()

        follow_log.flag = False if cancel == 1 else True
        follow_log.save()
        return Response({'count': instance.follow_count})


    def repost(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = request.user
        if user is None or user.is_anonymous or user.profile is None:
            raise PermissionDenied
        profile = user.profile
        repost_log, create = RepostLog.objects.get_or_create(**{'user':profile, obj:instance})
        if cancel == 1:
            if not create and repost_log.flag:
                instance.repost_count -= 1
                instance.save()
        else:
            if create or not repost_log.flag:
                instance.repost_count += 1
                instance.save()

        repost_log.flag = False if cancel == 1 else True
        repost_log.save()
        return Response({'count': instance.repost_count})


# TimelineTuple = namedtuple('Timeline', ('lost', 'found'))
class FollowFeedsView(viewsets.ModelViewSet):
    serializer_class = FollowFeedsSerializer
    queryset = FollowLog.objects.filter(flag=1)
    def list(self, request):
        user_profile = get_user_profile(request)
        queryset = FollowLog.objects.filter(flag=1, user=user_profile)

        follow_list = queryset.all()
        page = self.paginate_queryset(follow_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])


class MessageThreadViewSet(viewsets.ModelViewSet):
    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.filter(flag=1)

    def list(self, request):
        user_profile = get_user_profile(request)
        queryset = MessageThread.objects.filter(flag=1)\
                                        .filter(Q(user_a=user_profile)|Q(user_b=user_profile))
        thread_list = queryset.all()
        page = self.paginate_queryset(thread_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response([])

    def retrieve(self, request, pk=None):
        user_profile = get_user_profile(request)
        msg_thread = MessageThread.objects.filter(flag=1)\
                                          .filter(Q(user_a=user_profile)|Q(user_b=user_profile)).first()
        if msg_thread is None:
            raise Http404
        return Response(self.get_serializer(msg_thread).data)

    def create(self, request):
        user_profile = get_user_profile(request)
        msg_thread = MessageThreadSerializer(data=request.data, context={'request': request})
        if msg_thread.is_valid():
            msg_thread.save()
        return Response(self.get_serializer(msg_thread).data)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.filter(flag=1)

    def get_user_Q(user_a, user_b):
        return (Q(user_a=user_a)&Q(user_b=user_b))|(Q(user_a=user_b)&Q(user_b=user_a))

    def get_or_create_thread(self, user_a, user_b):
        msg_thread = MessageThread.objects.filter(flag=1)\
            .filter(__class__.get_user_Q(user_a, user_b)).first()
        if msg_thread is None:
            msg_thread = MessageThread(user_a=user_a, user_b=user_b)
            msg_thread.save()
        return msg_thread

    def list(self, request, thread_pk=None):
        user_profile = get_user_profile(request)
        message_list = Message.objects.filter(flag=1, msg_thread=thread_pk).all()
        if len(message_list) > 0:
            if user_profile not in (message_list[0].sender, message_list[0].receiver):
                raise PermissionDenied
        page = self.paginate_queryset(message_list)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, thread_pk=None):
        user_profile = get_user_profile(request)
        message = MessageSerializer(data=request.data, context={'request': request, 'sender': user_profile})
        if message.is_valid(raise_exception=True):
            msg_thread = self.get_or_create_thread(user_profile, message.validated_data['receiver'])
            if msg_thread is None:
                return Reponse({'detail': u'找不到消息主题'})
        message.msg_thread = msg_thread
        message = message.save(message.validated_data)
        msg_thread.last_msg = message
        msg_thread.save()
        return Response(self.get_serializer(message).data)

    def perform_destroy(self, instance):
        instance.flag=0
        instance.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Message.objects.filter(flag=1)

    def get_obj(self, obj, obj_pk):
        if obj == 'lost':
            return PetLost.objects.filter(flag=1, pk=obj_pk).get()
        elif obj == 'found':
            return PetFound.objects.filter(flag=1, pk=obj_pk).get()
        else:
            raise Http404

    def list(self, request, obj=None, obj_pk=None):
        if obj == 'lost':
            queryset = Comment.objects.filter(flag=1, lost=obj_pk)
        elif obj == 'found':
            queryset = Comment.objects.filter(flag=1, found=obj_pk)
        else:
            raise Http404

        page = self.paginate_queryset(queryset.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def create(self, request, obj, obj_pk):
        user_profile = get_user_profile(request)
        ext_arg = {'publisher': user_profile, obj: self.get_obj(obj, obj_pk)}
        comment = CommentSerializer(data=request.data)
        if comment.is_valid(raise_exception=True):
            comment = comment.save(**ext_arg)
            return Response(self.get_serializer(comment).data)

