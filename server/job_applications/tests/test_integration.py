"""Integration tests for job applications."""

from django.test import TestCase, AsyncClient
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from ..models import JobApplication
import pytest

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
        
        # Create test application
        self.application = JobApplication.objects.create(
            user=self.user,
            applicant_name='John Doe',
            position='Software Engineer',
            company='Tech Corp',
            skills=['Python', 'Django'],
            next_steps='Technical Interview',
            status='new'
        )
        
        # Set up API endpoints
        self.list_url = reverse('job-application-list')
        self.detail_url = reverse('job-application-detail', args=[self.application.id])
        self.process_emails_url = reverse('job-application-process-emails')
        self.update_status_url = reverse('job-application-update-status', args=[self.application.id])

    def test_list_job_applications(self):
        """Test retrieving list of job applications."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['applicant_name'], 'John Doe')

    def test_filter_job_applications(self):
        """Test filtering job applications."""
        response = self.client.get(f"{self.list_url}?status=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['status'], 'new')

    def test_update_job_application_status(self):
        """Test updating job application status."""
        response = self.client.patch(self.update_status_url, {'status': 'interviewed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'interviewed')

    @pytest.mark.asyncio
    async def test_process_emails(self):
        """Test successful email processing."""
        credentials = {
            'token': 'test_token',
            'refresh_token': 'test_refresh_token',
            'token_uri': 'test_token_uri',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.readonly']
        }
        
        response = await self.async_client.post(
            self.process_emails_url,
            {
                'email_query': 'subject:job application',
                'max_results': 10,
                'credentials': credentials
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @pytest.mark.asyncio
    async def test_process_emails_error_handling(self):
        """Test error handling during email processing."""
        response = await self.async_client.post(
            self.process_emails_url,
            {
                'email_query': 'subject:job application',
                'max_results': -1,
                'credentials': {}
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_required(self):
        """Test that authentication is required for API access."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            self.process_emails_url,
            {
                'email_query': 'subject:job application',
                'max_results': 10,
                'credentials': {}
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
