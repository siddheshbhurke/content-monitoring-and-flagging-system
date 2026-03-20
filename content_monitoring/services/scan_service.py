from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.db import transaction

from content_monitoring.models import ContentItem, Flag, Keyword
from content_monitoring.services.matching_service import MatchingService
from content_monitoring.services.suppression_service import SuppressionService


@dataclass
class ScanSummary:
    content_items_scanned: int = 0
    content_items_created: int = 0
    content_items_updated: int = 0
    flags_created: int = 0
    flags_updated: int = 0
    flags_skipped: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            'content_items_scanned': self.content_items_scanned,
            'content_items_created': self.content_items_created,
            'content_items_updated': self.content_items_updated,
            'flags_created': self.flags_created,
            'flags_updated': self.flags_updated,
            'flags_skipped': self.flags_skipped,
        }


@dataclass
class ContentUpsertResult:
    content_item: ContentItem
    created: bool = False
    updated: bool = False

    @property
    def content_changed(self) -> bool:
        return self.created or self.updated


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

    def resolve_dataset_path(self, dataset_path: str | None = None) -> Path:
        return Path(dataset_path) if dataset_path else self.default_dataset_path

    def load_dataset(self, dataset_path: str | None = None) -> list[dict[str, Any]]:
        path = self.resolve_dataset_path(dataset_path)
        with path.open(encoding='utf-8') as dataset_file:
            return json.load(dataset_file)

    @transaction.atomic
    def scan_dataset(self, dataset_path: str | None = None) -> dict[str, int]:
        summary = ScanSummary()

        for item_data in self.load_dataset(dataset_path=dataset_path):
            upsert_result = self.upsert_content_item(item_data)
            summary.content_items_scanned += 1
            summary.content_items_created += int(upsert_result.created)
            summary.content_items_updated += int(upsert_result.updated)

            flag_summary = self.scan_content_item(
                content_item=upsert_result.content_item,
                content_updated=upsert_result.content_changed,
            )
            summary.flags_created += flag_summary['created']
            summary.flags_updated += flag_summary['updated']
            summary.flags_skipped += flag_summary['skipped']

        return summary.to_dict()

    def upsert_content_item(self, item_data: dict[str, Any]) -> ContentUpsertResult:
        content_item = ContentItem.objects.filter(source=item_data['source']).first()
        if content_item is None:
            return ContentUpsertResult(
                content_item=ContentItem.objects.create(**item_data),
                created=True,
            )

        content_updated = any(
            getattr(content_item, field_name) != item_data[field_name]
            for field_name in ('title', 'body')
        )
        if content_updated:
            content_item.title = item_data['title']
            content_item.body = item_data['body']
            content_item.save(update_fields=['title', 'body', 'last_updated'])

        return ContentUpsertResult(content_item=content_item, updated=content_updated)

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
                    self._mark_existing_flag_irrelevant(existing_flag, score)
                    summary['updated'] += 1
                continue

            created = self._upsert_flag(keyword=keyword, content_item=content_item, score=score)
            summary['created' if created else 'updated'] += 1

        return summary

    def _upsert_flag(self, keyword: Keyword, content_item: ContentItem, score) -> bool:
        _, created = Flag.objects.update_or_create(
            keyword=keyword,
            content_item=content_item,
            defaults={
                'score': score,
                'status': self.suppression_service.default_status_for_score(score),
            },
        )
        return created

    @staticmethod
    def _mark_existing_flag_irrelevant(flag: Flag, score) -> None:
        flag.score = score
        flag.status = Flag.Status.IRRELEVANT
        flag.save(update_fields=['score', 'status'])
