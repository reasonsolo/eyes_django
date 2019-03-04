from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe
from pet.models import *

# Register your models here.

class EyesAdminSite(admin.AdminSite):
    site_header = 'EyesAdministration'
    def save_model(self, request, obj, form, change):
        obj.last_update_by = request.user
        obj.last_update_time = timezone.now()
        if not change:
            obj.create_by = request.user
        super(EyesAdminSite, self).save_model(self, request, obj, form, change)


def mark_as_passed(modeladmin, request, queryset):
    queryset.update(audit_status=1)

def mark_as_denied(modeladmin, request, queryset):
    queryset.update(audit_status=2)

mark_as_passed.short_description = u'标记选中为审核通过'
mark_as_denied.short_description = u'标记选中为审核不通过'

@admin.register(Tag, PetSpecies, PetCaseClose, PetMaterial, LikeLog, RepostLog)
class PetAdmin(admin.ModelAdmin):
    pass

class AuditAdmin(admin.ModelAdmin):
    actions = [mark_as_passed, mark_as_denied]

@admin.register(Comment)
class CommentAdmin(AuditAdmin):
    list_display = ('create_time', 'publisher', 'content', 'get_audit_status_display')
    list_filter = ('create_time', 'audit_status')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'sender', 'receiver', 'content', 'get_msg_type_display', 'get_read_status_display')
    list_filter = ('create_time', 'msg_type', 'read_status')

@admin.register(Banner)
class BannerAdmin(AuditAdmin):
    list_display = ('name', 'show_image', 'get_audit_status_display', 'get_banner_type_display',
                 'start_time', 'end_time', 'show_times', 'click_times')
    def show_image(self, instance):
        return mark_safe('<div style="width: 200px"><img src=%s style="width:200px"/></div>' % instance.img.url)

@admin.register(PetFound, PetLost)
class LostFoundAdmin(AuditAdmin):
    list_display = ('create_time', 'pet_type', 'species', 'place',
                    'brief_content','get_thumb_nails',
                    'audit_status', 'case_status', 'publisher', 'last_update_time')
    list_filter = ('create_time', 'audit_status', 'case_status', 'pet_type')
    ordering = ('-id',)
    readonly_fields = ['show_materials']
    filter_horizontal = ('tags',)

    def get_thumb_nails(self, instance):
        materials = instance.material_set.all()
        html = ''
        for material in materials:
            html += "<img src='%s' height=100px width=100px/>" % material.thumb_url
        return mark_safe(html)
    get_thumb_nails.allow_tags = True

    def brief_content(self, instance):
        return mark_safe('<div style="width: 200px; white-space:pre-wrap;  word-wrap: break-word; overflow: hidden; text-overflow: ellipsis;">%s</div>' % instance.description)
    brief_content.allow_tags=True

