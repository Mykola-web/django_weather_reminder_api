from django.db.models.signals import post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import Subscription

@receiver(post_delete, sender=Subscription)
def delete_related_periodic_task(sender, instance, **kwargs):
    task_name = f"weather_notification_for_subscription_id_{instance.id}"
    try:
        task = PeriodicTask.objects.get(name=task_name)
        schedule = task.crontab
        task.delete()
        if not PeriodicTask.objects.filter(crontab=schedule).exists():
            schedule.delete()
    except PeriodicTask.DoesNotExist:
        pass
