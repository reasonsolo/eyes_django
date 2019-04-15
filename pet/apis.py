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
from wx_auth.models import User
from pet.serializers import *
from pet.messages import get_or_create_thread_by_user, update_msg_thread , init_user_system_threads
from eyes1000.settings import get_absolute_url

from datetime import datetime, timedelta
from PIL import Image, ImageOps
from collections import namedtuple
import os
import mimetypes
import io
import uuid

mimetypes.init()

# Create your views here.

COORDINATE_RANGE=0.2  # this is about 22 KM
MATCH_COORDINATE_RANGE=0.05

def ResultResponse(data):
    if not isinstance(data, list):
        data = [data]
    return Response({'results': data})

def get_user_or_none(request):
    request.user =  AuthBackend().authenticate(request)
    if request.user and not request.user.is_anonymous:
        return request.user
    return None

def get_user(request):
    user = get_user_or_none(request)
    if user is None:
        raise APIException(detail=u'用户未登录', code=401)
    return user

def get_user_by_openid(openid):
    if openid is None:
        return None
    users = User.objects.filter(wx_openid=openid)
    if len(users) == 0:
        return None
    return users[0]

def get_obj(obj, obj_pk, user):
    instance = None
    if obj == 'lost':
        instance = get_object_or_404(PetLost, pk=obj_pk)
    elif obj == 'found':
        instance = get_object_or_404(PetFound, pk=obj_pk)
    else:
        raise Http404
    if instance.audit_status != 1 and instance.publisher != user:
        raise PermissionDenied
    return instance

class PetLostViewSet(viewsets.ModelViewSet):
    queryset = PetLost.objects
    serializer_class = PetLostSerializer

    def list(self, request):
        user = get_user_or_none(self.request)
        pet_type = request.GET.get('pet_type', 1)
        longitude = request.GET.get('longitude', '')[:18]
        latitude = request.GET.get('latitude', '')[:18]
        date_range = request.GET.get('date_range', None)
        pet_type = 1 if pet_type == '' else int(pet_type)
        queryset = PetLost.objects.filter(case_status=0, audit_status=1, pet_type=pet_type)
        if latitude != None and latitude != '' and longitude != None and longitude != '':
            queryset = queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                         .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                         .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                         .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        if date_range is not None and date_range != '':
            start_time = datetime.now() - timedelta(days=date_range)
            queryset = queryset.filter(create_time__gte=start_time)
        if user is not None:
            queryset = queryset | PetLost.objects.filter(case_status=0, pet_type=pet_type, publisher=user)
        lost_list = queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetLost.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResultResponse([])

    def retrieve(self, request, pk=None):
        user = get_user_or_none(self.request)
        instance = get_obj('lost', pk, user)
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
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
        instance.create_by = user
        instance.last_update_by = user
        instance.save()
        if instance.species is not None:
            instance.species.count += 1
            instance.species.save()

    def perform_destroy(self, instance):
        user = get_user(self.request)
        if instance.publisher == user:
            instance.last_update_by = user
            instance.flag = 0
            instance.save()
        else:
            raise PermissionDenied

    @action(detail=True)
    def match_found(self, request, pk=None):
        user = get_user_or_none(self.request)
        instance = get_obj('lost', pk, user)
        latitude, longitude = instance.latitude, instance.longitude
        lost_time = instance.lost_time
        pet_type = instance.pet_type

        start_time = lost_time - timedelta(days=30)
        end_time = lost_time + timedelta(days=30)

        queryset = PetFound.objects.filter(lost=instance, audit_status=1)
        place_queryset = PetFound.objects.none()
        if latitude is not None and longitude is not None:
            coord_queryset = queryset.filter(longitude__lte=float(longitude)+MATCH_COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-MATCH_COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+MATCH_COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-MATCH_COORDINATE_RANGE)\
                                     .filter(audit_status=1, case_status=0, pet_type=pet_type)\
                                     .filter(found_time__gte=start_time)\
                                     .filter(found_time__lte=end_time)
            queryset = queryset | coord_queryset
            queryset = queryset.distinct()

        found_list = queryset.all()
        page = self.paginate_queryset(found_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetFound.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = PetFoundSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])

    @action(detail=True)
    def create_found(self, request, pk):
        user = get_user(self.request)
        instance = get_obj('lost', pk, user)
        found = PetFoundSerializer(data=request.data, context={'request': request})
        if found.is_valid(raise_exception=True):
            found = found.save(publisher=user, lost=instance)
            if found.species is not None:
                found.species.count += 1
                found.species.save()
            return ResultResponse(PetFoundSerializer(found).data)

    @action(detail=True)
    def update_case_status(self, request, pk):
        case_status = int(request.GET.get('case_status', '0'))
        user = get_user(self.request)
        instance = self.get_object()
        if instance.publisher == user:
            instance.case_status = case_status
            instance.save()
            return ResultResponse(self.get_serializer(instance, context={'request': request}).data)
        else:
            raise PermissionDenied

    @action(detail=True)
    def get_love_concern(self, request, pk):
        user = get_user(self.request)
        instance = self.get_object()
        love_help_records = instance.love_help_record_set
        return ResultResponse(LoveHelpRecordSerializer(love_help_records, many=True).data)


