from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import pytz
from pytz import all_timezones


class CustomUser(AbstractUser):
    EMAIL = 'email'
    WEBHOOK = 'webhook'

    NOTIFICATION_CHOICES = [
        (EMAIL, 'Email'),
        (WEBHOOK, 'Webhook'),
    ]

    preferred_notification_type = models.CharField(
        max_length = 10,
        choices = NOTIFICATION_CHOICES,
        default = EMAIL
    )
    webhook_url = models.URLField(blank = True, null = True)

    def clean(self):
        super().clean()
        if self.preferred_notification_type == self.WEBHOOK and not self.webhook_url:
            raise ValidationError({
                'webhook_url': 'Webhook URL is required when preferred notification type is webhook.'
            })


def default_fields():
    return ['humidity', 'temperature', 'precipitationProbability', 'windSpeed']


class Subscription(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    city = models.CharField(max_length=20)
    preferred_notification_time = models.TimeField(default='00:00')
    forecast_days = models.IntegerField(default=1)
    weather_params_list = models.JSONField(default=default_fields)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in all_timezones],
        default='UTC'
    )

    class Meta:
        unique_together = ('user', 'city')

    @property
    def start_time(self):
        tz = pytz.timezone(self.timezone)  # создаем объект таймзоны
        now_local = datetime.now(tz).replace(tzinfo=None)
        now_local_iso = now_local.isoformat()
        return now_local_iso

    @property
    def end_time(self):
        tz = pytz.timezone(self.timezone)  # создаем объект таймзоны
        now_local = datetime.now(tz).replace(tzinfo=None)
        tommorow_local_time = now_local + timedelta(days=self.forecast_days)
        iso_tomorow = tommorow_local_time.isoformat()
        return iso_tomorow