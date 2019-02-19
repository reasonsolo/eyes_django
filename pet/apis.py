from django.shortcuts import render
from django.conf import settings
from django.db.models.query import QuerySet, EmptyQuerySet
from django.db.models import Q, F
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from rest_framework.settings import api_settings

from rest_framework import viewsets, views, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.pagination import LimitOffsetPagination

from wx_auth.backends import AuthBackend
from pet.models import *
from pet.serializers import *

from datetime import datetime, timedelta
from PIL import Image, ImageOps
from collections import namedtuple
import os
import mimetypes
import io
import uuid
mimetypes.init()

# Create your views here.

class Http401(APIException):
    def __init__(self):
        super().__init__(details='需要登录', code=401)

def get_absolute_url(url):
    return "http://www.1000eye.com.cn" + url

def ResultResponse(data):
    if not isinstance(data, list):
        data = [data]
    return Response({'results': data})

def get_user(request):
    request.user =  AuthBackend().authenticate(request)
    if  request.user is not None:
        return request.user
    raise APIException(detail=u'用户未登录', code=401)

def get_user_or_none(request):
    request.user =  AuthBackend().authenticate(request)
    if request.user is not None and not request.user.is_anonymous:
        return request.user
    return None

def get_obj(obj, obj_pk, user):
    instance = None
    if obj == 'lost':
        instance = get_object_or_404(PetLost, pk=obj_pk)
    elif obj == 'found':
        instance = get_object_or_404(PetFound, pk=obj_pk)
    else:
        raise Http404
    if (instance.case_status == 2 and instance.audit_status != 1) or instance.publisher != user:
        raise PermissionDenied
    return instance

class PetLostViewSet(viewsets.ModelViewSet):
    queryset = PetLost.objects
    serializer_class = PetLostSerializer
    COORDINATE_RANGE=0.1  # this is about 11 KM

    def list(self, request):
        pet_type = request.GET.get('pet_type', None)
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        date_range = request.GET.get('date_range', None)
        place = request.GET.get('place', None)
        lost_queryset = PetLost.objects.filter(case_status=0, audit_status=1)
        if latitude != None and longitude != None:
            lost_queryset = lost_queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                         .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                         .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                         .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        if pet_type != None:
            lost_queryset.filter(pet_type=int(pet_type))
        if date_range != None:
            start_time = datetime.now() - timedelta(days=date_range)
            lost_queryset.filter(create_time__gte=start_time)

        lost_list = lost_queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetLost.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResultResponse([])

    def retrieve(self, request, pk=None):
        user = get_user_or_none(self.request)
        instance = get_obj('lost', pk, user)
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return ResultResponse(serializer.data)

    def perform_update(self, serializer):
        user = get_user(self.request)
        instance = self.get_object()
        if instance.publisher != user:
            raise PermissionDenied
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
        instance.last_update_by = user
        instance.save()

    def perform_create(self, serializer):
        user = get_user(self.request)
        instance = serializer.save()
        if user is not None:
            instance.create_by = user
            instance.last_update_by = user
            instance.save()

    def perform_destroy(self, instance):
        instance.flag = 0
        user = get_user(self.request)
        instance.last_update_by = user
        instance.save()

    @action(detail=True)
    def match_found(self, request, pk=None):
        COORDINATE_RANGE=0.1  # this is about 11 KM
        user = get_user_or_none(self.request)
        instance = get_obj('lost', pk, user)
        latitude, longitude = instance.latitude, instance.longitude
        lost_time = instance.lost_time
        pet_type = instance.pet_type

        start_time = lost_time - timedelta(days=30)
        end_time = lost_time + timedelta(days=30)

        queryset = PetFound.objects.filter(audit_status=1, case_status=0, pet_type=pet_type)\
                                   .filter(found_time__gte=start_time)\
                                   .filter(found_time__lte=end_time)
        queryset = queryset | PetFound.objects.filter(lost=instance)
        place_queryset = PetFound.objects.none()
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
            ids = [instance.id for instance in page]
            PetFound.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = PetFoundSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])

    @action(detail=True)
    def create_found(self, request, pk):
        user = get_user(self.request)
        instance = get_obj('lost', pk, user)
        found = PetFoundSerializer(data=request.data)
        if found.is_valid(raise_exception=True):
            found = found.save(publisher=user, lost=lost)
            return ResultResponse(PetFoundSerializer(found).data)

    @action(detail=True)
    def update_case_status(self, request, pk):
        case_status = int(request.GET.get('case_status', '0'))
        user = get_user(self.request)
        instance = self.get_object(pk)
        instance.case_status = case_status
        instance.save()
        return ResultResponse(self.get_serializer(instance).data)


