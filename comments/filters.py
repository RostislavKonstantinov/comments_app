from django_filters import rest_framework as filters

from comments.models import Comment, Subscribe


class CommentsFilter(filters.FilterSet):
    """
    Commentaries endpoint's filters
    """
    created_at__gte = filters.IsoDateTimeFilter(name='created_at', lookup_expr="gte")
    created_at__lt = filters.IsoDateTimeFilter(name='created_at', lookup_expr="lt")

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at')
        )
    )

    class Meta:
        model = Comment
        fields = ('user', 'content_type', 'object_id', 'parent')


class SubscribesFilter(filters.FilterSet):
    """
    Subscribes list filters
    """
    class Meta:
        model = Subscribe
        fields = ('user', 'content_type', 'object_id')
