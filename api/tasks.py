import os
from datetime import datetime, timedelta, date

from celery import shared_task
from django.core.mail import send_mail
import requests

from .models import Subscription, CustomUser


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


def readable_message(api_response):
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
    return final_message


@shared_task
def release_subscription(subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)

    dt = datetime.combine(date.today(), subscription.preferred_notification_time)
    dt_plus_one = (dt + timedelta(days=subscription.forecast_days))
    forecast_start = dt.isoformat()  # example '2025-10-13T06:00:00'
    forecast_end = dt_plus_one.isoformat()  # example '2025-10-14T06:00:00'

    fields = ",".join(subscription.weather_params_list)

    url = f"https://api.tomorrow.io/v4/timelines?location={subscription.city}" \
          f"&fields={fields}" \
          f"&timesteps=1h&startTime={forecast_start}" \
          f"&endTime={forecast_end}" \
          f"&timezone=Europe/Kyiv" \
          f"&apikey={os.getenv('TOMMOROWIO_API_KEY')}"

    api_response = get_weather_data(url)
    message = readable_message(api_response)
    user = subscription.user

    if user.preferred_notification_type == 'Webhook':
        requests.post(url = user.webhook_url, json = message)
    else:
        send_mail(
            f"Weather notification for {subscription.city}, forecast {subscription.forecast_days} hours",
            message,
            os.getenv('EMAIL_HOST_USER'),
            [user.email],
        )
