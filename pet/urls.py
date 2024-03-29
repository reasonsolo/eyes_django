from django.conf.urls import url
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from .apis import *

lost_list = PetLostViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

lost_detail = PetLostViewSet.as_view({
    'get': 'retrieve',
    'post': 'update',
    'delete': 'destroy',
})
lost_match = PetLostViewSet.as_view({
    'get': 'match_found',
	'post': 'create_found',
})
lost_status = PetLostViewSet.as_view({
    'get': 'update_case_status',
})
lost_love_help = PetLostViewSet.as_view({
	'get': 'get_love_help',
})

found_list = PetFoundViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
found_detail = PetFoundViewSet.as_view({
    'get': 'retrieve',
    'post': 'update',
    'delete': 'destroy',
})
found_match = PetFoundViewSet.as_view({
    'get': 'match_lost',
	'post': 'create_lost',
})
found_status = PetFoundViewSet.as_view({
    'get': 'update_case_status',
})
found_love_help = PetFoundViewSet.as_view({
	'get': 'get_love_help',
})

like_feeds = LikeFeedsView.as_view({
    'get': 'list',
})

msg_thread_list = MessageThreadViewSet.as_view({
	'get': 'list',
})

msg_thread_view = MessageThreadViewSet.as_view({
	'get': 'retrieve',
	'post': 'create_msg',
})

comment_list = CommentViewSet.as_view({
	'get': 'list',
	'post': 'create',
})
material_detail = MaterialViewSet.as_view({
	'get': 'retrieve',
	'delete': 'destroy',
})
case_close_obj = PetCaseCloseViewSet.as_view({
	'get': 'retrieve_by_obj',
	'post': 'create_for_obj',
})
case_close_detail = PetCaseCloseViewSet.as_view({
	'get': 'retrieve',
})
banner_list = BannerViewSet.as_view({'get': 'list'})
banner_click = BannerViewSet.as_view({'get': 'click'})

#router = DefaultRouter()
#router.register(r'lost', PetLostViewSet)
#router.register(r'species', SpeciesListView)

urlpatterns = format_suffix_patterns([
    # url(r'^$', api_root),
    # path('', include(router.urls)),
    url(r'^losts$', lost_list, name='lost-list'),
    url(r'^lost/(?P<pk>[0-9]+)$', lost_detail, name='lost-detail'),
    url(r'^lost/match/(?P<pk>[0-9]+)$', lost_match, name='lost-match'),
    url(r'^lost/status/(?P<pk>[0-9]+)$', lost_status, name='lost-status'),
    url(r'^lost/love_help/(?P<pk>[0-9]+)$', lost_love_help, name='lost-love-help'),

    url(r'^material/upload$', MaterialUploadView.as_view(), name='material-upload'),
	url(r'^material/(?P<pk>[0-9]+)$', material_detail, name='material-detail'),

    url(r'^species$', SpeciesListView.as_view({'get': 'list'}), name='species-list'),

    url(r'^founds$', found_list, name='found-list'),
    url(r'^found/(?P<pk>[0-9]+)$', found_detail, name='found-detail'),
    url(r'^found/match/(?P<pk>[0-9]+)$', found_match, name='found-match'),
    url(r'^found/status/(?P<pk>[0-9]+)$', found_status, name='found-status'),
    url(r'^found/love_help/(?P<pk>[0-9]+)$', found_love_help, name='found-love-help'),

	url(r'^close/(?P<obj>lost|found)/(?P<pk>[0-9]+)/', case_close_obj, name='case-close-obj'),
	url(r'^close/(?P<pk>[0-9]+)/', case_close_detail, name='case-close-detail'),

    url(r'^action/(?P<action>like|repost|follow|lovehelp|loveconcern)/(?P<obj>lost|found)/(?P<pk>[0-9]+)$', ActionLogAPIView.as_view()),

    url(r'^user/like$', like_feeds, name='like-feeds'),
    url(r'^user/(?P<obj>lost|found)$', MyPostView.as_view(), name='my-feeds'),

	url(r'^msg/threads$', msg_thread_list, name='msg-thread-list'),
	# url(r'^msg/thread/(?P<obj>lost|found)/(?P<obj_pk>[0-9]+)$', msg_thread_relate, name='msg-thread-relate'),
	url(r'^msg/thread/(?P<pk>[0-9]+)$', msg_thread_view, name='msg-thread-view'),
	url(r'^msg/thread$', msg_thread_view, name='msg-thread-view'),

	url(r'^comment/(?P<obj>lost|found)/(?P<obj_pk>[0-9]+)$', comment_list, name='comment-list'),

	url(r'^tag$', TagView.as_view(), name='tag-list'),

	url(r'^banners$', banner_list, name='banner-list'),
	url(r'^banner/(?P<pk>[0-9]+)$', banner_click, name='banner-click'),
])
