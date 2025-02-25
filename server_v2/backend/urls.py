"""
URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Authentication endpoints
    path('api/auth/', include('authentication.urls')),
    path('api/gmail/', include('gmail.urls')),
    path('api/jobs/', include('job_applications.urls')),
]
