from rest_framework import serializers

from .models import ContentItem, FlagRecord


class FlagRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlagRecord
        fields = ['id', 'content_item', 'status', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class ContentItemSerializer(serializers.ModelSerializer):
    flags = FlagRecordSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = ['id', 'title', 'body', 'source', 'created_at', 'flags']
        read_only_fields = ['id', 'created_at', 'flags']
