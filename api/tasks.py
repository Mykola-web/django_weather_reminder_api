import os
from datetime import datetime, timedelta
import json

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
import requests

from .models import Subscriptions, CustomUser

def build_api_link(data):
    apikey = os.getenv('TOMMOROWIO_API_KEY')

    interval_start_dt = datetime.fromisoformat(data['last_notified'].replace('Z', '+00:00'))
    interval_end_dt = interval_start_dt + timedelta(hours=data['notification_frequency'])
    interval_start = interval_start_dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    interval_end = interval_end_dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    fields = 'temperature,'

    if data['humidity']:
        fields += 'humidity,'
    if data['precipitationProbability']:
        fields += 'precipitationProbability,'
    if data['wind_speed']:
        fields += 'windSpeed,'

    fields = fields.rstrip(',')

    url = f"https://api.tomorrow.io/v4/timelines?location={data['city']}" \
          f"&fields={fields}" \
          f"&timesteps=1h&startTime={interval_start}" \
          f"&endTime={interval_end}" \
          f"&timezone=Europe/Kyiv" \
          f"&apikey={apikey}"
    print(url)
    return url


def get_weather_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Api request status error", e)
        return None

    try:
        data = response.json()
    except ValueError:
        print("API return not valid JSON")
        return None

    if 'data' not in data or not data['data'].get('timelines'):
        print("API returned empty or invalid data:", data)
        return None

    return response


@shared_task
def send_weather_notification(data):
    print(f"Sending notification to user {data['user_id']} with data: {data}")

    url = build_api_link(data)

    api_response = get_weather_data(url)

    if not api_response:
        return  f"No data for city {data['city']} at that moment, wait for further notifications"

    intervals = api_response.json()['data']['timelines'][0]['intervals']
    notifications = []
    for interval in intervals:
        # Extract only the hour and minute from startTime
        time = interval['startTime'][11:16]  # HH:MM
        values = interval['values']
        text = f"Time: {time}, Temperature: {values.get('temperature', '-')}°C, " \
               f"Humidity: {values.get('humidity', '-')}%, " \
               f"Precipitation Probability: {values.get('precipitationProbability', '-')}%, " \
               f"Wind Speed: {values.get('windSpeed', '-')} m/s"
        notifications.append(text)

    final_message = "\n".join(notifications)

    user = CustomUser.objects.get(id = data['user_id'])
    #sending message to email or webhook
    if user.preferred_notification_type == 'Webhook':
        requests.post(url = user.webhook_url, json = final_message)
    else:
        send_mail(
            f"Weather notification for {data['city']}, next {data['notification_frequency']} hours",
            final_message,
            os.getenv('EMAIL_HOST_USER'),
            [user.email],
        )
    #updating last notified time
    Subscriptions.objects.filter(user_id = data['user_id'],
                                 city = data['city']).update(last_notified=timezone.now())


@shared_task
def check_and_send_notifications():
    now = timezone.now()
    for subscription in Subscriptions.objects.all():
        if not subscription.last_notified or now - subscription.last_notified >= subscription.notification_frequency:
            notification_data = {
                "user_id": subscription.user.id,
                "city": subscription.city,
                "notification_frequency": subscription.notification_frequency,
                'humidity': subscription.humidity,
                'precipitationProbability': subscription.precipitationProbability,
                'wind_speed': subscription.wind_speed,
                "last_notified": subscription.last_notified.isoformat() if subscription.last_notified else None,
            }
            send_weather_notification.delay(subscription.user, subscription)
            subscription.save()