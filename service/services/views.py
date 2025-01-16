from django.conf import settings
from django.db.models import Prefetch, F, Sum, Avg
from django.core.cache import cache
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.select_related(
            'user', 'company_name').only('user__email', 'company_name__name'))
    )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        price_cache = cache.get(settings.PRICE_CACHE_NAME)
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60 * 60)

        active_quantity = Subscription.objects.filter(status='active').count()
        avg_price = queryset.aggregate(avg=Avg('price')).get('avg')

        response_data = {'result': response.data}
        response_data['total_amount'] = total_price
        response_data['active_quantity'] = active_quantity
        response_data['average_price'] = avg_price
        response.data = response_data
        return response
