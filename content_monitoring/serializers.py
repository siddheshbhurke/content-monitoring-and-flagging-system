from rest_framework import serializers

from .models import ContentItem, Flag, Keyword


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['id', 'name']
        read_only_fields = ['id']


class ScanRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    body = serializers.CharField()
    source = serializers.CharField(max_length=255)


class FlagSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(read_only=True)
    content_item = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Flag
        fields = ['id', 'keyword', 'content_item', 'score', 'status', 'last_reviewed_at']
        read_only_fields = ['id', 'keyword', 'content_item', 'score', 'status', 'last_reviewed_at']


class FlagUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ['status']


class ContentItemSerializer(serializers.ModelSerializer):
    flags = FlagSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = ['id', 'title', 'body', 'source', 'last_updated', 'flags']
        read_only_fields = ['id', 'last_updated', 'flags']


class ScanResultSerializer(serializers.ModelSerializer):
    flags = FlagSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = ['id', 'title', 'body', 'source', 'last_updated', 'flags']
        read_only_fields = ['id', 'last_updated', 'flags']
