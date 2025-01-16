from django.contrib.auth.models import User
from django.test import TestCase
from collections import OrderedDict
from clients.models import Client, CompanyName
from services.serializers import PlanSerializer, SubscriptionSerializer
from services.models import Service, Plan, Subscription


class PlanSerializerTestCase(TestCase):
    def test_plan(self):
        plan1 = Plan.objects.create(plan_type='full', discount_percent=0)
        plan2 = Plan.objects.create(plan_type='student', discount_percent=15)
        data = PlanSerializer([plan1, plan2], many=True).data
        expected_data = [
            {
                'id': plan1.id,
                'plan_type': 'full',
                'discount_percent': 0
            },
            {
                'id': plan2.id,
                'plan_type': 'student',
                'discount_percent': 15
            }
        ]
        self.assertEqual(expected_data, data)


class SubscriptionSerializerTestCase(TestCase):
    def test_subscription(self):
        user1 = User.objects.create_user(username='testuser2', password='password', email='usertest@gmail.com')
        company1 = CompanyName.objects.create(name='Test Company2')

        client1 = Client.objects.create(
            user=user1,
            company_name=company1,
            full_address='Test1'
        )

        service1 = Service.objects.create(
            name='servicetest1',
            full_price=100
        )

        plan1 = Plan.objects.create(
            plan_type='full',
            discount_percent=0
        )

        subscription1 = Subscription.objects.create(
            client=client1,
            service=service1,
            plan=plan1,
            price=100,
            status='active',
            time_remaining=10 * 3600
        )

        subscription2 = Subscription.objects.create(
            client=client1,
            service=service1,
            plan=plan1,
            plan_id=plan1.id,
            price=200,
            status='pending',
            time_remaining=0
        )

        data = SubscriptionSerializer([subscription1, subscription2], many=True).data
        expected_data = [
            OrderedDict({
                'id': subscription1.id,
                'plan_id': plan1.id,
                'client_name': company1.name,
                'email': 'usertest@gmail.com',
                'plan': OrderedDict(PlanSerializer(plan1).data),
                'price': 100,
                'remaining_time': 'Hours: 10',
                'status': 'active'
            }),
            OrderedDict({
                'id': subscription2.id,
                'plan_id': plan1.id,
                'client_name': company1.name,
                'email': 'usertest@gmail.com',
                'plan': OrderedDict(PlanSerializer(plan1).data),
                'price': 200,
                'remaining_time': 'Seconds: 0',
                'status': 'pending'
            })
        ]
        self.assertEqual(expected_data, data)
