from __future__ import annotations

from decimal import Decimal

from content_monitoring.models import ContentItem, Keyword


class MatchingService:
    """Encapsulates keyword-to-content scoring logic."""

    def score_keyword_match(self, keyword: Keyword, content_item: ContentItem) -> Decimal:
        keyword_text = keyword.name.strip().lower()
        if not keyword_text:
            return Decimal('0.00')

        haystack = f"{content_item.title} {content_item.body}".lower()
        occurrences = haystack.count(keyword_text)
        return Decimal(str(min(occurrences, 100)))
