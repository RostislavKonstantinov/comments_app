from django.conf.urls import url

from pushes import consumers

websocket_urlpatterns = [
    url(r'^ws/push/(?P<user_id>\d+)/$', consumers.PushConsumer),
]
