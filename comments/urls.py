from django.conf.urls import url

from comments.views.comments import CommentsViewSet
from comments.views.comments_reports import CommentsReportsViewSet, CommentsReportsResultViewSet
from comments.views.history import CommentHistoryViewSet
from comments.views.subscribes import SubscribesViewSet

urlpatterns = [
    url(r'^$', CommentsViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/(?P<pk>\d+)$', CommentsViewSet.as_view({'get': 'retrieve',
                                                    'put': 'update',
                                                    'delete': 'destroy',
                                                    'patch': 'partial_update'})),
    url(r'^/reports$', CommentsReportsViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/reports/(?P<pk>\d+)$', CommentsReportsViewSet.as_view({'get': 'retrieve'})),
    url(r'^/reports/(?P<pk>\d+)/(?P<format_name>\w+)$', CommentsReportsResultViewSet.as_view({'get': 'retrieve'})),
    url(r'^/history/(?P<comment_id>\d+)$', CommentHistoryViewSet.as_view({'get': 'list'})),
    url(r'^/subscribe$', SubscribesViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/subscribe$/(?P<pk>\d+)$', CommentsViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]
