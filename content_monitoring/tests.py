import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContentItem, Flag, Keyword


class ContentMonitoringApiTests(APITestCase):
    def test_keyword_creation_endpoint(self):
        response = self.client.post(reverse('keyword-create'), {'name': 'spam'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'spam')

    def test_scan_endpoint_loads_mock_dataset_and_creates_records(self):
        Keyword.objects.create(name='alert')

        response = self.client.post(reverse('scan'), {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content_items_scanned'], 2)
        self.assertEqual(ContentItem.objects.count(), 2)
        self.assertEqual(Flag.objects.count(), 1)

    def test_irrelevant_flags_are_skipped_until_content_updates(self):
        Keyword.objects.create(name='alert')

        with TemporaryDirectory() as temp_dir:
            dataset_path = Path(temp_dir) / 'mock_content.json'
            dataset_path.write_text(
                json.dumps(
                    [
                        {
                            'source': 'feed-irrelevant',
                            'title': 'Initial alert title',
                            'body': 'alert appears here',
                        }
                    ]
                )
            )

            first_scan = self.client.post(
                reverse('scan'),
                {'dataset_path': str(dataset_path)},
                format='json',
            )
            self.assertEqual(first_scan.status_code, status.HTTP_200_OK)
            flag = Flag.objects.get()

            review_response = self.client.patch(
                reverse('flag-partial-update', kwargs={'pk': flag.pk}),
                {'status': Flag.Status.IRRELEVANT},
                format='json',
            )
            self.assertEqual(review_response.status_code, status.HTTP_200_OK)

            second_scan = self.client.post(
                reverse('scan'),
                {'dataset_path': str(dataset_path)},
                format='json',
            )
            self.assertEqual(second_scan.status_code, status.HTTP_200_OK)
            self.assertEqual(second_scan.data['flags_skipped'], 1)
            self.assertEqual(Flag.objects.count(), 1)
            flag.refresh_from_db()
            self.assertEqual(flag.status, Flag.Status.IRRELEVANT)

            dataset_path.write_text(
                json.dumps(
                    [
                        {
                            'source': 'feed-irrelevant',
                            'title': 'Updated alert title',
                            'body': 'alert appears here with new context',
                        }
                    ]
                )
            )

            third_scan = self.client.post(
                reverse('scan'),
                {'dataset_path': str(dataset_path)},
                format='json',
            )
            self.assertEqual(third_scan.status_code, status.HTTP_200_OK)
            self.assertEqual(third_scan.data['content_items_updated'], 1)
            self.assertEqual(third_scan.data['flags_updated'], 1)
            self.assertEqual(Flag.objects.count(), 1)
            flag.refresh_from_db()
            self.assertEqual(flag.status, Flag.Status.PENDING)
