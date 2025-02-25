"""Models for job applications.

This module defines the database models for storing job application data.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class JobApplication(models.Model):
    """Model for tracking job applications."""

    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewing', 'Interviewing'),
        ('offer_received', 'Offer Received'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('withdrawn', 'Withdrawn'),
    ]

    STATUS_DICT = dict(STATUS_CHOICES)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_description = models.TextField(blank=True)
    application_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    last_updated = models.DateTimeField(auto_now=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    remote_option = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    
    class Meta:
        """Meta options for JobApplication model."""
        db_table = 'job_applications'
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['user', '-application_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        """String representation of the JobApplication."""
        return f"{self.company_name} - {self.position}"

    def clean(self):
        """Validate model fields."""
        if not self.company_name:
            raise ValidationError({'company_name': 'Company name is required'})
        if not self.position:
            raise ValidationError({'position': 'Position is required'})
        if self.status not in self.STATUS_DICT:
            raise ValidationError({
                'status': f'Invalid status. Must be one of: {", ".join(self.STATUS_DICT.keys())}'
            })


class Communication(models.Model):
    """Model for storing communication records."""

    COMMUNICATION_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('interview', 'Interview'),
        ('other', 'Other'),
    ]

    job_application = models.ForeignKey(JobApplication, related_name='communications', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    notes = models.TextField()
    follow_up_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        """Meta options for Communication model."""
        db_table = 'communications'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        """String representation of the Communication."""
        return f"{self.get_type_display()} on {self.date}"
