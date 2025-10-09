from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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

class Subscriptions(models.Model):
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    city = models.CharField(max_length = 20)
    notification_frequency = models.IntegerField(default = 24)
    humidity = models.BooleanField(default = True)
    precipitation_probability = models.BooleanField(default = True)
    wind_speed = models.BooleanField(default = True)
    last_notified = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'city')