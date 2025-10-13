import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone

from .models import Subscription

def create_weather_subscription(user):
    subscription = Subscription.objects.get(user=user)

    hour = subscription.preferred_notification_time.hour
    minute = subscription.preferred_notification_time.minute

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=str(minute),
        hour=str(hour),
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone=str(timezone.get_current_timezone()),
    )

    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name=f"weather_notification_user_{user.id}",
        task='api.tasks.send_weather_notification',
        args=json.dumps([user.id]),
    )
