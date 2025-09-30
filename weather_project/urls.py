from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (RegisterUserView, SubsListView, SubscriptionCreateView, SubscriptionUpdateView,
                       DeleteSubscriptionView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterUserView.as_view(), name = 'register'),
    # path('drf_auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('api/subs_list/', SubsListView.as_view(), name = 'subs_list'),
    path('api/subscribe/', SubscriptionCreateView.as_view(), name = 'subscribe'),
    path('api/subscriptions/update/<int:pk>/', SubscriptionUpdateView.as_view(), name = 'update_subscription'),
    path('api/subscriptions/delete/<int:pk>/', DeleteSubscriptionView.as_view(), name = 'delete_subscription'),
]
