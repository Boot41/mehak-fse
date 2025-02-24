"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Authentication endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/gmail/', include('gmail.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Job applications API
    path('api/', include('job_applications.urls')),
]
