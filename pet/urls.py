from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .apis import PetLostViewSet, MaterialUploadView

lost_list = PetLostViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

lost_detail = PetLostViewSet.as_view({
    'get': 'retrieve',
    'post': 'update',
})

urlpatterns = format_suffix_patterns([
    # url(r'^$', api_root),
    url(r'^losts/$', lost_list, name='lost-list'),
    url(r'^lost/(?P<pk>[0-9]+)/$', lost_detail, name='lost-detail'),
    url(r'^material/$', MaterialUploadView.as_view(), name='material-upload'),
])
