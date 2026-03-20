from rest_framework import serializers

from .models import Flag, Keyword


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['id', 'name']
        read_only_fields = ['id']


class ScanRequestSerializer(serializers.Serializer):
    dataset_path = serializers.CharField(required=False)


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


class ScanSummarySerializer(serializers.Serializer):
    content_items_scanned = serializers.IntegerField()
    content_items_created = serializers.IntegerField()
    content_items_updated = serializers.IntegerField()
    flags_created = serializers.IntegerField()
    flags_updated = serializers.IntegerField()
    flags_skipped = serializers.IntegerField()
