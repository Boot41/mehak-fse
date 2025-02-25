"""Admin interface for job applications.

This module configures the Django admin interface for managing job applications.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import JobApplication, Communication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Admin interface for job applications."""

    # List display configuration
    list_display = (
        'company_name',
        'position',
        'status',
        'application_date',
        'last_updated'
    )
    list_filter = (
        'status',
        'application_date',
        'remote_option'
    )
    search_fields = (
        'company_name',
        'position',
        'notes'
    )
    date_hierarchy = 'application_date'
    ordering = ('-application_date',)

    # Detail view configuration
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'company_name',
                'position',
                'status',
                'application_date',
                'last_updated'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'remote_option',
                'job_description',
                'salary_range',
                'location',
                'source',
                'url'
            )
        })
    )
    readonly_fields = (
        'application_date',
        'last_updated'
    )

    # Actions configuration
    actions = ['mark_as_interviewed', 'mark_as_rejected', 'mark_as_accepted']

    def mark_as_interviewed(self, request, queryset):
        """Mark selected applications as interviewed."""
        queryset.update(status='interviewing')
        self.message_user(request, f'Successfully marked {queryset.count()} application(s) as interviewing')

    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected."""
        queryset.update(status='rejected')
        self.message_user(request, f'Successfully marked {queryset.count()} application(s) as rejected')

    def mark_as_accepted(self, request, queryset):
        """Mark selected applications as accepted."""
        queryset.update(status='accepted')
        self.message_user(request, f'Successfully marked {queryset.count()} application(s) as accepted')

    # Action descriptions
    mark_as_interviewed.short_description = "Mark as interviewed"
    mark_as_rejected.short_description = "Mark as rejected"
    mark_as_accepted.short_description = "Mark as accepted"


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    """Admin interface for communications."""

    # List display configuration
    list_display = (
        'job_application',
        'type',
        'date',
        'follow_up_date'
    )
    list_filter = (
        'type',
        'date'
    )
    search_fields = (
        'notes',
        'job_application__company_name'
    )
    date_hierarchy = 'date'
    ordering = ('-date',)

    # Detail view configuration
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'job_application',
                'type',
                'date',
                'follow_up_date'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',)
        })
    )
    readonly_fields = (
        'date',
    )
