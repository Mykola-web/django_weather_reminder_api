import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .models import Subscription

def create_weather_subscription(subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)

    hour = subscription.preferred_notification_time.hour
    minute = subscription.preferred_notification_time.minute

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=str(minute),
        hour=str(hour),
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
        timezone=str(subscription.timezone),
    )

    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name=f"weather_notification_for_subscription_id_{subscription.id}",
        task='api.tasks.release_subscription',
        args=json.dumps([subscription.id]),
    )
