from django.db import models
from django.utils.timezone import now
from separatedvaluesfield.models import SeparatedValuesField
from datetime import datetime

SHORT_CHAR=5
MID_CHAR=20
LONG_CHAR=200

FLAG_CHOICE = (
    (1, 'Yes'),
    (2, 'No'),
)
GENDER_CHOICE = (
    (0, 'Unknown'),
    (1, 'Male'),
    (2, 'Female'),
)
CASE_STATUS = (
    (0, 'Valid'),
    (1, 'Closed'),
    (2, 'Expired'),
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
	(1, 'Sterilized'),
	(2, 'Vaccinated'),
	(3, 'Desinsect'),
)
PET_TYPE = (
    (1, 'Cat'),
    (2, 'Dog'),
    (3, 'Other'),
)
MATERIAL_TYPE = (
    (0, 'Video'),
    (1, 'Image'),
)

class UserAuth(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    pass

class User(models.Model):
    pass

class PetLost(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    publiser = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True, related_name='published_pet_losts')
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.IntegerField(choices=PET_TYPE, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICE, default=1)
    color = models.CharField(max_length=MID_CHAR, blank=True, null=True)
    descrption = models.TextField(blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    place = models.CharField(max_length=LONG_CHAR, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=4)
    latitude = models.DecimalField(max_digits=10, decimal_places=4)
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
    like_count = models.IntegerField(default=0)
    medical_status = SeparatedValuesField(max_length=MID_CHAR,choices=MEDICAL_STATUS,\
                                          blank=True, null=True)
    create_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='created_pet_losts')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey('User',on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='updated_pet_losts')
    last_update_time = models.DateTimeField(default=now)

class PetFound(models.Model):
    pass

class ContactRelation(models.Model):
    pass

class PrivateContact(models.Model):
    pass

class PetLostFoundTag(models.Model):
    pass

class PetListFoundComment(models.Model):
    pass

class PetLostBoost(models.Model):
    pass

class PetTag(models.Model):
    pass

class PetSpecies(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    name = models.CharField(max_length=20, blank=False, null=False)

class PetClass(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    species = models.ForeignKey('PetSpecies', on_delete=models.SET_NULL, blank=True, null=True, related_name='class_species')
    name = models.CharField(max_length=20, blank=False, null=False)

class PetLostFoundMatch(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match')
    found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_found_match')
    contact_status = models.IntegerField(choices=CONTACT_TYPE, blank=False, null=False)
    static_score = models.IntegerField(default=None)
    feedback_score = models.IntegerField(default=None)
    create_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='lost_found_match_create')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey('User',on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='lost_found_match_update')
    last_update_time = models.DateTimeField(default=now)

class PetCaseClose(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    lost = models.ForeignKey('PetLost', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_case_close')
    best_found = models.ForeignKey('PetFound', on_delete=models.SET_NULL, blank=False, null=True, related_name='lost_case_close')
    descrption = models.TextField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    repost_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reward_charge_status = models.IntegerField(choices=CHARGE_STATUS, default=0)
    reward_charge_amount = models.IntegerField(default=0, help_text='单位分')
    create_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='case_close_create')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey('User',on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='case_close_update')
    last_update_time = models.DateTimeField(default=now)

class PetMaterial(models.Model):
    flag = models.IntegerField(choices=FLAG_CHOICE, default=1)
    type = models.IntegerField(choices=MATERIAL_TYPE, blank=True, null=True)
    mime_type = models.CharField(max_length=20, blank=True, null=True)
    size = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    create_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,\
                                  related_name='material_create')
    create_time = models.DateTimeField(default=now)
    last_update_by = models.ForeignKey('User',on_delete=models.SET_NULL, blank=True, null=True,\
                                       related_name='material_update')
    last_update_time = models.DateTimeField(default=now)

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