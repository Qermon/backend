from django.test import TestCase
from django.urls import reverse
from django.db.models import Avg
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from clients.models import Client, CompanyName
from services.models import Subscription, Plan, Service


"""
Команди для тестування
docker-compose run --rm web-app sh -c "coverage run manage.py test services.tests.test_views"
docker-compose run --rm web-app sh -c "coverage report"
"""


class SubscriptionViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(username='testuser', password='password', email='user1@example.com')
        self.user2 = User.objects.create_user(username='testuser2', password='password', email='user2@example.com')

        self.company1 = CompanyName.objects.create(name='Company 1')
        self.company2 = CompanyName.objects.create(name='Company 2')

        self.client1 = Client.objects.create(user=self.user1, company_name=self.company1, full_address='Address 1')
        self.client2 = Client.objects.create(user=self.user2, company_name=self.company2, full_address='Address 2')

        self.plan1 = Plan.objects.create(plan_type='basic', discount_percent=10)
        self.plan2 = Plan.objects.create(plan_type='premium', discount_percent=20)

        self.service1 = Service.objects.create(name='Service 1', full_price=100)
        self.service2 = Service.objects.create(name='Service 2', full_price=200)

        self.subscription1 = Subscription.objects.create(
            client=self.client1,
            service=self.service1,
            plan=self.plan1,
            price=90,
            status='active',
            time_remaining=30
        )
        self.subscription2 = Subscription.objects.create(
            client=self.client2,
            service=self.service2,
            plan=self.plan2,
            price=160,
            status='pending',
            time_remaining=0
        )

        self.url = reverse('subscription-list')

    def test_list_subscriptions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('result', response.data)
        self.assertIn('total_amount', response.data)
        self.assertIn('active_quantity', response.data)
        self.assertIn('average_price', response.data)

    def test_active_quantity(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        active_quantity = Subscription.objects.filter(status='active').count()
        self.assertEqual(response.data['active_quantity'], active_quantity)

    def test_average_price(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        avg_price = Subscription.objects.aggregate(avg=Avg('price'))['avg']
        self.assertEqual(response.data['average_price'], avg_price)
