"""Views for job applications.

This module provides API endpoints for managing job applications.
"""

from django.db import models
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters

from .models import Application
from .serializers import ApplicationSerializer
from .services.email_service import EmailService
from .services.metrics_service import MetricsService


class ApplicationFilter(django_filters.FilterSet):
    """Filter set for job applications."""

    company_name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter()
    search = django_filters.CharFilter(method='search_fields')

    def search_fields(self, queryset, name, value):
        """Search across multiple fields."""
        return queryset.filter(
            models.Q(job_title__icontains=value) |
            models.Q(company_name__icontains=value) |
            models.Q(applicant_name__icontains=value)
        )

    class Meta:
        model = Application
        fields = ['company_name', 'status']


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for job applications."""

    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ApplicationFilter
    search_fields = ['applicant_name', 'job_title', 'company_name', 'email_content']
    ordering_fields = ['created_at', 'updated_at', 'company_name', 'job_title']

    def get_queryset(self):
        """Get applications for the current user."""
        return Application.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new application."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def send_follow_up(self, request, pk=None):
        """Send a follow-up email for a job application.

        Args:
            request: HTTP request object.
            pk: Primary key of the application.

        Returns:
            Response: HTTP response with success status and message.
        """
        # Check if user has Gmail credentials
        if not hasattr(request.user, 'gmail_credentials') or not request.user.gmail_credentials:
            return Response(
                {'error': 'Gmail credentials not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get application for current user
        try:
            application = Application.objects.get(id=pk, user=request.user)
        except Application.DoesNotExist:
            return Response(
                {'error': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid application ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send follow-up email
        try:
            result = EmailService.send_follow_up_email(
                application_id=str(application.id),
                user_credentials=request.user.gmail_credentials
            )
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': result.get('message', 'Failed to send email')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get job application metrics for the current user.

        Returns:
            Response: HTTP response containing calculated metrics.
        """
        try:
            metrics = MetricsService.calculate_metrics(request.user)
            return Response(metrics, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
