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

-Database: PostgreSQL

-ORM: Django ORM

-Framework: Django, Django REST Framework

-Serializers: DRF serializers

-HTTP requests: requests

-Periodic tasks: Celery + Redis

-Authentication: JWT via DRF SimpleJWT