# encoding: utf-8
from django.db import models
from django.db.models import Q,F
from django.utils import timezone
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.conf import settings
from datetime import datetime
from wx_auth.models import User

import os

SHORT_CHAR=5
MID_CHAR=20
LONG_CHAR=200

FLAG_CHOICE = (
    (0, '否'),
    (1, '是'),
)
GENDER_CHOICE = (
    (0, u'未知'),
    (1, u'男'),
    (2, u'女'),
)
CASE_STATUS = (
    (0, u'有效'),
    (1, u'已关闭'),
    (2, u'已过期'),
)
AUDIT_STATUS = (
    (0, '待审核'),
    (1, '已通过'),
    (2, '已拒绝'),
)
CHARGE_STATUS = (
    (0, '未付款'),
    (1, '付款失败'),
    (2, '付款成功'),
    (3, '免费'),
)
CONTACT_STATUS = (
    (0, 'NotContact'),
    (1, 'Contacted'),
)
BOOST_KPI_TYPE = (
    (0, '无'),
    (1, '浏览量'),
)
MEDICAL_STATUS = (
	(0, '无'),
	(1, '已绝育'),
	(2, '已免疫'),
	(3, '已除虫'),
)
PET_TYPE = (
    (0, '其他'),
    (1, '猫'),
    (2, '狗'),
)
FOUND_STATUS = (
    (0, '在身边'),
    (1, '在医院'),
    (2, '不在身边'),
)
MATERIAL_TYPE = (
    (0, '视频'),
    (1, '图片'),
)

MESSAGE_TYPE = (
    (0, '私信'),
    (1, '发布'),
    (2, '关注'),
    (3, '系统'),
)
READ_STATUS = (
    (0, '未读'),
    (1, '已读'),
)
BANNER_TYPE = (
    (0, '默认'),
    (1, '广告'),
    (2, '寻宠'),
    (3, '寻主'),
)

def today():
    return timezone.now().date()

# filter out flag=0 by default
class FlaggedModelManager(models.Manager):
    def get_queryset(self):
        return super(FlaggedModelManager, self).get_queryset().filter(flag=1)

class CommonMixin(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    create_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_%(app_label)s_%(class)s_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(User,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_%(app_label)s_%(class)s_set')
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-create_time']


class AuditMixin(models.Model):
    def __init__(self, *args, **kwargs):
        super(AuditMixin, self).__init__(*args, **kwargs)
        self.__old_audit_status = self.audit_status

    def audit_update(self, _from, _to):
        from pet.messages import create_audit_msg
        create_audit_msg(self)

    def save(self, *args, **kwargs):
        if self.__old_audit_status != self.audit_status:
            self.audit_update(self.__old_audit_status, self.audit_status)
        super(AuditMixin, self).save(*args, **kwargs)
        self.__old_audit_status = self.audit_status

    class Meta:
        abstract = True


class PetLost(CommonMixin, AuditMixin):
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='published_lost_set')
    nickname = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True)
    species_str = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    pet_type = models.IntegerField(choices=PET_TYPE, blank=True, null=True)
    lost_time = models.DateTimeField(blank=True, null=True, default=timezone.now)
    birthday = models.DateField(blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, default=1)
    color = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    case_status = models.IntegerField(choices=CASE_STATUS, default=0)
    # IMPORTANT: do NOT use update() to update audit_status, or the audit message will be missing
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)
    reward = models.IntegerField(default=0)
    is_in_boost = models.BooleanField(default=False)
    boost_kpi_type = models.IntegerField(choices=BOOST_KPI_TYPE, default=0)
    boost_amount = models.IntegerField(default=0, help_text='单位分')
    boost_scope = models.IntegerField(default=0, help_text='单位米')
    boost_count = models.IntegerField(default=0)
    publish_charge_status = models.IntegerField(choices=CHARGE_STATUS, default=0)
    publish_charge_amount = models.IntegerField(default=0, help_text='单位分')
    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    follow_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)
    medical_status = models.CharField(max_length=MID_CHAR, blank=True, null=True)

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return '%d:%s@%s-%s' % (self.id, self.publisher.wx_nickname if self.publisher is not None else 'None',
                                self.place, self.get_case_status_display())

    def show_materials(self):
        html = ''
        for material in self.material_set.all():
            html += '<img src="%s" />' % material.thumb_url
        return mark_safe(html)

    def save(self, *args, **kwargs):
        AuditMixin.save(self, *args, **kwargs)


