from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    GoogleAuthView,
    UserProfileView,
)

app_name = 'authentication'

urlpatterns = [
    # Google OAuth endpoints
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
    
    # JWT token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # JWT token verify
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    # User profile endpoint
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
