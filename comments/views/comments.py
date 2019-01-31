from django.db import connection
from django.forms import NullBooleanField
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from comments.activity_log import CommentActivityLogMixin
from comments.filters import CommentsFilter
from comments.mixins import GetUserMixin
from comments.models import Comment
from comments.serializers.comment import CommentSerializer
from comments.sql import CHILDREN_SQL

CHILDREN_FILTER_KEY = 'children'
CONTENT_TYPE_FILTER_KEY = 'content_type'
OBJECT_ID_FILTER_KEY = 'object_id'
PARENT_FILTER_KEY = 'parent'


def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class CommentsViewSet(GetUserMixin, CommentActivityLogMixin, ModelViewSet):
    """
    This endpoint used to show, create and modify commentaries.
    It's provide filters for all comments presentation: single, paginated first
    level comments list-view by object (content_type + object_id) or parent instance
    and child list-view by parent or object.
    """

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_class = CommentsFilter

    def get_queryset(self):
        return super().get_queryset().select_related('user')

    @staticmethod
    def get_parent_object_kwargs(request):
        """ Format parameters for sql and choosing root by filters. """
        parent = parse_int(request.query_params.get(PARENT_FILTER_KEY))
        if parent:
            return dict(id=parent)

        content_type = parse_int(request.query_params.get(CONTENT_TYPE_FILTER_KEY))
        object_id = parse_int(request.query_params.get(OBJECT_ID_FILTER_KEY))
        if content_type and content_type == Comment.get_content_type().id and object_id:
            return dict(id=object_id)
        raise Comment.DoesNotExist()

    def list(self, request, *args, **kwargs):
        # Without filters return empty list response
        if not request.query_params:
            return Response([])
        # Condition for child list-view
        if NullBooleanField().to_python(request.query_params.get(CHILDREN_FILTER_KEY)):
            result = []
            try:
                # SQL optimization for increase render performance
                with connection.cursor() as cursor:
                    cursor.execute(CHILDREN_SQL, self.get_parent_object_kwargs(request))
                    for row, in cursor:
                        result.append(row)
            except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
                result = []

            return Response(result)
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.get_descendant_count():
            raise ValidationError({"detail": "Comment can't be deleted because it has child comments"})
        super().perform_destroy(instance)
