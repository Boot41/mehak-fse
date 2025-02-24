from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GoogleAuthView

app_name = 'authentication'

urlpatterns = [
    # Google OAuth endpoints
    path('google/login/', GoogleAuthView.as_view(), name='google_auth_login'),
    path('google/callback/', GoogleAuthView.as_view(), name='google_auth_callback'),
    
    # JWT token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Logout endpoint (handled by frontend)
    path('logout/', GoogleAuthView.as_view(), name='logout'),
]
