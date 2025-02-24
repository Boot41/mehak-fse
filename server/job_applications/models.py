"""Models for job applications.

This module defines the database models for storing job application data.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Application(models.Model):
    """Model for tracking job applications."""

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interviewed', 'Interviewed'),
        ('offer', 'Offer Received'),
        ('accepted', 'Offer Accepted'),
        ('rejected', 'Rejected'),
        ('ghosted', 'No Response'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="User who owns this application"
    )
    applicant_name = models.CharField(
        max_length=255,
        help_text="Name of the job applicant"
    )
    job_title = models.CharField(
        max_length=255,
        help_text="Title of the job position"
    )
    company_name = models.CharField(
        max_length=255,
        help_text="Name of the company"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='applied',
        help_text="Current status of the application"
    )
    email_content = models.TextField(
        null=True,
        blank=True,
        help_text="Original email content related to the application"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the application was created",
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the application was last updated",
        db_index=True
    )

    class Meta:
        """Meta options for Application model."""
        db_table = 'applications'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['company_name']),
            models.Index(fields=['user', 'company_name', 'job_title']),
            models.Index(fields=['user', 'status']),
        ]
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'company_name', 'job_title'],
                name='unique_user_application'
            )
        ]

    def __str__(self):
        """String representation of the Application."""
        return f"{self.applicant_name} - {self.job_title} at {self.company_name}"

    def clean(self):
        """Validate model fields."""
        if not self.applicant_name:
            raise ValidationError({'applicant_name': 'Applicant name is required'})
        if not self.job_title:
            raise ValidationError({'job_title': 'Job title is required'})
        if not self.company_name:
            raise ValidationError({'company_name': 'Company name is required'})
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError({
                'status': f'Invalid status. Must be one of: {", ".join(dict(self.STATUS_CHOICES).keys())}'
            })

    def save(self, *args, **kwargs):
        """Save the application after validation."""
        self.clean()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class ApplicationMetrics(models.Model):
    """Model for storing historical job application metrics."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='application_metrics',
        help_text="User who owns these metrics"
    )
    total_applications = models.IntegerField(
        default=0,
        help_text="Total number of applications sent"
    )
    response_rate = models.FloatField(
        default=0.0,
        help_text="Percentage of applications that received a response"
    )
    interview_rate = models.FloatField(
        default=0.0,
        help_text="Percentage of applications that led to interviews"
    )
    ghosted_rate = models.FloatField(
        default=0.0,
        help_text="Percentage of applications with no response"
    )
    avg_response_time = models.FloatField(
        default=0.0,
        help_text="Average number of days to receive a response"
    )
    best_companies = models.JSONField(
        default=dict,
        help_text="Companies with highest response rates"
    )
    worst_companies = models.JSONField(
        default=dict,
        help_text="Companies with lowest response rates"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when these metrics were calculated"
    )

    class Meta:
        """Meta options for ApplicationMetrics model."""
        db_table = 'application_metrics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """String representation of the ApplicationMetrics."""
        return f"Metrics for {self.user.username} at {self.created_at}"
