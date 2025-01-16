from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SubscriptionApiTest(APITestCase):
    def test_get(self):

        url = reverse('subscription-list')

        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
