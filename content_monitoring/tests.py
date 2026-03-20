from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Flag, Keyword


class ContentMonitoringApiTests(APITestCase):
    def test_keyword_creation_endpoint(self):
        response = self.client.post(reverse('keyword-create'), {'name': 'spam'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'spam')

    def test_scan_and_flag_review_flow(self):
        keyword = Keyword.objects.create(name='alert')

        scan_response = self.client.post(
            reverse('scan'),
            {
                'title': 'Alert detected',
                'body': 'This alert appears twice: alert.',
                'source': 'feed-a',
            },
            format='json',
        )

        self.assertEqual(scan_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(scan_response.data['flags']), 1)
        self.assertEqual(scan_response.data['flags'][0]['keyword']['name'], keyword.name)

        flag = Flag.objects.get()
        list_response = self.client.get(reverse('flag-list'))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        update_response = self.client.patch(
            reverse('flag-partial-update', kwargs={'pk': flag.pk}),
            {'status': Flag.Status.RELEVANT},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['status'], Flag.Status.RELEVANT)
