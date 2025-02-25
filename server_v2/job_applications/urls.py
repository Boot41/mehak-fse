"""URL configuration for job applications.

This module defines the URL patterns for job application-related views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'applications', JobApplicationViewSet, basename='job-application')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
