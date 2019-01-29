# encoding: utf-8
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from separatedvaluesfield.models import SeparatedValuesField
from datetime import datetime
from wx_auth.models import UserProfile
from datetime import datetime

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
    (0, 'Pending'),
    (1, 'Passed'),
    (2, 'Denied'),
)
CHARGE_STATUS = (
    (0, 'NotPaid'),
    (1, 'Failed'),
    (2, 'Succeeded'),
    (3, 'Free'),
)
CONTACT_TYPE = (
    (0, 'LostFound'),
    (1, 'Clue'),
)
CONTACT_STATUS = (
    (0, 'NotContact'),
    (1, 'Contacted'),
)
BOOST_KPI_TYPE = (
    (0, 'NoKpi'),
    (1, 'ViewAmount'),
)
MEDICAL_STATUS = (
	(0, 'None'),
	(1, 'Sterilized'),
	(2, 'Vaccinated'),
	(3, 'Desinsect'),
)
PET_TYPE = (
    (0, 'Other'),
    (1, 'Cat'),
    (2, 'Dog'),
)
FOUND_STATUS = (
    (0, 'NotAtHand'),
    (1, 'AtHand'),
    (2, 'InHospital'),
)
MATERIAL_TYPE = (
    (0, 'Video'),
    (1, 'Image'),
)
MESSAGE_TYPE = (
    (0, 'System'),
    (1, 'Personal'),
)
READ_STATUS = (
    (0, 'NotRead'),
    (1, 'Read'),
)

# filter out flag=0 by default
class FlaggedModelManager(models.Manager):
    def get_queryset(self):
        return super(FlaggedModelManager, self).get_queryset().filter(flag=1)


class PetLost(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    publisher = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='published_lost_set')
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True)
    pet_type = models.IntegerField(choices=PET_TYPE, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, default=1)
    color = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    case_status = models.IntegerField(choices=CASE_STATUS, default=0)
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)
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
    medical_status = SeparatedValuesField(max_length=MID_CHAR,choices=MEDICAL_STATUS,\
                                          blank=True, null=True)
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_pet_lost_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_pet_lost_set')
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return '%d:%s@%s-%s' % (self.id, self.publisher.nickname if self.publisher is not None else 'None',
                                self.place, self.get_case_status_display())


class PetFound(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    publisher = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='published_found_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True)
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True)
    pet_type = models.IntegerField(choices=PET_TYPE, default=1)
    color = models.CharField(max_length=SHORT_CHAR, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    found_status = models.IntegerField(choices=FOUND_STATUS, default=0)
    case_status = models.IntegerField(choices=CASE_STATUS, default=0)
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)
    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    follow_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    tags = models.ManyToManyField('Tag', blank=True)

    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_pet_found_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_pet_found_set')
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return '%d:%s@%s-%s' % (self.id, self.publisher.nickname if self.publisher is not None else 'None',
                                self.place, self.get_case_status_display())


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    name = models.CharField(max_length=MID_CHAR, unique=True, db_index=True)
    count = models.IntegerField(default=0)
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_lost_found_tag_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()

    class Meta:
        ordering = ['count']


    def __str__(self):
        return self.name

class TagUsage(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, blank=True, null=True, related_name='tag_usage_set')
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='tag_usage_set')
    count = models.IntegerField(default=0)
    last_usage = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    class Meta:
        ordering = ['-count', '-last_usage']

    def save(self, *args, **kwargs):
        self.last_usage = datetime.now()
        self.count += 1
        self.tag.count += 1
        self.tag.save()
        return super(TagUsage, self).save(*args, **kwargs)


class Comment(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    publisher = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='published_comment_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, null=True, blank=True, related_name='comment_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, null=True, blank=True, related_name='comment_set')
    content = models.TextField()
    audit_status = models.IntegerField(choices=AUDIT_STATUS, default=0)
    reply_to = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, blank=True, related_name='reply_set')
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_comment_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_comment_set')
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    class Meta:
        ordering = ['create_time']

    def __str__(self):
        return '%d:%s@%s' % (self.id,
                             self.publisher.nickname if self.publisher is not None else 'anonymous',
                             str(self.create_time))


class Message(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    receiver = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='received_message_set')
    sender = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='sent_message_set')
    content = models.TextField(default='')
    message_type = models.CharField(max_length=SHORT_CHAR, choices=MESSAGE_TYPE, default=0)
    read_status = models.CharField(max_length=SHORT_CHAR, choices=READ_STATUS, default=0)
    msg_thread = models.ForeignKey('MessageThread', on_delete=models.SET_NULL, null=True, blank=True, related_name='message_set')

    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_message_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    class Meta:
        ordering = ['create_time']

    def __str__(self):
        return '%d:%s->%s@%s' (self.id, self.sender.nickname, self.receiver.nickname, str(self.create_time))


