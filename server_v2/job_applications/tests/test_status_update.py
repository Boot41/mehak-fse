"""Test cases for job application status updates."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from job_applications.models import Application

User = get_user_model()


class ApplicationStatusUpdateTests(TestCase):
    """Test cases for updating job application status."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test application
        self.application = Application.objects.create(
            user=self.user,
            applicant_name='John Doe',
            job_title='Software Engineer',
            company_name='Tech Corp',
            status='applied',
            email_content='Test application email'
        )
        
        # Set up API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URL for updating application
        self.url = reverse('application-detail', args=[self.application.id])

    def test_valid_status_update(self):
        """Test updating status with a valid value."""
        data = {'status': 'interviewed'}
        response = self.client.patch(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'interviewed')
        
        # Verify database was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'interviewed')

    def test_invalid_status_value(self):
        """Test updating status with an invalid value."""
        data = {'status': 'invalid_status'}
        response = self.client.patch(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data['error']['message'])
        
        # Verify database was not updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')

    def test_multiple_field_update(self):
        """Test updating status along with other fields."""
        data = {
            'status': 'interviewed',
            'job_title': 'Senior Engineer'
        }
        response = self.client.patch(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'interviewed')
        self.assertEqual(response.data['job_title'], 'Senior Engineer')
        
        # Verify database was updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'interviewed')
        self.assertEqual(self.application.job_title, 'Senior Engineer')

    def test_unauthorized_status_update(self):
        """Test updating status without authentication."""
        # Create new client without authentication
        client = APIClient()
        data = {'status': 'interviewed'}
        response = client.patch(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify database was not updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')

    def test_wrong_user_status_update(self):
        """Test updating status of another user's application."""
        # Create another user and authenticate as them
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        data = {'status': 'interviewed'}
        response = self.client.patch(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify database was not updated
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')

    def test_all_valid_status_transitions(self):
        """Test all valid status transitions."""
        valid_statuses = dict(Application.STATUS_CHOICES).keys()
        
        for new_status in valid_statuses:
            data = {'status': new_status}
            response = self.client.patch(self.url, data)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], new_status)
            
            # Verify database was updated
            self.application.refresh_from_db()
            self.assertEqual(self.application.status, new_status)
