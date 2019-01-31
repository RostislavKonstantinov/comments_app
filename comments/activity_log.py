from comments.models import CommentActivityLog, CREATED, DELETED, UPDATED
from comments.serializers.comment import CommentSerializer


class CommentActivityLogMixin:
    """
    Keeps history of comment actions
    """

    def perform_create(self, serializer):
        serializer.save(user=self.get_user())
        CommentActivityLog.objects.create(
            comment_id=serializer.instance.id,
            state_after=serializer.data,
            operation=CREATED,
            user=self.get_user()
        )

    def perform_destroy(self, instance):
        state_before = CommentSerializer(instance).data
        comment_id = instance.id
        instance.delete()
        CommentActivityLog.objects.create(
            comment_id=comment_id,
            state_before=state_before,
            operation=DELETED,
            user=self.get_user()
        )

    def perform_update(self, serializer):
        state_before = CommentSerializer(serializer.instance).data
        text_before = serializer.instance.text
        serializer.save()
        state_after = serializer.data
        if text_before != serializer.instance.text:
            CommentActivityLog.objects.create(
                comment_id=serializer.instance.id,
                state_before=state_before,
                state_after=state_after,
                operation=UPDATED,
                user=self.get_user()
            )
