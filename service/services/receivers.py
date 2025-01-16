from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from clients.models import Client, CompanyName


@receiver(post_delete, sender=None)
def delete_cache_total_sum(*args, **kwargs):
    cache.delete(settings.PRICE_CACHE_NAME)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def post_create_client(sender, instance, created, **kwargs):
    if created:
        email = instance.email
        company = CompanyName.objects.first()

        if company:
            new_client = Client.objects.create(
                user=instance,
                company_name=company,
                full_address=email
            )
            new_client.save()


@receiver(post_save, sender=Client)
def create_subscription(sender, instance, created, **kwargs):
    from .models import Subscription, Service, Plan
    if created:
        service = Service.objects.filter(name='Phone Calls').first()
        email = instance.user.email

        if 'student' in email:
            plan = Plan.objects.filter(plan_type='student').first()
        else:
            plan = Plan.objects.filter(plan_type='full').first()

        if service and plan:
            Subscription.objects.create(
                client=instance,
                service=service,
                plan=plan,
                price=service.full_price,
                status='active',
                start_time=timezone.now(),
                time_remaining=10 * 3600
            )
