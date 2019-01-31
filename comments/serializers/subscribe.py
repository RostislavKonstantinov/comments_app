from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.models import CONTENT_TYPE_CHOICES, Subscribe


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Serialize parameters for subscribe to commentaries.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.filter(CONTENT_TYPE_CHOICES),
        required=True)
    object_id = serializers.IntegerField(min_value=0, required=True)

    class Meta:
        model = Subscribe
        fields = ('id', 'user', 'content_type', 'object_id')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'content_type', 'object_id'),
                message=_("User already subscribed")
            )
        ]

    def validate(self, data):
        data = super().validate(data)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        if not content_type.model_class().objects.filter(id=object_id).exists():
            raise serializers.ValidationError({'object_id': ['Object does not exists.']})
        return data
