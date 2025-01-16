from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.utils import timezone

from services.receivers import delete_cache_total_sum
from services.tasks import set_price, set_comment
from clients.models import Client


# Create your models here.


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)

                                                   ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        if self.discount_percent != self.__discount_percent:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending')
    ]

    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=50, default='', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField(null=True, blank=True)
    time_remaining = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['price', 'status']),
        ]

    def save(self, *args, **kwargs):
        creating = not bool(self.id)

        if self.status == 'expired':
            self.time_remaining = 0

        if self.status == 'active':
            if not self.start_time:
                self.start_time = timezone.now()

            if self.time_remaining == 0:
                self.time_remaining = 10 * 3600

        if creating and not self.comment:
            self.comment = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        result = super().save(*args, **kwargs)

        if creating:
            set_price.delay(self.id)

        return result

    def get_time_remaining(self):
        if self.status == 'active' and self.start_time:
            elapsed_time = (timezone.now() - self.start_time).total_seconds()
            remaining_time = self.time_remaining - int(elapsed_time)
            if remaining_time <= 0:
                self.status = 'expired'
                self.time_remaining = 0
                self.save()
                return 0
            return remaining_time
        return 0

    def __str__(self):
        return f'Subscription for {self.client}'


post_delete.connect(delete_cache_total_sum, sender=Subscription)





