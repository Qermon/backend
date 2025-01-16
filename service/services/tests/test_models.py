from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now, timedelta
from unittest.mock import patch
from services.models import Service, Plan, Subscription
from clients.models import Client, CompanyName


class SubscriptionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='password')
        self.company1 = CompanyName.objects.create(name='Test Company')

        self.client1 = Client.objects.create(
            user=self.user1,
            company_name=self.company1,
            full_address='Test'
        )

        self.service1 = Service.objects.create(
            name='service1',
            full_price=100
        )

        self.plan1 = Plan.objects.create(
            plan_type='full',
            discount_percent=0
        )

        self.subscription1 = Subscription.objects.create(
            client=self.client1,
            service=self.service1,
            plan=self.plan1,
            price=100,
            status='active',
            time_remaining=0
        )

    @patch('services.tasks.set_price.delay')
    @patch('services.tasks.set_comment.delay')
    def test_service_full_price(self, mock_set_comment, mock_set_price):
        self.service1.full_price = 200
        self.service1.save()

        self.assertTrue(mock_set_price.called)
        self.assertTrue(mock_set_comment.called)

        for subscription in self.service1.subscriptions.all():
            mock_set_price.assert_any_call(subscription.id)
            mock_set_comment.assert_any_call(subscription.id)

    @patch('services.tasks.set_price.delay')
    @patch('services.tasks.set_comment.delay')
    def test_plan_discount_change(self, mock_set_comment, mock_set_price):
        self.plan1.discount_percent = 20
        self.plan1.save()

        self.assertTrue(mock_set_price.called)
        self.assertTrue(mock_set_comment.called)

        for subscription in self.plan1.subscriptions.all():
            mock_set_price.assert_any_call(subscription.id)
            mock_set_comment.assert_any_call(subscription.id)

    @patch('services.tasks.set_price.delay')
    @patch('services.tasks.set_comment.delay')
    def test_no_change(self, mock_set_comment, mock_set_price):
        self.service1.save()
        self.plan1.save()

        mock_set_price.assert_not_called()
        mock_set_comment.assert_not_called()

    @patch('services.tasks.set_price.delay')
    def test_status_change(self, mock_set_price):
        self.subscription1.status = 'active'
        self.subscription1.save()
        self.assertEqual(self.subscription1.time_remaining, 10 * 3600)

        self.subscription1.status = 'expired'
        self.subscription1.save()
        self.assertEqual(self.subscription1.time_remaining, 0)

    def test_default_comment(self):
        subscription = Subscription.objects.create(
            client=self.client1,
            service=self.service1,
            plan=self.plan1,
            price=200
        )
        self.assertTrue(subscription.comment.startswith(now().strftime('%Y-%m-%d')))

    def test_get_time_remaining(self):
        self.subscription1.start_time = now() - timedelta(hours=1)
        self.subscription1.save()
        remaining_time = self.subscription1.get_time_remaining()
        self.assertEqual(remaining_time, 9 * 3600)

    def test_indexing_on_price(self):
        subscriptions = Subscription.objects.filter(price=100, status='active')
        self.assertIn(self.subscription1, subscriptions)
