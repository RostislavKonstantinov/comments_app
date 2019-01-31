from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers

from comments.models import CommentsReport, CONTENT_TYPE_CHOICES
from comments.tasks import generate_comments_report


class CommentsReportSerializer(serializers.ModelSerializer):
    """
    Serialize parameters for comments report generation
    and present report model.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        source='user_id')
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.filter(CONTENT_TYPE_CHOICES),
        required=False, allow_null=True,
        source='content_type_id')
    object_id = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    created_at__gte = serializers.DateTimeField(required=False, allow_null=True)
    created_at__lt = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = CommentsReport
        fields = ('id', 'created_by', 'status', 'created_at', 'updated_at', 'user', 'content_type',
                  'object_id', 'created_at__gte', 'created_at__lt')

        extra_kwargs = {
            'created_by': {'read_only': True},
            'status': {'read_only': True},
        }

    def validate(self, data):
        data = super().validate(data)
        content_type = data.get('content_type_id')
        object_id = data.get('object_id')
        if object_id and content_type is None:
            raise serializers.ValidationError({'content_type': ['This field is required.']})
        if content_type and not content_type.model_class().objects.filter(id=object_id).exists():
            raise serializers.ValidationError({'object_id': ['Object does not exists.']})
        return data

    def create(self, validated_data):
        instance = super().create(validated_data)
        # async report generation
        transaction.on_commit(
            lambda: generate_comments_report.apply_async(kwargs=dict(report_id=instance.id))
        )
        return instance
