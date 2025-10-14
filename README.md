DjangoWeatherReminder
Project Description

DjangoWeatherReminder is a Django REST Framework API that sends weather notifications to users based on their selected cities and preferred time intervals. Users can subscribe to one or multiple cities and choose their preferred notification method: email or webhook (URL).

After successful login, users receive a JWT token (via DRF SimpleJWT) that authenticates them for every API request while the token is valid.

Features

-User registration: username, password, email, and preferred notification method (email, webhook, or both).

-Login and JWT token issuance using DRF SimpleJWT.

-Subscribe to cities with configurable notification intervals (1, 3, 6, 12 hours).

-Edit and delete subscriptions.

-Retrieve a list of user subscriptions.

-Fetch current weather data from third-party services.

-Periodic weather notifications using Celery + Redis.

Technologies

-Database: PostgresSQL

-ORM: Django ORM

-Framework: Django, Django REST Framework

-Serializers: DRF serializers

-HTTP requests: requests

-Periodic tasks: Django-celery-beat + PeriodicTasks + Redis

-Authentication: JWT via DRF SimpleJWT

To fill database with fake data just enter this command:

python manage.py fake_data_maker --count 10

This command makes 5 (default) new users with 1 subscription to certain city, default = london.
Can be expanded with --count (your number) flag.

How to use:

### 1. Register User
**Endpoint:**

POST /api/register/

**URL:**

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/register/

**Request body (JSON):**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "12345678",
  "password2": "12345678",
  "preferred_notification_type": "webhook",  (optional, defaul = email)
  "webhook_url": "https://example.com/hook"   (optional)
}

2. Get Access & Refresh Tokens

Endpoint:

POST /api/token/

URL:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/token/

Request body (JSON):

{
  "username": "testuser",
  "password": "12345678"
}

3. Refresh Access Token

Endpoint:

POST /api/token/refresh/

URL:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/token/refresh/

Request body (JSON):

{
  "refresh": "YOUR_REFRESH_TOKEN"
}

⚠️ Authorization Header

Authorization: Bearer YOUR_ACCESS_TOKEN

4. Subscribe to Weather Notifications

Endpoint:

POST /api/subscribe/

URL:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/subscribe/

Request body (JSON):

{
  "city": "tbilisi",
  "preferred_notification_time": "18:30",
  "timezone":"Mexico/BajaNorte"
}


Required fields:

    city,
    
⚠️ Notes: 
If you don't specify a time zone, you will receive notifications at 00:00 UTC time.
Example : "timezone":"Mexico/BajaNorte") default='UTC'

Optional fields (with default values):

{
  "preferred_notification_time": "00:00",   // default
  "forecast_days": "1",                // default
  "weather_params_list" : ['humidity', 'temperature', 'precipitationProbability', 'windSpeed'], // default 
  *You can include only the parameters you need and send a list with them, 4 paramaters supported
}

5. List Subscriptions

Endpoint:

GET /api/subs_list/

URL:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/subs_list/

Request:

    No body

    Requires Authorization header with access token

6. Update Subscription

Endpoint:

PUT /api/subscriptions/update/<int:pk>/

URL Example:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/subscriptions/update/12/

Request body (JSON):

{
  "preferred_notification_time": "01:55",
  "timezone":"Europe/Kyiv"
}

⚠️ Notes:

    City cannot be changed

    You cannot subscribe to the same city twice

7. Delete Subscription

Endpoint:

DELETE /api/subscriptions/delete/<int:pk>/

URL Example:

https://django-weather-reminder-api-18886423261.europe-west1.run.app/api/subscriptions/delete/12/

Request:

    No body

    Requires Authorization header with access token