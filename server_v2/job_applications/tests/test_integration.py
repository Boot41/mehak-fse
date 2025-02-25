"""Integration tests for job applications."""

from django.test import TestCase, AsyncClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import JobApplication, Communication
from ..utils.job_tracker import JobTracker
import pytest
import json

User = get_user_model()

class JobApplicationIntegrationTests(TestCase):
    """Integration tests for job applications."""

    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        self.async_client = AsyncClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test applications with different dates and statuses
        self.applications = []
        statuses = ['applied', 'interview_scheduled', 'interviewing', 'offer_received', 'rejected']
        dates = [
            timezone.now(),
            timezone.now() - timedelta(days=5),
            timezone.now() - timedelta(days=15),
            timezone.now() - timedelta(days=25),
            timezone.now() - timedelta(days=35)
        ]
        
        for i, (status, date) in enumerate(zip(statuses, dates)):
            app = JobApplication.objects.create(
                user=self.user,
                position=f'Software Engineer {i}',
                company_name=f'Tech Corp {i}',
                job_description=f'Job description {i}',
                status=status,
                application_date=date,
                last_updated=date,
                location=f'Location {i}',
                remote_option=i % 2 == 0,
                url=f'https://example.com/job/{i}'
            )
            self.applications.append(app)
        
        # Set up API endpoints
        self.list_url = reverse('job-application-list')
        self.detail_url = reverse('job-application-detail', args=[self.applications[0].id])
        self.stats_url = reverse('job-application-stats', args=[])
        self.reminders_url = reverse('job-application-reminders', args=[])

    def test_list_job_applications(self):
        """Test retrieving list of job applications."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_filter_by_status(self):
        """Test filtering applications by status."""
        response = self.client.get(f"{self.list_url}?status=applied")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'applied')

    def test_filter_by_date_range(self):
        """Test filtering applications by date range."""
        start_date = (timezone.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        response = self.client.get(
            f"{self.list_url}?start_date={start_date}&end_date={end_date}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_search_applications(self):
        """Test searching applications."""
        response = self.client.get(f"{self.list_url}?search=Tech Corp 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], 'Tech Corp 1')

    def test_application_stats(self):
        """Test getting application statistics."""
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data
        self.assertEqual(stats['total_applications'], 5)
        self.assertEqual(stats['applications_last_30_days'], 4)
        self.assertEqual(stats['applications_last_7_days'], 2)
        
        # Verify rates
        self.assertEqual(stats['interview_rate'], 40.0)  # 2 out of 5 in interview stages
        self.assertEqual(stats['offer_rate'], 20.0)     # 1 out of 5 with offer
        self.assertEqual(stats['response_rate'], 80.0)  # 4 out of 5 with response

    def test_follow_up_reminders(self):
        """Test getting follow-up reminders."""
        # Create an application that needs follow-up
        old_app = JobApplication.objects.create(
            user=self.user,
            position='Senior Developer',
            company_name='Old Corp',
            status='applied',
            application_date=timezone.now() - timedelta(days=10),
            last_updated=timezone.now() - timedelta(days=10)
        )
        
        response = self.client.get(self.reminders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(
            any(reminder['id'] == old_app.id for reminder in response.data)
        )

    def test_add_communication(self):
        """Test adding communication to an application."""
        app = self.applications[0]
        url = reverse('job-application-add-communication', args=[app.id])
        
        data = {
            'type': 'email',
            'notes': 'Test communication',
            'date': timezone.now().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify communication was added
        app.refresh_from_db()
        self.assertEqual(app.communications.count(), 1)
        self.assertEqual(app.communications.first().notes, 'Test communication')

    def test_update_status_with_notes(self):
        """Test updating application status with notes."""
        app = self.applications[0]
        url = reverse('job-application-update-status', args=[app.id])
        
        data = {
            'status': 'interviewing',
            'notes': 'Moving to interview stage'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status and notes were updated
        app.refresh_from_db()
        self.assertEqual(app.status, 'interviewing')
        self.assertEqual(app.notes, 'Moving to interview stage')

    def test_parse_email(self):
        """Test parsing email content."""
        app = self.applications[0]
        url = reverse('job-application-parse-email', args=[app.id])
        
        data = {
            'email_body': '''
            Dear John,
            
            Thank you for applying to the Software Engineer position at Tech Corp.
            We would like to schedule an interview with you.
            
            Best regards,
            HR Team
            ''',
            'email_subject': 'Interview Request - Software Engineer Position'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('position', response.data)
        self.assertIn('company_name', response.data)

    def test_authentication_required(self):
        """Test that authentication is required for all endpoints."""
        self.client.force_authenticate(user=None)
        
        # Test all endpoints
        endpoints = [
            self.list_url,
            self.detail_url,
            self.stats_url,
            self.reminders_url
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {endpoint} should require authentication"
            )