# TODO(zlz): test this
class PetCaseCloseViewSet(viewsets.ModelViewSet):
    queryset = PetCaseClose.objects
    serializer_class = PetCaseCloseSerializer

    def create_for_obj(self, request, obj, obj_pk):
        user = get_user(self.request)
        instance = get_object(obj, pk)
        if instance.publisher != user:
            raise PermissionDenied
        case_close = PetCaseCloseSerializer(data=request.data, context={'request': request})
        if case_close.is_valid(raise_exception=True):
            case_close = case_close.save(**{'publisher': user, obj:instance})
            return ResultResponse(PetCaseCloseSerializer(case_close, context={'request': request}).data)

    def retrieve_by_obj(self, request, obj, obj_pk):
        user = get_user_or_none(self.request)
        instance = get_object(obj, pk)
        if instance.publisher != user:
            raise PermissionDenied
        return ResultResponse(PetCaseCloseSerializer(data=instance,  context={'request': request}).data)

    def retrieve(self, request, pk):
        user = get_user_or_none(self.request)
        instance = self.get_object(pk)
        if instance.audit_status != 1 and instance.publisher != request.user:
            raise PermissionDenied
        return ResultResponse(PetCaseCloseSerializer(data=instance, context={'request': request}).data)


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = PetMaterial.objects
    serializer_class = PetMaterialSerializer

    def perform_destroy(self, instance):
        user = get_user(self.request)
        if instance.publisher == user:
            instance.flag = 0
            instance.save()
        else:
            raise PermissionDenied

    def retrieve(self, pk):
        material = self.get_object(pk)
        if material ==  None:
            raise Http404
        ret = {'id': material.id, 'url': get_absolute_url(material.url), 'thumbnail_url': get_absolute_url(material.thumb_url)}
        return ResultResponse(ret)


class MaterialUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    def gen_filename(self, mime):
        return str(uuid.uuid1())

    def post(self, request, format=None):
        user = get_user(request)

        file_obj = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'material'),
                               base_url=settings.MEDIA_URL + 'material')
        upload_filename = file_obj.name
        _, ext = os.path.splitext(upload_filename)
        filename = self.gen_filename(file_obj.content_type) + ext
        filepath = fs.save(filename, file_obj)
        uploaded_url = fs.url(filepath)

        image = Image.open(file_obj)
        image = image.convert('RGB')
        thumb = ImageOps.fit(image, settings.THUMB_SIZE, Image.ANTIALIAS)

        thumb_io = io.BytesIO()
        thumb.save(thumb_io, 'JPEG')
        thumb_io.seek(0)
        thumb_filename = 'thumb_' + filename
        thumb_filepath = fs.save(thumb_filename, thumb_io)
        thumb_url = fs.url(thumb_filepath)

        material = PetMaterial(publisher=user, mime_type=file_obj.content_type,
                               size=file_obj.size, url=uploaded_url, thumb_url=thumb_url,
                               create_by=user, last_update_by=user)
        material.save()
        ret = {'id': material.id, 'url': get_absolute_url(material.url), 'thumbnail_url': get_absolute_url(material.thumb_url)}
        return ResultResponse(ret)



class SpeciesListView(viewsets.ReadOnlyModelViewSet):
    queryset = PetSpecies.objects
    serializer_class = PetSpeciesSerializer

    def list(self, request):
        pet_type = int(request.GET.get('pet_type', 1))
        species_list = PetSpecies.objects
        top = PetSpecies.objects.filter(pet_type=pet_type).order_by('-count')[:9]
        ordered = PetSpecies.objects.filter(pet_type=pet_type).order_by('pinyin')

        serializer = PetSpeciesCollectionsSerrializer({'top': top, 'ordered': ordered})
        return ResultResponse(serializer.data)

