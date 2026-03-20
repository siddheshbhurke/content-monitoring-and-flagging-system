from content_monitoring.models import Flag


class FlaggingService:
    """Service layer placeholder for flagging-related business logic."""

    def create_flag(self, validated_data: dict) -> Flag:
        return Flag.objects.create(**validated_data)
