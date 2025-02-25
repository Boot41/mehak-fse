"""Views for job applications.

This module provides API endpoints for managing job applications.
"""

import logging
from django.db import models
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from django.utils import timezone
from django.db.models import Q
from rest_framework.exceptions import APIException as Http404

from .models import JobApplication, Communication
from .serializers import JobApplicationSerializer, CommunicationSerializer
from .utils.email_parser import EmailParser
from .utils.job_tracker import JobTracker
from .utils.email_service import EmailService

logger = logging.getLogger(__name__)

class JobApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing job applications."""
    permission_classes = [IsAuthenticated]
    serializer_class = JobApplicationSerializer
    
    def get_queryset(self):
        """Get applications for the current user with optional filters."""
        try:
            queryset = JobApplication.objects.filter(user=self.request.user)
            
            # Filter by status
            status_param = self.request.query_params.get('status', None)
            if status_param:
                queryset = queryset.filter(status=status_param)
            
            # Filter by date range
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            if start_date and end_date:
                queryset = queryset.filter(
                    application_date__range=[start_date, end_date]
                )
            
            # Search by company or position
            search = self.request.query_params.get('search', None)
            if search:
                queryset = queryset.filter(
                    Q(company_name__icontains=search) |
                    Q(position__icontains=search)
                )
            
            # Sort by field
            sort_by = self.request.query_params.get('sort', '-application_date')
            return queryset.order_by(sort_by)
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            raise

    def get_object(self):
        """Get object and check permissions."""
        try:
            obj = super().get_object()
            if obj.user != self.request.user:
                raise Http404("Application not found")
            return obj
        except Http404:
            raise
        except Exception as e:
            logger.error(f"Error in get_object: {str(e)}")
            raise Http404("Application not found")

    def perform_create(self, serializer):
        """Create a new application for the current user."""
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get application statistics."""
        try:
            tracker = JobTracker(request.user)
            stats = tracker.get_application_stats()
            return Response(stats)
        except Exception as e:
            logger.error(f"Error in stats action: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def reminders(self, request):
        """Get follow-up reminders."""
        try:
            tracker = JobTracker(request.user)
            reminders = tracker.get_follow_up_reminders()
            return Response(reminders)
        except Exception as e:
            logger.error(f"Error in reminders action: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def add_communication(self, request, pk=None):
        """Add a communication record to a job application."""
        try:
            application = self.get_object()
            serializer = CommunicationSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save(job_application=application)
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http404:
            return Response(
                {'error': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in add_communication action: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update application status with optional notes."""
        try:
            application = self.get_object()
            new_status = request.data.get('status')
            notes = request.data.get('notes', '')
            
            if new_status not in JobApplication.STATUS_DICT:
                return Response(
                    {'error': 'Invalid status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            application.status = new_status
            if notes:
                application.notes = notes
            application.save()
            
            serializer = self.get_serializer(application)
            return Response(serializer.data)
        except Http404:
            return Response(
                {'error': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in update_status: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def parse_email(self, request, pk=None):
        """Parse email content for job details."""
        try:
            email_body = request.data.get('email_body', '')
            email_subject = request.data.get('email_subject', '')
            
            parser = EmailParser()
            details = parser.parse_email(email_body, email_subject)
            
            return Response(details)
        except Exception as e:
            logger.error(f"Error in parse_email action: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def send_follow_up(self, request, pk=None):
        """Send follow-up email for a job application."""
        try:
            application = self.get_object()
            
            # Check if user has Gmail credentials
            if not request.user.gmail_credentials:
                return Response(
                    {'error': 'Gmail credentials not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send follow-up email
            email_service = EmailService()
            result = email_service.send_follow_up_email(
                application_id=str(application.id),
                user_credentials=request.user.gmail_credentials
            )
            
            if result['success']:
                return Response({'success': True, 'message': result['message']})
            else:
                return Response(
                    {'error': result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Http404:
            return Response(
                {'error': 'Application not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in send_follow_up: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
