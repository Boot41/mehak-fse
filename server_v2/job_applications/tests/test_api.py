"""Test cases for job application API endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Application

User = get_user_model()


class JobApplicationAPITestCase(APITestCase):
    """Base test case for job application API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        # Create test applications
        self.applications = [
            Application.objects.create(
                user=self.user1,
                applicant_name='John Doe',
                job_title='Software Engineer',
                company_name='Tech Corp',
                status='applied',
                email_content='Test application 1'
            ),
            Application.objects.create(
                user=self.user1,
                applicant_name='Jane Smith',
                job_title='Data Scientist',
                company_name='AI Corp',
                status='screening',
                email_content='Test application 2'
            ),
            Application.objects.create(
                user=self.user2,
                applicant_name='Bob Wilson',
                job_title='Product Manager',
                company_name='Product Corp',
                status='offer',
                email_content='Test application 3'
            )
        ]

        # Get tokens for authentication
        refresh = RefreshToken.for_user(self.user1)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # API endpoints
        self.list_create_url = '/api/applications/'
        self.valid_payload = {
            'applicant_name': 'Alice Brown',
            'job_title': 'Frontend Developer',
            'company_name': 'Web Corp',
            'status': 'applied',
            'email_content': 'Test application 4'
        }


class TestJobApplicationCreate(JobApplicationAPITestCase):
    """Test cases for creating job applications."""

    def test_create_valid_application(self):
        """Test creating a valid job application."""
        response = self.client.post(
            self.list_create_url,
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 4)
        self.assertEqual(
            Application.objects.get(id=response.data['id']).user,
            self.user1
        )

    def test_create_invalid_application(self):
        """Test creating an application with invalid data."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['status'] = 'invalid_status'
        response = self.client.post(
            self.list_create_url,
            invalid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 3)

    def test_create_application_unauthenticated(self):
        """Test creating an application without authentication."""
        self.client.credentials()  # Remove authentication
        response = self.client.post(
            self.list_create_url,
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Application.objects.count(), 3)


class TestJobApplicationList(JobApplicationAPITestCase):
    """Test cases for listing job applications."""

    def test_list_applications(self):
        """Test listing all applications for authenticated user."""
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only user1's applications

    def test_list_applications_unauthenticated(self):
        """Test listing applications without authentication."""
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_status(self):
        """Test filtering applications by status."""
        response = self.client.get(f'{self.list_create_url}?status=applied')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'applied')

    def test_filter_by_company(self):
        """Test filtering applications by company name."""
        response = self.client.get(
            f'{self.list_create_url}?company_name=Tech Corp'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['company_name'],
            'Tech Corp'
        )
