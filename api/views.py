import json

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, SubscriptionSerializer, LoginSerializer, SubscriptionUpdateSerializer
from .models import Subscription
from .services import create_weather_subscription
from .tasks import release_subscription


class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()

        return Response({
            "message": "User registered successfully",
            "user": RegisterSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class SubscriptionCreateView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        release_subscription.delay([subscription.id])
        # create_weather_subscription(subscription.id)

        return Response({
            "message": "Subscribed successfully",
            "subscription": {
                "city": subscription.city,
                "user": subscription.user.username
            }
        }, status = status.HTTP_201_CREATED)


class SubsListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        sub= Subscription.objects.filter(user=user).first()
        print(sub.timezone,'00000', type(sub.timezone))
        print(sub)
        return Subscription.objects.filter(user=user)

class SubscriptionUpdateView(generics.GenericAPIView):
    serializer_class = SubscriptionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)

        user = request.user
        subscription_id = self.kwargs['pk']

        subscription = Subscription.objects.get(user = user, id=subscription_id)
        serializer.update(subscription, serializer.validated_data)

        return Response({"message": "Subscription updated successfully"}, status = status.HTTP_200_OK)


class DeleteSubscriptionView(generics.DestroyAPIView):
    serializer_class = SubscriptionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if not hasattr(self, 'subscription'):
            self.subscription = self.get_object()
        self.perform_destroy(self.subscription)
        return Response(
            {"message": f"Subscription for city '{self.subscription.city}' has been deleted."},
            status=200
        )