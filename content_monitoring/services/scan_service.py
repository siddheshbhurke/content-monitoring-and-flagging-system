from __future__ import annotations

from django.db import transaction

from content_monitoring.models import ContentItem, Flag, Keyword
from content_monitoring.services.matching_service import MatchingService
from content_monitoring.services.suppression_service import SuppressionService


class ScanService:
    """Coordinates scanning content items against configured keywords."""

    def __init__(
        self,
        matching_service: MatchingService | None = None,
        suppression_service: SuppressionService | None = None,
    ) -> None:
        self.matching_service = matching_service or MatchingService()
        self.suppression_service = suppression_service or SuppressionService()

    @transaction.atomic
    def scan_content_item(self, content_item: ContentItem) -> list[Flag]:
        flags: list[Flag] = []
        for keyword in Keyword.objects.all():
            score = self.matching_service.score_keyword_match(keyword=keyword, content_item=content_item)
            status = self.suppression_service.default_status_for_score(score)
            flag, _ = Flag.objects.update_or_create(
                keyword=keyword,
                content_item=content_item,
                defaults={
                    'score': score,
                    'status': status,
                },
            )
            flags.append(flag)
        return flags