class PetFoundViewSet(viewsets.ModelViewSet):
    queryset = PetFound.objects
    serializer_class = PetFoundSerializer

    def list(self, request):
        user = get_user_or_none(self.request)
        pet_type = request.GET.get('pet_type', 1)
        longitude = request.GET.get('longitude', None)
        latitude = request.GET.get('latitude', None)
        date_range = request.GET.get('date_range', None)
        pet_type = 1 if pet_type == '' else int(pet_type)
        queryset = PetFound.objects.filter(case_status=0, audit_status=1, pet_type=pet_type)
        if latitude != None and latitude != '' and longitude != None and longitude != '':
            queryset = queryset.filter(longitude__lte=float(longitude)+COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-COORDINATE_RANGE)
        if date_range != None:
            start_time = datetime.now() - timedelta(days=int(date_range))
            queryset = queryset.filter(create_time__gte=start_time)

        if user is not None:
            queryset = queryset | PetFound.objects.filter(case_status=0, pet_type=pet_type, publisher=user)
        found_list = queryset.all()
        page = self.paginate_queryset(found_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetFound.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])

    def retrieve(self, request, pk=None):
        user = get_user_or_none(self.request)
        instance = get_obj('found', pk, user)
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
        return ResultResponse(serializer.data)

    def perform_update(self, serializer):
        user = get_user(self.request)
        instance = serializer.save()
        if instance.publisher == user:
            instance.last_update_by = user
            instance.save()
        else:
            raise PermissionDenied

    def perform_create(self, serializer):
        user = get_user(self.request)
        instance = serializer.save()
        instance.create_by = user
        instance.publisher = user
        instance.save()
        if instance.species is not None:
            instance.species.count += 1
            instance.species.save()

    def perform_destroy(self, instance):
        instance.flag = 0
        user = get_user(self.request)
        if instance.publisher == user:
            instance.last_update_by = user
            instance.save()
        else:
            raise PermissionDenied

    @action(detail=True)
    def match_lost(self, request, pk=None):
        user = get_user_or_none(self.request)
        instance = self.get_object(pk)
        latitude, longitude = instance.latitude, instance.longitude
        found_time = instance.found_time
        pet_type = instance.pet_type

        start_time = found_time - timedelta(days=30)
        end_time = found_time + timedelta(days=30)

        queryset = PetLost.objects.filter(audit_status=1, found=instance)
        if latitude is not None and longitude is not None:
            coord_queryset = queryset.filter(longitude__lte=float(longitude)+MATCH_COORDINATE_RANGE)\
                                     .filter(longitude__gte=float(longitude)-MATCH_COORDINATE_RANGE)\
                                     .filter(latitude__lte=float(latitude)+MATCH_COORDINATE_RANGE)\
                                     .filter(latitude__gte=float(latitude)-MATCH_COORDINATE_RANGE)\
                                     .filter(lost_time__gte=start_time)\
                                     .filter(lost_time__lte=end_time)\
                                     .filter(case_status=0, pet_type=pet_type, audit_status=1)
            queryset = queryset | coord_queryset
            queryset = queryset.distinct()

        lost_list = queryset.all()
        page = self.paginate_queryset(lost_list)
        if page is not None:
            ids = [instance.id for instance in page]
            PetLost.objects.filter(id__in=ids).update(view_count=F('view_count')+1)
            serializer = self.get_serializer(page, many=True, context={'request': request})
            serializer = PetLostSerializer(page, many=True, context={'request': request})
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
            return ResultResponse(PetLostSerializer(lost, context={'request': request}).data)

    @action(detail=True)
    def update_case_status(self, request, pk):
        case_status = int(request.GET.get('case_status', '0'))
        user = get_user(self.request)
        instance = self.get_object()
        instance.case_status = case_status
        instance.save()
        return ResultResponse(self.get_serializer(instance, context={'request': request}).data)

    @action(detail=True)
    def get_love_concern(self, request, pk):
        user = get_user(self.request)
        instance = self.get_object()
        love_help_records = instance.love_help_record_set
        return ResultResponse(LoveHelpRecordSerializer(love_help_records, many=True).data)


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
        if action == 'repost':
            return self.repost(request, obj, pk)
        if action == 'lovehelp':
            return self.love_help(request, obj, pk)
        if action == 'loveconcern':
            return self.love_concern(request, obj, pk)

    def like(self, request, obj=None, pk=None):
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        user = get_user(request)
        like_log, create = LikeLog.all_objects.get_or_create(**{'user':user, obj:instance})

        if cancel == 1:
            if not create and like_log.flag:
                instance.like_count -= 1
                instance.save()
            like_log.flag = False
            like_log.save()
        else:
            if create or not like_log.flag:
                instance.like_count += 1
                instance.save()

        like_log.flag = False if cancel == 1 else True
        like_log.save()
        return ResultResponse({'count': instance.like_count})

    def follow(self, request, obj=None, pk=None):
        user = get_user(request)
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        follow_log, create = FollowLog.all_objects.get_or_create(**{'user':user, obj:instance})
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
        user = get_user(request)
        cancel = int(request.GET.get('cancel', 0))
        instance = self.get_object(obj, pk)
        repost_log, create = RepostLog.all_objects.get_or_create(**{'user':user, obj:instance})
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

    def love_help(self, request, obj=None, pk=None):
        instance = self.get_object(obj, pk)
        openid = request.GET.get('openid', None)
        if openid is None:
            raise Http404
        lovehelp_log, create = LoveHelpLog.all_objects.get_or_create(**{'openid':openid, obj:instance})

        if create or not lovehelp_log.flag:
            instance.love_help_count += 1
            instance.save()
            user = get_user_by_openid(openid)
            if user is not None:
                user.love_help_num += 1
                user.save()
                love_help_record = LoveHelpRecord.all_objects.get_or_create(**{'user': user,
                                                                               'count': 1,
                                                                               obj:instance})


        lovehelp_log.flag = True
        lovehelp_log.save()
        return ResultResponse({'count': instance.love_help_count})

    def love_concern(self, request, obj=None, pk=None):
        instance = self.get_object(obj, pk)
        openid = request.GET.get('openid', None)
        from_openid = request.GET.get('from_openid', None)
        if openid is None or from_openid is None:
            raise Http404
        loveconcern_log, create = LoveConcernLog.all_objects.get_or_create(**{'openid':openid, obj:instance})

        if create or not loveconcern_log.flag:
            instance.love_concern_count += 1
            instance.save()
            user = get_user_by_openid(from_openid)
            if user is not None:
                user.bring_love_concern_num += 1
                user.save()
                LoveHelpRecord.objects.filter(**{'user': user, obj:instance}).update(count=F('count')+1)


        loveconcern_log.flag = True
        loveconcern_log.from_openid = from_openid
        loveconcern_log.save()
        return ResultResponse({'count': instance.love_concern_count})

