"""Filters for job applications."""

from django_filters import rest_framework as filters
from .models import Application


class ApplicationFilter(filters.FilterSet):
    """Filter for job applications.
    
    Provides filtering options for:
    - Company name (exact match or contains)
    - Job title (exact match or contains)
    - Status (exact match)
    - Date range (after/before specific dates)
    """
    
    company_name = filters.CharFilter(lookup_expr='icontains')
    job_title = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Application.STATUS_CHOICES)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Application
        fields = {
            'company_name': ['exact', 'icontains'],
            'job_title': ['exact', 'icontains'],
            'status': ['exact'],
            'created_at': ['gte', 'lte']
        }
