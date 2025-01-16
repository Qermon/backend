from rest_framework import serializers
from services.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('__all__')


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()
    client_name = serializers.CharField(source='client.company_name')
    email = serializers.CharField(source='client.user.email')
    price = serializers.SerializerMethodField()
    remaining_time = serializers.SerializerMethodField()
    status = serializers.CharField()

    def get_price(self, instance):
        return instance.price

    def get_remaining_time(self, instance):
        total_seconds = instance.get_time_remaining()
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        time_parts = []
        if hours > 0:
            time_parts.append(f'Hours: {hours}')
        if minutes > 0:
            time_parts.append(f'Minutes: {minutes}')
        if seconds > 0 or not time_parts:
            time_parts.append(f'Seconds: {seconds}')

        return ' '.join(time_parts)

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'client_name', 'email', 'plan', 'price', 'remaining_time', 'status')
