from rest_framework import serializers

from comments.models import CommentActivityLog
from comments.serializers.comment import UserSerializer


class CommentHistorySerializer(serializers.ModelSerializer):
    """
    Present comments history.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommentActivityLog
        fields = ('id', 'comment_id', 'operation', 'state_before', 'state_after', 'created_at', 'user')