# TimelineTuple = namedtuple('Timeline', ('lost', 'found'))
class LikeFeedsView(viewsets.ModelViewSet):
    serializer_class = LikeFeedsSerializer
    queryset = LikeLog.objects
    def list(self, request):
        user = get_user(request)
        queryset = LikeLog.objects.filter(user=user)\
                                  .filter((~Q(lost__case_status=2)&Q(lost__audit_status=1))
                                           |(~Q(found__case_status=2)&Q(found__audit_status=1)))

        like_list = queryset.all()
        page = self.paginate_queryset(like_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return ResultResponse([])


class MessageThreadViewSet(viewsets.ViewSet):
    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects

    def list(self, request):
        user = get_user(request)
        if user.msg_thr_set.filter(msg_type=3).count() == 0:
            init_user_system_threads(user)
        msg_thr = MessageThread.objects.filter(user=user, hide=False)
        post_msg_thread = msg_thr.filter(msg_type=1)

        return ResultResponse(MessageThreadSerializer(msg_thr.all(),
                                                      many=True,
                                                      context={'request': request}).data)

    def retrieve(self, request, pk=None):
        user = get_user(request)
        receiver = None
        if pk == None:
            receiver_id = int(request.GET.get('receiver', 0))
            receiver = User.objects.filter(pk=receiver_id).first()
            if receiver is None or receiver.id == user.id:
                raise Http404
            msg_thr, create = MessageThread.objects.get_or_create(user=user, peer=receiver)
        else:
            msg_thr = MessageThread.objects.filter(user=user, pk=pk).first()
        if msg_thr is None:
            raise Http404
        if msg_thr.msg_type == 3:
            msgs = Message.objects.filter(msg_type=3).order_by('id')
            msg_thr.last_msg = msgs.first()
        else:
            msgs = msg_thr.messages.order_by('id')

        if msgs.count() > 0:
            msg_thr.read = msgs.last().id
            msg_thr.new = 0
            msg_thr.save()

        serializer = MessageAndThreadSerializer({'thread':msg_thr, 'msgs': msgs, 'user': user, 'peer': receiver})
        response = ResultResponse(serializer.data)
        msg_thr.messages.filter(receiver=user).update(read_status=1)

        # msg_thr.messages.filter(receiver=user, read_status=0).update(read_status=1)

        return response

    @action(detail=True)
    def hide(self, request, pk=None):
        user = get_user(request)
        msg_thr = MessageThread.objects.filter(receiver=user, pk=pk).first()
        msg_thr.hide = True
        msg_thr.save()
        return ResultResponse('')

    @action(detail=True)
    def create_msg(self, request, pk=None):
        user = get_user(request)
        msg_thread = MessageThread.objects.filter(pk=pk).first()
        if msg_thread is None:
            raise Http404
        if msg_thread.user != user:
            raise PermissionDenied
        message = MessageSerializer(data=request.data, context={'request': request})
        if message.is_valid(raise_exception=True):
            message.save(**{'receiver': msg_thread.peer, 'sender': user})
        return ResultResponse(MessageSerializer(message).data)


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
        ext_arg = {'publisher': user, obj: get_obj(obj, obj_pk, user), 'audit_status':1}
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
        pet_type = request.GET.get('pet_type', 1)
        pet_type = 1 if pet_type == '' else int(pet_type)
        queryset = obj_class.objects.filter(publisher=user, pet_type=pet_type)
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