# TODO(zlz): test this
class PetCaseCloseViewSet(viewsets.ModelViewSet):
    queryset = PetCaseClose.objects
    serializer_class = PetCaseCloseSerializer

    def create_for_obj(self, request, obj, obj_pk):
        user = get_user(self.request)
        instance = get_object(obj, pk)
        if instance.publisher != user:
            raise PermissionDenied
        case_close = PetCaseCloseSerializer(data=request.data)
        if case_close.is_valid(raise_exception=True):
            case_close = case_close.save(**{'publisher': user, obj:instance})
            return ResultResponse(PetCaseCloseSerializer(case_close).data)

    def retrieve_by_obj(self, request, obj, obj_pk):
        user = get_user_or_none(self.request)
        instance = get_object(obj, pk)
        if instance.publisher != user:
            raise PermissionDenied
        return ResultResponse(PetCaseCloseSerializer(data=instance).data)

    def retrieve(self, request, pk):
        instance = self.get_object(pk)
        if instance.audit_status != 1 and instance.publisher != request.user:
            raise PermissionDenied
        return ResultResponse(PetCaseCloseSerializer(data=instance).data)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = PetMaterial.objects
    serializer_class = PetMaterialSerializer

    def perform_destroy(self, instance):
        instance.flag = 0
        instance.save()

    def retrieve(self, pk):
        material = self.get_object(pk)
        if material ==  None:
            raise Http404
        ret = {'id': material.id, 'url': get_absolute_url(material.url), 'thumbnail_url': get_absolute_url(material.thumb_url)}
        return ResultResponse(ret)


class MaterialUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    def gen_filename(self, mime):
        ext = mimetypes.guess_extension(mime)
        if ext == '.jpe':
            ext = '.jpg'
        return str(uuid.uuid1()) + ext, ext

    def post(self, request, format=None):
        user = get_user(request)

        file_obj = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'material'),
                               base_url=settings.MEDIA_URL + 'material')
        filename, ext = self.gen_filename(file_obj.content_type)
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

        material = PetMaterial(mime_type=file_obj.content_type, size=file_obj.size,
                            url=uploaded_url, thumb_url=thumb_url,
                            create_by=user, last_update_by=user)
        material.save()
        ret = {'id': material.id, 'url': get_absolute_url(material.url), 'thumbnail_url': get_absolute_url(material.thumb_url)}
        return ResultResponse(ret)



class SpeciesListView(viewsets.ReadOnlyModelViewSet):
    queryset = PetSpecies.objects
    serializer_class = PetSpeciesSerializer

    def list(self, request):
        species_list = PetSpecies.objects
        serializer = self.get_serializer(species_list, many=True)
        return ResultResponse(serializer.data)

