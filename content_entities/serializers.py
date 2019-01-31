from rest_framework import serializers

from content_entities.models import Blog, Topic


class BlogSerializer(serializers.ModelSerializer):
    self_content_type = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'title', 'created_at', 'self_content_type')
        model = Blog


class TopicSerializer(serializers.ModelSerializer):
    self_content_type = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'title', 'created_at', 'self_content_type')
        model = Topic