class PetFound(CommonMixin, AuditMixin):
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='published_found_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True)
    found_time = models.DateTimeField(blank=True, null=True, default=timezone.now)
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True)
    pet_type = models.IntegerField(choices=PET_TYPE, default=1)
    color = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    found_status = models.IntegerField(choices=FOUND_STATUS, default=0)
    case_status = models.IntegerField(choices=CASE_STATUS, default=0)
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)

    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    follow_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    boost_count = models.IntegerField(default=0)

    tags = models.ManyToManyField('Tag', blank=True)

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return '%d:%s@%s-%s' % (self.id, self.publisher.wx_nickname if self.publisher is not None else 'None',
                                self.place, self.get_case_status_display())

    def show_materials(self):
        html = ''
        for material in self.material_set.all():
            html += '<img src="%s" height=100px width=100px/>' % material.thumb_url
        return mark_safe(html)

    def save(self, *args, **kwargs):
        AuditMixin.save(self, *args, **kwargs)


class Tag(CommonMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=MID_CHAR, unique=True, db_index=True)
    count = models.IntegerField(default=0)

    class Meta:
        ordering = ['count']

    def __str__(self):
        return self.name


class TagUsage(CommonMixin):
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, blank=True, null=True, related_name='tag_usage_set')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='tag_usage_set')
    count = models.IntegerField(default=0)
    last_usage = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-count', '-last_usage']

    def save(self, *args, **kwargs):
        self.last_usage = datetime.now()
        self.count += 1
        self.tag.count += 1
        self.tag.save()
        return super(TagUsage, self).save(*args, **kwargs)


class Comment(CommonMixin):
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='published_comment_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, null=True, blank=True, related_name='comment_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, null=True, blank=True, related_name='comment_set')
    content = models.TextField()
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)
    reply_to = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, blank=True, related_name='reply_set')

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        super(Comment, self).save(*args, **kwargs)

        from pet.messages import update_lost_comment_msg, update_found_comment_msg
        if self.lost is not None and self.publisher != self.lost.publisher:
            update_lost_comment_msg(self.lost)
        elif self.found is not None and self.publisher != self.instance.publisher:
            update_found_comment_msg(self.found)


class Message(CommonMixin):
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='received_message_set')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sent_message_set')
    content = models.TextField(default='')
    msg_type = models.IntegerField(choices=MESSAGE_TYPE, default=0)
    read_status = models.IntegerField(choices=READ_STATUS, default=0)

    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, null=True, blank=True)
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, null=True, blank=True)

    new_comment = models.IntegerField(default=0)
    audit_change = models.IntegerField(default=0)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        is_create =  self.pk is None
        super(Message, self).save(*args, **kwargs)
        from pet.messages import update_private_msg_thread, update_publisher_msg_thread
        if is_create:
            if self.msg_type == 0:
                update_private_msg_thread(self)
            elif self.msg_type == 1:
                update_publisher_msg_thread(self)
            elif self.msg_type == 3:
                system_msg_threads = MessageThread.objects.filter(msg_type=3)
                system_msg_threads.update(new=F('new')+1, last_msg=self, hide=False)


class MessageThread(CommonMixin):
    msg_type = models.IntegerField(choices=MESSAGE_TYPE, default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='msg_thr_set')
    peer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='msg_thr_as_peer_set')
    read = models.IntegerField(default=0)
    new = models.IntegerField(default=0)
    last_msg = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True)
    hide = models.BooleanField(default=False)
    messages = models.ManyToManyField('Message', blank=True, related_name='msg_thread_set')

    #class Meta:
    #    unique_together = ('user_a', 'user_b')