class PetFoundViewSet(viewsets.ModelViewSet):
    COORDINATE_RANGE=0.1  # this is about 11 KM
    queryset = PetFound.objects
    serializer_class = PetFoundSerializer

    def list(self, request):
        pet_type = request.GET.get('pet_type', None)
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        date_range = request.GET.get('date_range', None)
        queryset = PetFound.objects.filter(case_status=0, audit_status=1)
        if latitude != None and longitude != None:
            queryset = found_queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        if pet_type != None:
            queryset.filter(pet_type=int(pet_type))
        if date_range != None:
            start_time = datetime.now() - timedelta(days=date_range)
            queryset.filter(create_time__gte=start_time)

        found_list = queryset.all()
        page = self.paginate_queryset(found_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetFound.objects.filter(id__in=ids).update(view_count=F(view_count)+1)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])

    def retrieve(self, request, pk=None):
        instance = self.get_object(pk)
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return ResultResponse(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        user = get_user(self.request)
        if user is not None:
            instance.last_update_by = user
            instance.save()

    def perform_create(self, serializer):
        instance = serializer.save()
        user = get_user(self.request)
        if user is not None:
            instance.create_by = user
            instance.save()

    def perform_destroy(self, instance):
        instance.flag = 0
        user = get_user(self.request)
        instance.last_update_by = user
        instance.save()

    @action(detail=True)
    def match_lost(self, request, pk=None):
        instance = self.get_object(pk)
        latitude, longitude = instance.latitude, instance.longitude
        found_time = instance.found_time
        pet_type = instance.pet_type

        start_time = found_time - timedelta(days=30)
        end_time = found_time + timedelta(days=30)

        queryset = PetLost.objects.filter(audit_status=1, case_status=0, pet_type=pet_type)\
                                  .filter(lost_time__gte=start_time)\
                                  .filter(lost_time__lte=end_time)
        queryset = queryset | PetLost.objects.filter(found=instance)
        place_queryset = PetLost.objects.none()
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
            ids = [instance.id for instance in page]
            PetLost.objects.filter(id__in=ids).update(view_count=F(view_count)+1)
            serializer = self.get_serializer(page, many=True)
            serializer = PetLostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])

    @action(detail=True)
    def create_lost(self, request, pk):
        user = get_user(self.request)
        found = self.get_object(pk)
        lost = PetLostSerializer(request.data)
        if lost.is_valid(raise_exception=True):
            lost = lost.save(publisher=user, found=found)
            return ResultResponse(PetLostSerializer(lost).data)

    @action(detail=True)
    def update_case_status(self, request, pk):
        case_status = int(request.GET.get('case_status', '0'))
        user = get_user(self.request)
        instance = self.get_object(pk)
        instance.case_status = case_status
        instance.save()
        return ResultResponse(self.get_serializer(instance).data)

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
        if action == 'boost':
            return self.boost(request, obj, pk)

    def boost(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = get_user(request)
        like_log, create = BoostLog.objects.get_or_create(**{'user':user, obj:instance})

        if cancel == 1:
            if not create and boost_log.flag:
                instance.boost_count -= 1
                instance.save()
        else:
            if create or not like_log.flag:
                instance.like_count += 1
                instance.save()

    def like(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = get_user(request)
        like_log, create = LikeLog.objects.get_or_create(**{'user':user, obj:instance})

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
        return ResultResponse({'count': instance.like_count})

    def follow(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = get_user(request)
        follow_log, create = FollowLog.objects.get_or_create(**{'user':user, obj:instance})
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
        return ResultResponse({'count': instance.follow_count})


    def repost(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = get_user(request)
        repost_log, create = RepostLog.objects.get_or_create(**{'user':user, obj:instance})
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
        return ResultResponse({'count': instance.repost_count})


# TimelineTuple = namedtuple('Timeline', ('lost', 'found'))
class FollowFeedsView(viewsets.ModelViewSet):
    serializer_class = FollowFeedsSerializer
    queryset = FollowLog.objects
    def list(self, request):
        user = get_user(request)
        queryset = FollowLog.objects.filter(user=user)\
                                    .filter((~Q(lost__case_status=2)&Q(lost__audit_status=1))
                                             |(~Q(found__case_status=2)&Q(found__audit_status=1)))

        follow_list = queryset.all()
        page = self.paginate_queryset(follow_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])


def get_or_create_thread_by_user(user_a, user_b):
    if user_a.id > user_b.id:
        user_a, user_b = user_b, user_a
    elif user_a.id == user_b.id:
        raise PermissionDenied
    msg_thread = MessageThread.objects.filter(user_a=user_a, user_b=user_b).first()
    if msg_thread is None:
        msg_thread = MessageThread(user_a=user_a, user_b=user_b)
        msg_thread.save()
    return msg_thread


class MessageThreadViewSet(viewsets.ModelViewSet):
    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects

    def list(self, request):
        user = get_user(request)
        queryset = MessageThread.objects.filter(Q(user_a=user)|Q(user_b=user))
        thread_list = queryset.all()
        serializer = self.get_serializer(thread_list, many=True)
        return ResultResponse(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_user(request)
        msg_thread = MessageThread.objects.filter(Q(user_a=user)|Q(user_b=user)).first()
        if msg_thread is None:
            raise Http404
        return ResultResponse(self.get_serializer(msg_thread).data)

    def create(self, request):
        user = get_user(request)
        msg_thread = MessageThreadSerializer(data=request.data, context={'request': request})
        if msg_thread.is_valid():
            msg_thread.save()
        return ResultResponse(self.get_serializer(msg_thread).data)

    @action(detail=True)
    def relate_thread(self, request, obj, obj_pk):
        user = get_user(request)
        if obj == 'lost':
            obj_class = PetLost
        elif obj == 'found':
            obj_class = PetFound
        else:
            raise Http404
        related_obj = obj_class.objects.filter(pk).first()
        if related_obj is None:
            raise Http404
        user_a = user
        user_b = related_obj.publisher
        msg_thread = get_or_create_thread_by_user(user_a, user_b)
        messages = Message.objects.filter(msg_thread=msg_thread)
        serializer = MessageAndThreadSerializer(msg_thread=msg_thread,
                                                messages=messages)
        return ResultResponse(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects

    def list(self, request, thread_pk=None):
        user = get_user(request)
        msg_thread = MessageThread.objects.filter(pk=thread_pk).get()
        message_list = Message.objects.filter(msg_thread=thread_pk).all()
        if user != msg_thread.user_a and user != msg_thread.user_b:
            raise PermissionDenied
        serializer = MessageAndThreadSerializer(messages=message_list, msg_thread=msg_thread)
        return ResultResponse(serializer.data)

    def create(self, request, thread_pk=None):
        user = get_user(request)
        message = MessageSerializer(data=request.data, context={'request': request})
        if message.is_valid(raise_exception=True):
            msg_thread = get_or_create_thread_by_user(user, message.validated_data['receiver'])
            if msg_thread is None:
                return Reponse({'detail': u'找不到消息主题'})
        message = message.save(msg_thread=msg_thread)
        msg_thread.last_msg = message
        msg_thread.save()
        return ResultResponse(self.get_serializer(message).data)

    def perform_destroy(self, instance):
        instance.flag=0
        instance.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Message.objects

    def list(self, request, obj=None, obj_pk=None):
        user = get_user(request)
        if obj == 'lost':
            queryset = Comment.objects.filter(lost=obj_pk, audit_status=1)
        elif obj == 'found':
            queryset = Comment.objects.filter(found=obj_pk, audit_status=1)
        else:
            raise Http404

        page = self.paginate_queryset(queryset.all())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def create(self, request, obj, obj_pk):
        user = get_user(request)
        ext_arg = {'publisher': user, obj: get_obj(obj, obj_pk, user)}
        comment = CommentSerializer(data=request.data)
        if comment.is_valid(raise_exception=True):
            comment = comment.save(**ext_arg)
            return ResultResponse(self.get_serializer(comment).data)


class MyPostView(views.APIView, LimitOffsetPagination):
    def get(self, request, obj):
        user = get_user(request)
        if obj == 'lost':
            obj_class = PetLost
            serializer_class = PetLostSerializer
        elif obj == 'found':
            obj_class = PetFound
            serializer_class = PetFoundSerializer
        else:
            raise Http404
        queryset = obj_class.objects.filter(publisher=user)
        page = self.paginate_queryset(queryset.all(), request=request)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

class TagView(views.APIView):
    def get(self, request):
        user = get_user(request)
        top_tags = Tag.objects.order_by('-count')[:5]
        user_tags = [tag_usage.tag for tag_usage in user.pet_tag_usage_set.all()]
        serializer = RecommendedTagSerializer({'top_tags': top_tags, 'user_tags':user_tags})
        return ResultResponse(serializer.data)

    def post(self, request):
        user = get_user(request)
        tag = TagSerializer(data=request.data)
        tag.is_valid(raise_exception=True)
        tag = tag.save()
        return ResultResponse(TagSerializer(tag).data)


class BannerViewSet(viewsets.ModelViewSet):
    serializer_class = BannerSerializer
    queryset = Banner.objects

    def list(self, request):
        banner_type = int(request.GET.get('type', 0))
        num = int(request.GET.get('num', 5))
        banners = Banner.objects.filter(start_time__lt=timezone.now(),
                                        end_time__gt=timezone.now(),
                                        audit_status=1,
                                        banner_type__in=[banner_type, 0, 1])  # add default/ad banner
        banners = banners.order_by('?')[:num]
        Banner.objects.filter(pk__in=[b.id for b in banners]).update(show_times=F('show_times')+1)
        return ResultResponse(self.get_serializer(banners, many=True).data)

    @action(detail=True)
    def click(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk, audit_status=1)
        banner.click_times += 1
        banner.save()
        return redirect(banner.click_url)



