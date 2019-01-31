from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from comments.models import Comment, CONTENT_TYPE_CHOICES
from comments.mixins import NotEditableFieldsMixin


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class CommentSerializer(NotEditableFieldsMixin, serializers.ModelSerializer):
    """
    Serializer for present and save Comment model.
    """
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.filter(CONTENT_TYPE_CHOICES),
                                                      required=True)
    self_content_type = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content_type', 'object_id', 'text', 'parent', 'user',
                  'created_at', 'updated_at', 'self_content_type')
        not_editable_fields = ('content_type', 'object_id')
        extra_kwargs = {
            'parent': {'read_only': True},
            'object_id': {'required': True},
        }

    def validate(self, data):
        data = super().validate(data)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        if content_type and not content_type.model_class().objects.filter(id=object_id).exists():
            raise serializers.ValidationError({'object_id': ['Object does not exists']})
        if content_type and content_type.model_class() is self.Meta.model:
            data['parent_id'] = object_id
        return data
