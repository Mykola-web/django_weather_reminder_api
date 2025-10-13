import os
from datetime import time

from django.contrib.auth import authenticate
from rest_framework import serializers
import requests
from dotenv import load_dotenv

from .models import CustomUser, Subscription

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
        model = Subscription
        fields = ['id', 'user', 'city', 'preferred_notification_time',
                  'forecast_days','weather_params_list']
        read_only_fields = ['id', 'user']

    def validate_city(self, value):
        #city existence validation
        apikey = os.getenv('TOMMOROWIO_API_KEY')
        response = requests.get(
            f"https://api.tomorrow.io/v4/weather/realtime?location={value}&apikey={apikey}")

        if response.status_code != 200:
            raise serializers.ValidationError("Invalid location")
        #one city one subscription check means no duplication
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError("You must be logged in")

        if Subscription.objects.filter(user=user, city=value).exists():
            raise serializers.ValidationError("You already have a subscription for this city.")

        return value

    def validate_weather_params_list(self, value):
        allowed = {"humidity", "temperature", "windSpeed", "precipitationProbability"}
        if not all(param in allowed for param in value):
            raise serializers.ValidationError("Incorrect weather parameters in given list")
        return value

    def validate_preferred_notification_time(self, value):
        if not isinstance(value, time):
            raise serializers.ValidationError("Time must be in HH:MM format")
        if value.hour < 0 or value.hour > 23 or value.minute < 0 or value.minute > 59:
            raise serializers.ValidationError("Invalid hour or minute")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Subscription.objects.create(user=user, **validated_data)


class SubscriptionUpdateSerializer(SubscriptionSerializer):
    class Meta(SubscriptionSerializer.Meta):
        read_only_fields = ['id', 'user', 'city']
