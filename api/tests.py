from rest_framework.test import APIClient
from django.urls import reverse
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Subscriptions

class TestWeatherApi(TestCase):

    def setUp(self):
        self.client = APIClient()

        def create_test_user():
            new_user = CustomUser.objects.create(username="tester", email="test10@example.com")
            new_user.set_password('12345678')
            new_user.save()
            return new_user

        def set_jwt_token(test_user):
            refresh = RefreshToken.for_user(test_user)
            self.access_token = str(refresh.access_token)
            self.refresh_token = str(refresh)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        if 'test_register' in self._testMethodName:
            return
        elif 'test_token' in self._testMethodName:
            create_test_user()
        elif 'test_subscribe' in self._testMethodName:
            user = create_test_user()
            set_jwt_token(user)
        else:
            self.user = create_test_user()
            set_jwt_token(self.user)
            self.Subscription = Subscriptions.objects.create(user = self.user, city = 'snovsk',
                                                           notification_frequency = '2')

    def test_register_view(self):
        data = {
                  "username": "tester5",
                  "email": "test5@example.com",
                  "password": "12345678",
                  "password2": "12345678"
                }
        response = self.client.post(reverse('register'), data = data)
        user = CustomUser.objects.get(username='tester5')

        assert 'User registered successfully' in str(response.data)
        assert response.status_code == 201
        assert user.username == 'tester5'
        assert user.preferred_notification_type == 'email'

    def test_register_without_email(self):
        data = {
            "username": "tester5",
            "password": "12345678",
            "password2": "12345678"
        }
        response = self.client.post(reverse('register'), data = data)

        assert 'This field is required' in str(response.data)
        assert response.status_code == 400

    def test_register_with_different_passwords(self):
        data = {
            "username": "tester5",
            "email": "test5@example.com",
            "password": "12345678",
            "password2": "12345679"
        }
        response = self.client.post(reverse('register'), data = data)

        assert 'The passwords do not match' in str(response.data)
        assert response.status_code == 400

    def test_register_with_webhook_conflict(self):
        data = {
              "username": "tester5",
              "email": "test5@example.com",
              "password": "12345678",
              "password2": "12345678",
              "preferred_notification_type": "webhook",
            }
        response = self.client.post(reverse('register'), data = data)

        assert 'Webhook URL is required when preferred notification type is webhook.' in str(response.data)
        assert response.status_code == 400

    def test_registration_with_existing_username(self):
        data = {
            "username": "tester",
            "password": "12345678",
            "password2": "12345678"
        }
        response = self.client.post(reverse('register'), data = data)

        assert 'A user with that username already exists.' in str(response.data)
        assert response.status_code == 400

    def test_token_obtain_view(self):
        data = {"username": "tester","password": "12345678"}
        response = self.client.post(reverse('token_obtain_pair'), data = data)

        assert response.data['access'] and 'refresh' in str(response.data)
        assert response.status_code == 200

    def test_refresh_token_view(self):
        response = self.client.post(reverse('token_refresh'), data = {'refresh' : self.refresh_token})

        assert response.data['access'] in str(response.data)
        assert response.status_code == 200

    def test_token_not_given(self):
        response = self.client.post(reverse('subscribe'), data ={'some key':'some value'})

        assert response.data['detail'] == 'Authentication credentials were not provided.'
        assert response.status_code == 401

    def test_subscribe_view(self):
        data = {
            "city": "paris",
            "notification_frequency": "2",
            "humidity": "False",
            "precipitation_probability": "False",
            "wind_speed": "False"
        }
        response = self.client.post(reverse('subscribe'), data=data)

        assert response.status_code == 201
        assert response.data['subscription'] == {'city': 'paris', 'user': 'tester'}

    def test_subscribe_without_city(self):
        data = {
            "notification_frequency": "2",
        }
        response = self.client.post(reverse('subscribe'), data=data)

        assert response.data['city'] == ["This field is required."]
        assert response.status_code == 400

    def test_subscribe_invalid_city(self):
        data = {
            "city": "paris12",
        }
        response = self.client.post(reverse('subscribe'), data=data)

        assert response.data['city'] == ["Invalid location"]
        assert response.status_code == 400

    def test_subs_list_view(self):
        Subscriptions.objects.create(user=self.user, city='london')
        response = self.client.get(reverse('subs_list'))

        assert 'snovsk' and 'london' in str(response.data)
        assert response.status_code == 200

    def test_update_subscription_view(self):
        response = self.client.put(reverse('update_subscription', kwargs = {'pk' : self.Subscription.id }),
                                   data = {"notification_frequency": "12"})

        self.Subscription.refresh_from_db()

        assert response.status_code == 200
        assert response.data['message'] == 'Subscription updated successfully'
        assert self.Subscription.notification_frequency == 12

    def test_delete_subscription_view(self):
        response = self.client.delete(reverse('delete_subscription', kwargs = {'pk': self.Subscription.id}))
        subscription_after = Subscriptions.objects.filter(user = self.user, city = 'snovsk').exists()

        assert response.status_code == 200
        assert subscription_after == False