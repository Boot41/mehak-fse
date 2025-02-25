"""Tests for job application metrics.

This module contains tests for the metrics calculation and API endpoint.
"""

from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from job_applications.models import Application, ApplicationMetrics
from job_applications.services.metrics_service import MetricsService

User = get_user_model()


class MetricsServiceTests(TestCase):
    """Test cases for MetricsService."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Set base time
        self.base_time = timezone.now()

        # Create test applications
        self.company1_apps = [
            Application.objects.create(
                user=self.user,
                applicant_name='Test Applicant',
                job_title=f'Software Engineer {i}',
                company_name='Company 1',
                status='applied' if i == 0 else 'interviewed',
                created_at=self.base_time - timedelta(days=10),
                updated_at=self.base_time - timedelta(days=5) if i > 0 else None
            )
            for i in range(3)
        ]

        self.company2_apps = [
            Application.objects.create(
                user=self.user,
                applicant_name='Test Applicant',
                job_title=f'Developer {i}',
                company_name='Company 2',
                status='ghosted',
                created_at=self.base_time - timedelta(days=30)
            )
            for i in range(2)
        ]

        self.company3_apps = [
            Application.objects.create(
                user=self.user,
                applicant_name='Test Applicant',
                job_title=f'Engineer {i}',
                company_name='Company 3',
                status='interviewed' if i == 0 else 'rejected',
                created_at=self.base_time - timedelta(days=15),
                updated_at=self.base_time - timedelta(days=10)
            )
            for i in range(2)
        ]

        # Update all responded applications to have 5 days response time
        for app in Application.objects.filter(user=self.user).exclude(status__in=['applied', 'ghosted']):
            app.updated_at = app.created_at + timedelta(days=5)
            app.save()

    def test_calculate_metrics(self):
        """Test metrics calculation."""
        metrics = MetricsService.calculate_metrics(self.user)

        # Check total applications
        self.assertEqual(metrics['total_applications'], 7)

        # Check rates
        self.assertEqual(metrics['response_rate'], 57.14)
        self.assertEqual(metrics['interview_rate'], 42.86)
        self.assertEqual(metrics['ghosted_rate'], 28.57)

        # Check average response time
        self.assertEqual(metrics['avg_response_time'], 5.0)

        # Check company rankings
        self.assertEqual(len(metrics['best_companies']), 2)
        self.assertEqual(len(metrics['worst_companies']), 2)
        
        # Company 3 should be best (100% response rate)
        self.assertIn('Company 3', metrics['best_companies'])
        self.assertEqual(
            metrics['best_companies']['Company 3']['response_rate'],
            100.0
        )

        # Company 2 should be worst (0% response rate)
        self.assertIn('Company 2', metrics['worst_companies'])
        self.assertEqual(
            metrics['worst_companies']['Company 2']['response_rate'],
            0.0
        )

    def test_metrics_stored_in_database(self):
        """Test that metrics are stored in the database."""
        metrics = MetricsService.calculate_metrics(self.user)
        
        # Check that metrics were stored
        stored_metrics = ApplicationMetrics.objects.filter(user=self.user).first()
        self.assertIsNotNone(stored_metrics)
        self.assertEqual(stored_metrics.total_applications, 7)
        self.assertEqual(stored_metrics.response_rate, 57.14)
        self.assertEqual(stored_metrics.interview_rate, 42.86)
        self.assertEqual(stored_metrics.ghosted_rate, 28.57)
        self.assertEqual(stored_metrics.avg_response_time, 5.0)

    def test_empty_metrics(self):
        """Test metrics calculation with no applications."""
        # Create new user with no applications
        empty_user = User.objects.create_user(
            username='emptyuser',
            email='empty@example.com',
            password='testpass123'
        )

        metrics = MetricsService.calculate_metrics(empty_user)
        self.assertEqual(metrics['total_applications'], 0)
        self.assertEqual(metrics['response_rate'], 0.0)
        self.assertEqual(metrics['interview_rate'], 0.0)
        self.assertEqual(metrics['ghosted_rate'], 0.0)
        self.assertEqual(metrics['avg_response_time'], 0.0)
        self.assertEqual(metrics['best_companies'], {})
        self.assertEqual(metrics['worst_companies'], {})


class MetricsAPITests(TestCase):
    """Test cases for metrics API endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Setup API client
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Create some test applications
        self.base_time = timezone.now()
        Application.objects.create(
            user=self.user,
            applicant_name='Test Applicant',
            job_title='Software Engineer',
            company_name='Test Company',
            status='interviewed',
            created_at=self.base_time - timedelta(days=10),
            updated_at=self.base_time - timedelta(days=5)
        )

        # URL for metrics endpoint
        self.metrics_url = reverse('application-metrics')

    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        response = self.client.get(self.metrics_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 1)
        self.assertEqual(response.data['interview_rate'], 100.0)
        self.assertEqual(response.data['avg_response_time'], 5.0)

    def test_get_metrics_unauthenticated(self):
        """Test metrics endpoint with unauthenticated user."""
        self.client.credentials()
        response = self.client.get(self.metrics_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