class MessageRelation(CommonMixin):
    msg_thread = models.ForeignKey(MessageThread, on_delete=models.SET_NULL, null=True)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, null=True, related_name='msg_relation_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, null=True, related_name='msg_relation_set')

    def save(self,  *args, **kwargs):
        relation = MessageRelation.objects.filter(msg_thread=self.msg_thread, lost=self.lost, found=self.found).first()
        if relation is not None:
            return relation
        else:
            return super(MessageRelation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-create_time']
        unique_together = ('msg_thread', 'lost', 'found')


class PetSpecies(CommonMixin):
    pet_type = models.IntegerField(choices=PET_TYPE, default=0)
    name = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    count = models.IntegerField(default=0)
    pinyin = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    img = models.ImageField(upload_to='species', blank=True, null=True)

    def __str__(self):
        return '%d:%s' % (self.id, self.name)


class PetLostFoundMatch(CommonMixin):
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match_set')
    contact_status = models.IntegerField(choices=CONTACT_STATUS, blank=False, null=False, default=0)
    static_score = models.IntegerField(default=None)
    feedback_score = models.IntegerField(default=None)

    objects = FlaggedModelManager()
    def __str___(self):
        return '%d:%d-%d' % (self.id, self.lost.id, self.found.id)


class PetCaseClose(CommonMixin):
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='case_close_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='case_close_set')
    descrption = models.TextField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reward_charge_status = models.IntegerField(choices=CHARGE_STATUS, default=0)
    reward_charge_amount = models.IntegerField(default=0, help_text='单位分')


class PetMaterial(CommonMixin):
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='published_material_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='material_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='material_set')
    close = models.ForeignKey('PetCaseClose', on_delete=models.SET_NULL, blank=True, null=True, related_name='material_set')
    mat_type = models.IntegerField(choices=MATERIAL_TYPE, blank=True, null=True)
    mime_type = models.CharField(max_length=20, blank=True, null=True)
    size = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    thumb_url = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    full_path = models.CharField(max_length=LONG_CHAR, blank=True, null=True)


class PetLostInteractHourly(CommonMixin):
    date_id = models.IntegerField(default=None)
    hour_id = models.IntegerField(default=None)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    pv = models.IntegerField(default=0)
    uv = models.IntegerField(default=0)
    valid_uv = models.IntegerField(default=0)
    boost_uv = models.IntegerField(default=0)
    boost_amount = models.IntegerField(default=0, help_text='单位分')


class PetFoundInteractHourly(CommonMixin):
    date_id = models.IntegerField(default=None)
    hour_id = models.IntegerField(default=None)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    pv = models.IntegerField(default=0)
    uv = models.IntegerField(default=0)


class FollowLog(CommonMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    updated = models.CharField(max_length=SHORT_CHAR, choices=FLAG_CHOICE)
    obj_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.lost is not None:
            self.obj_time = self.lost.create_time
        if self.found is not None:
            self.obj_time = self.found.create_time
        super(FollowLog, self).save()

    class Meta:
        ordering = ['-obj_time', '-create_time']


class LikeLog(CommonMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')

    class Meta:
        ordering = ['-create_time']

class BoostLog(CommonMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    count = models.IntegerField(default=1)

    class Meta:
        ordering = ['-create_time']


class RepostLog(CommonMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')

    class Meta:
        ordering = ['-create_time']


def banner_expire():
    return timezone.now() + timezone.timedelta(weeks=10*52)

class Banner(CommonMixin):
    name = models.CharField(max_length=MID_CHAR)
    img = models.ImageField(upload_to='banner')
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(default=banner_expire)
    banner_type = models.IntegerField(default=0, choices=BANNER_TYPE)
    audit_status = models.IntegerField(default=0, choices=AUDIT_STATUS)

    click_url = models.URLField(null=True, blank=True)
    show_times = models.IntegerField(default=0)
    click_times = models.IntegerField(default=0)

    def __str__(self):
        return self.name


