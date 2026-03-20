from __future__ import annotations

from decimal import Decimal

from content_monitoring.models import Flag


class SuppressionService:
    """Determines whether low-signal matches should be treated as suppressed/irrelevant."""

    suppression_threshold = Decimal('0.00')

    def should_suppress(self, score: Decimal) -> bool:
        return score <= self.suppression_threshold

    def should_skip_irrelevant_flag(self, flag: Flag, content_updated: bool) -> bool:
        return flag.status == Flag.Status.IRRELEVANT and not content_updated

    def default_status_for_score(self, score: Decimal) -> str:
        if self.should_suppress(score):
            return Flag.Status.IRRELEVANT
        return Flag.Status.PENDING
