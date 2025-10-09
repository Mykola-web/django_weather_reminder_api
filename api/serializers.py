import os

from django.contrib.auth import authenticate
from rest_framework import serializers
import requests
from dotenv import load_dotenv

from .models import CustomUser, Subscriptions

load_dotenv()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = True)
    password2 = serializers.CharField(write_only = True, required = True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'preferred_notification_type', 'webhook_url']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        email = attrs.get('email')

        if password != password2:
            raise serializers.ValidationError({
                'password': 'The passwords do not match.'
            })

        if email and CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'User with this email already exists'
            })

        if attrs.get('preferred_notification_type') == 'webhook' and not attrs.get('webhook_url'):
            raise serializers.ValidationError({
                'webhook_url': 'Webhook URL is required when preferred notification type is webhook.'
            })
        return attrs

    def create(self, validated_data):
        user = CustomUser(
            username = validated_data['username'],
            email = validated_data['email'],
            webhook_url = validated_data.get('webhook_url', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        user = authenticate(**data)

        if  not user:
            raise serializers.ValidationError("Wrong password or username")

        if not user.is_active:
            raise serializers.ValidationError("User is not active")

        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'preferred_notification_type', 'webhook_url']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ['id', 'user', 'city', 'notification_frequency',
                  'humidity', 'precipitation_probability', 'wind_speed','last_notified']
        read_only_fields = ['id', 'user', 'last_notified']

    def validate_city(self, value):
        #city existence validation
        apikey = os.getenv('TOMMOROWIO_API_KEY')
        response = requests.get(
            f"https://api.tomorrow.io/v4/weather/realtime?location={value}&apikey={apikey}")

        if response.status_code != 200:
            raise serializers.ValidationError("Invalid location")
        #one city one subscription check means no dublication
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError("You must be logged in")

        if Subscriptions.objects.filter(user=user, city=value).exists():
            raise serializers.ValidationError("You already have a subscription for this city.")

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Subscriptions.objects.create(user=user, **validated_data)


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = [ 'notification_frequency', 'humidity', 'precipitation_probability', 'wind_speed']