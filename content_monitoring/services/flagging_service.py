from content_monitoring.models import FlagRecord


class FlaggingService:
    """Service layer placeholder for flagging-related business logic."""

    def create_flag(self, validated_data: dict) -> FlagRecord:
        return FlagRecord.objects.create(**validated_data)
