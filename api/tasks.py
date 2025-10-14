import os

from celery import shared_task
from django.core.mail import send_mail
import requests

from .models import Subscription


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

    fields = ",".join(subscription.weather_params_list)

    url = f"https://api.tomorrow.io/v4/timelines?location={subscription.city}" \
          f"&fields={fields}" \
          f"&timesteps=1h&startTime={subscription.start_time}" \
          f"&endTime={subscription.end_time}" \
          f"&apikey={os.getenv('TOMMOROWIO_API_KEY')}"

    api_response = get_weather_data(url)
    message = readable_message(api_response)
    user = subscription.user

    if user.preferred_notification_type == 'Webhook':
        requests.post(url = user.webhook_url, json = message)
    else:
        send_mail(
            f"Weather forecat for {subscription.forecast_days} days, city {subscription.city}.",
            message,
            os.getenv('EMAIL_HOST_USER'),
            [user.email],
        )
