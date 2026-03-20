from content_monitoring.models import Keyword


class KeywordService:
    """Service layer for keyword management."""

    def create_keyword(self, validated_data: dict) -> Keyword:
        return Keyword.objects.create(**validated_data)
