from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from content_entities.models import Blog
from content_entities.serializers import BlogSerializer, TopicSerializer


class BlogViewSet(ReadOnlyModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = (AllowAny,)


class TopicViewSet(ReadOnlyModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (AllowAny,)
