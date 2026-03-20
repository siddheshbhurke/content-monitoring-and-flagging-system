from content_monitoring.models import ContentItem


class ContentService:
    """Service layer placeholder for content-related business logic."""

    def create_content(self, validated_data: dict) -> ContentItem:
        return ContentItem.objects.create(**validated_data)
