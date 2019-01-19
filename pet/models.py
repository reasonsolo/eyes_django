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
BOOST_KPI_TYPE = (
    (1, 'NoKpi'),
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
    pass

class PetClass(models.Model):
    pass

class PetCase(models.Model):
    pass

class PetCaseClose(models.Model):
    pass

class PetMaterial(models.Model):
    pass

class PetLostInteractHourly(models.Model):
    pass

class PetFoundInteractHourly(models.Model):
    pass
