from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from comments.models import Comment, DELETED, CREATED, UPDATED
from comments.serializers.comment import CommentSerializer
from comments.sql import SUBSCRIBERS_SQL


def send_push(user_id, operation, data):
    """ Send push notifications. """
    channel_layer = get_channel_layer()
    # Trigger reload message sent to group
    group_name = f'user_{user_id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'push_message',
            'message': {
                'operation': operation,
                'data': data
            }
        }
    )


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def comment_instance_modified(sender, instance, created=None, **kwargs):
    """ Actons after comment created, updated or deleted """
    operation = CREATED
    data = CommentSerializer(instance).data
    # comment deleted
    if created is None:
        operation = DELETED
        for user_id in instance.subscribed_users:
            send_push(user_id, operation, data)
        return

    # comment updated
    if created is False:
        operation = UPDATED

    with connection.cursor() as cursor:
        cursor.execute(SUBSCRIBERS_SQL, dict(id=instance.id))
        for row, in cursor:
            send_push(row['user_id'], operation, data)
