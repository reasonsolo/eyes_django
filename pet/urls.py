from django.conf.urls import url
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from .apis import *

lost_list = PetLostViewSet.as_view({
    'get': 'list',
    'create': 'create'
})

lost_detail = PetLostViewSet.as_view({
    'get': 'retrieve',
    'create': 'create',
    'update': 'update',
    'destroy': 'destroy',
})

lost_match = PetLostViewSet.as_view({
    'get': 'match_found',
	'post': 'create_found',
})

found_list = PetFoundViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

found_detail = PetFoundViewSet.as_view({
    'get': 'retrieve',
    'create': 'update',
    'update': 'update',
    'destroy': 'destroy',
})

found_match = PetFoundViewSet.as_view({
    'get': 'match_lost',
	'post': 'create_lost',
})

follow_feeds = FollowFeedsView.as_view({
    'get': 'list',
})

message_list = MessageViewSet.as_view({
	'get': 'list'
})

msg_thread_list = MessageThreadViewSet.as_view({
	'get': 'list',
	'post': 'create',
})
message_list = MessageViewSet.as_view({
	'get': 'list',
	'post': 'create',
	'destroy': 'destroy',
})
comment_list = CommentViewSet.as_view({
	'get': 'list',
	'post': 'create',
})
material_detail = MaterialViewSet.as_view({
	'get': 'retrieve',
	'delete': 'destroy',
})


#router = DefaultRouter()
#router.register(r'lost', PetLostViewSet)
#router.register(r'species', SpeciesListView)

urlpatterns = format_suffix_patterns([
    # url(r'^$', api_root),
    # path('', include(router.urls)),
    url(r'^losts/$', lost_list, name='lost-list'),
    url(r'^lost/(?P<pk>[0-9]+)/$', lost_detail, name='lost-detail'),
    url(r'^lost/match/(?P<pk>[0-9]+)/$', lost_match, name='lost-match'),

    url(r'^material/upload$', MaterialUploadView.as_view(), name='material-upload'),
	url(r'^material/(?P<pk>[0-9]+)/$', material_detail, name='material-detail'),

    url(r'^species/$', SpeciesListView.as_view({'get': 'list'}), name='species-list'),

    url(r'^founds/$', found_list, name='found-list'),
    url(r'^found/(?P<pk>[0-9]+)/$', found_detail, name='found-detail'),
    url(r'^found/match/(?P<pk>[0-9]+)/$', found_match, name='found-match'),

    url(r'^action/(?P<action>like|repost|follow)/(?P<obj>lost|found)/(?P<pk>[0-9]+)/$', ActionLogAPIView.as_view()),

    url(r'^user/follow/$', follow_feeds, name='follow-feeds'),
    url(r'^user/(?P<obj>lost|found)/$', MyPostView.as_view(), name='follow-feeds'),

	url(r'^msg/threads/$', msg_thread_list, name='msg-thread-list'),
	url(r'^msg/thread/(?P<thread_pk>[0-9]+)$', message_list, name='msg-list'),

	url(r'^comment/(?P<obj>lost|found)/(?P<obj_pk>[0-9]+)/$', comment_list, name='comment-list'),

	# url(r'^tag/$', tag_list, name='tag-list'),
])