class MessageThread(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    message_type = models.CharField(max_length=SHORT_CHAR, choices=MESSAGE_TYPE, default=0)
    user_a = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='message_as_a_set')
    user_b = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='message_as_b_set')
    last_msg = models.ForeignKey('Message', on_delete=models.SET_NULL, null=True, blank=True)
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    def save(self, *args, **kwargs):
        thread = MessageThread.objects.filter((Q(user_a=self.user_a)&Q(user_b=self.user_b))\
                                              |(Q(user_a=self.user_b)&Q(user_b=self.user_a))).first()
        if thread is None:
            return super(MessageThread, self).save(*args, **kwargs)
        else:
            return thread

    def __str__(self):
        return '%d:%s-%s@%s' % (self.id, self.user_a.nickname, self.user_b.nickname, self.create_time)

    class Meta:
        unique_together = ('user_a', 'user_b')


class MessageRelation(models.Model):
    msg_thread = models.ForeignKey(MessageThread, on_delete=models.SET_NULL, null=True)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, null=True, related_name='msg_relation_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, null=True, related_name='msg_relation_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    def save(self,  *args, **kwargs):
        relation = MessageRelation.objects.filter(msg_thread=self.msg_thread, lost=self.lost, found=self.found).first()
        if relation is not None:
            return relation
        else:
            return super(MessageRelation, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-create_time']
        unique_together = ('msg_thread', 'lost', 'found')


class PetSpecies(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    pet_type = models.IntegerField(choices=PET_TYPE, default=0)
    name = models.CharField(max_length=MID_CHAR, blank=True, null=True)

    objects = FlaggedModelManager()
    def __str__(self):
        return '%d:%s' % (self.id, self.name)


class PetLostFoundMatch(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match_set')
    contact_status = models.IntegerField(choices=CONTACT_TYPE, blank=False, null=False)
    static_score = models.IntegerField(default=None)
    feedback_score = models.IntegerField(default=None)
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_match_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_match_set')
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    def __str___(self):
        return '%d:%d-%d' % (self.id, self.lost.id, self.found.id)


class PetCaseClose(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_case_close_set')
    best_found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_case_close_set')
    descrption = models.TextField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reward_charge_status = models.IntegerField(choices=CHARGE_STATUS, default=0)
    reward_charge_amount = models.IntegerField(default=0, help_text='单位分')
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_case_close_set')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey(UserProfile,on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_case_close_set')
    last_update_time = models.DateTimeField(default=now)


class PetMaterial(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='material_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='material_set')
    mat_type = models.IntegerField(choices=MATERIAL_TYPE, blank=True, null=True)
    mime_type = models.CharField(max_length=20, blank=True, null=True)
    size = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    thumb_url = models.URLField(max_length=LONG_CHAR, blank=True, null=True)
    full_path = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    create_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_material_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()

class PetLostInteractHourly(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    date_id = models.IntegerField(default=None)
    hour_id = models.IntegerField(default=None)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    pv = models.IntegerField(default=0)
    uv = models.IntegerField(default=0)
    valid_uv = models.IntegerField(default=0)
    boost_uv = models.IntegerField(default=0)
    boost_amount = models.IntegerField(default=0, help_text='单位分')
    create_time = models.DateTimeField(default=now)
    last_update_time = models.DateTimeField(default=now)


class PetFoundInteractHourly(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    date_id = models.IntegerField(default=None)
    hour_id = models.IntegerField(default=None)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    pv = models.IntegerField(default=0)
    uv = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=now)
    last_update_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()


class FollowLog(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='follow_set')
    updated = models.CharField(max_length=SHORT_CHAR, choices=FLAG_CHOICE)
    create_time = models.DateTimeField(default=now)
    obj_time = models.DateTimeField(blank=True, null=True)

    objects = FlaggedModelManager()

    def save(self, *args, **kwargs):
        if self.lost is not None:
            self.obj_time = self.lost.create_time
        if self.found is not None:
            self.obj_time = self.found.create_time
        super(FollowLog, self).save()

    class Meta:
        ordering = ['-obj_time', '-create_time']


class LikeLog(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='like_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()
    class Meta:
        ordering = ['-create_time']

class BoostLog(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='boost_set')
    count = models.IntegerField(default=1)
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()

    class Meta:
        ordering = ['-create_time']


class RepostLog(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=True, null=True, related_name='repost_set')
    create_time = models.DateTimeField(default=now)

    objects = FlaggedModelManager()

    class Meta:
        ordering = ['-create_time']


