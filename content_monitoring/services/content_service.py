from content_monitoring.models import ContentItem
from content_monitoring.services.scan_service import ScanService


class ContentService:
    """Service layer for content-related workflows."""

    def __init__(self, scan_service: ScanService | None = None) -> None:
        self.scan_service = scan_service or ScanService()

    def create_content(self, validated_data: dict) -> ContentItem:
        return ContentItem.objects.create(**validated_data)

    def create_and_scan_content(self, validated_data: dict) -> ContentItem:
        content_item = self.create_content(validated_data)
        self.scan_service.scan_content_item(content_item)
        return content_item
