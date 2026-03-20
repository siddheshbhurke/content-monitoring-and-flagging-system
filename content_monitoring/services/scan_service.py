from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.db import transaction

from content_monitoring.models import ContentItem, Flag, Keyword
from content_monitoring.services.matching_service import MatchingService
from content_monitoring.services.suppression_service import SuppressionService


class ScanService:
    """Coordinates dataset-driven scanning against configured keywords."""

    default_dataset_path = Path(__file__).resolve().parents[1] / 'data' / 'mock_content.json'

    def __init__(
        self,
        matching_service: MatchingService | None = None,
        suppression_service: SuppressionService | None = None,
    ) -> None:
        self.matching_service = matching_service or MatchingService()
        self.suppression_service = suppression_service or SuppressionService()

    def load_dataset(self, dataset_path: str | None = None) -> list[dict[str, Any]]:
        path = Path(dataset_path) if dataset_path else self.default_dataset_path
        with path.open() as dataset_file:
            return json.load(dataset_file)

    @transaction.atomic
    def scan_dataset(self, dataset_path: str | None = None) -> dict[str, int]:
        dataset = self.load_dataset(dataset_path=dataset_path)
        summary = {
            'content_items_scanned': 0,
            'content_items_created': 0,
            'content_items_updated': 0,
            'flags_created': 0,
            'flags_updated': 0,
            'flags_skipped': 0,
        }

        for item_data in dataset:
            content_item, created, updated = self.upsert_content_item(item_data)
            summary['content_items_scanned'] += 1
            summary['content_items_created'] += int(created)
            summary['content_items_updated'] += int(updated)

            flag_summary = self.scan_content_item(content_item=content_item, content_updated=created or updated)
            summary['flags_created'] += flag_summary['created']
            summary['flags_updated'] += flag_summary['updated']
            summary['flags_skipped'] += flag_summary['skipped']

        return summary

    def upsert_content_item(self, item_data: dict[str, Any]) -> tuple[ContentItem, bool, bool]:
        content_item = ContentItem.objects.filter(source=item_data['source']).first()
        if content_item is None:
            return ContentItem.objects.create(**item_data), True, False

        content_updated = any(
            getattr(content_item, field_name) != item_data[field_name]
            for field_name in ('title', 'body')
        )
        if content_updated:
            content_item.title = item_data['title']
            content_item.body = item_data['body']
            content_item.save(update_fields=['title', 'body', 'last_updated'])

        return content_item, False, content_updated

    def scan_content_item(self, content_item: ContentItem, content_updated: bool) -> dict[str, int]:
        summary = {'created': 0, 'updated': 0, 'skipped': 0}

        for keyword in Keyword.objects.all():
            score = self.matching_service.score_keyword_match(keyword=keyword, content_item=content_item)
            existing_flag = Flag.objects.filter(keyword=keyword, content_item=content_item).first()

            if existing_flag and self.suppression_service.should_skip_irrelevant_flag(existing_flag, content_updated):
                summary['skipped'] += 1
                continue

            if self.suppression_service.should_suppress(score):
                if existing_flag and content_updated:
                    existing_flag.score = score
                    existing_flag.status = Flag.Status.IRRELEVANT
                    existing_flag.save(update_fields=['score', 'status'])
                    summary['updated'] += 1
                continue

            status = self.suppression_service.default_status_for_score(score)
            flag, created = Flag.objects.update_or_create(
                keyword=keyword,
                content_item=content_item,
                defaults={
                    'score': score,
                    'status': status,
                },
            )
            summary['created' if created else 'updated'] += 1

        return summary
