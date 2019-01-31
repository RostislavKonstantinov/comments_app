from django.conf.urls import url

from content_entities.views import BlogViewSet, TopicViewSet

urlpatterns = [
    url(r'^/blogs$', BlogViewSet.as_view({'get': 'list'})),
    url(r'^/blogs/(?P<pk>\d+)$', BlogViewSet.as_view({'get': 'retrieve'})),
    url(r'^/topics', TopicViewSet.as_view({'get': 'list'})),
    url(r'^/topics/(?P<pk>\d+)$', TopicViewSet.as_view({'get': 'retrieve'})),
]