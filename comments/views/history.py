from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from comments.models import CommentActivityLog
from comments.serializers.history import CommentHistorySerializer


class CommentHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    This endpoint used to show history of commentaries.
    """
    serializer_class = CommentHistorySerializer
    queryset = CommentActivityLog.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(**self.kwargs).select_related('user')
