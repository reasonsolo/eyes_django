from django.contrib import admin
from pet.models import *

# Register your models here.

class EyesAdminSite(admin.AdminSite):
    site_header = 'EyesAdministration'

@admin.register(PetLost, PetFound, ContactRelation, PrivateContact,
 Comment, Message, LostFoundTag, PetLostBoost, PetSpecies,
 PetCaseClose, PetMaterial)
class PetAdmin(admin.ModelAdmin):
    pass