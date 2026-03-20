from django.utils import timezone

from content_monitoring.models import Flag
from content_monitoring.services.suppression_service import SuppressionService


class FlaggingService:
    """Service layer for flag creation and review state management."""

    def __init__(self, suppression_service: SuppressionService | None = None) -> None:
        self.suppression_service = suppression_service or SuppressionService()

    def create_flag(self, validated_data: dict) -> Flag:
        validated_data.setdefault(
            'status',
            self.suppression_service.default_status_for_score(validated_data['score']),
        )
        if validated_data['status'] != Flag.Status.PENDING:
            validated_data.setdefault('last_reviewed_at', timezone.now())
        return Flag.objects.create(**validated_data)
