"""Admin interface for job applications.

This module configures the Django admin interface for managing job applications.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import Application
from .services.email_service import EmailService


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for job applications."""

    # List display configuration
    list_display = (
        'applicant_name',
        'job_title',
        'company_name',
        'status',
        'created_at',
        'updated_at'
    )
    list_filter = (
        'company_name',
        'status',
        'created_at'
    )
    search_fields = (
        'applicant_name',
        'job_title',
        'company_name',
        'email_content'
    )
    ordering = ['-created_at']

    # Detail view configuration
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'applicant_name',
                'job_title',
                'company_name'
            )
        }),
        ('Application Details', {
            'fields': (
                'email_content',
                'status'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    readonly_fields = (
        'created_at',
        'updated_at'
    )

    # Actions configuration
    actions = ['send_follow_up_email', 'mark_as_interviewed', 'mark_as_rejected', 'mark_as_accepted']

    def send_follow_up_email(self, request, queryset):
        """Send follow-up emails for selected applications."""
        success_count = 0
        for application in queryset:
            try:
                if not application.user.gmail_credentials:
                    messages.error(request, f'Gmail credentials not found for {application.applicant_name}')
                    continue

                result = EmailService.send_follow_up_email(
                    application_id=str(application.id),
                    user_credentials=application.user.gmail_credentials
                )
                if result.get('success'):
                    success_count += 1
                else:
                    messages.error(request, f'Failed to send email for {application.applicant_name}: {result.get("message")}')
            except Exception as e:
                messages.error(request, f'Error sending email for {application.applicant_name}: {str(e)}')

        if success_count:
            messages.success(request, f'Successfully sent {success_count} follow-up email(s)')

    def mark_as_interviewed(self, request, queryset):
        """Mark selected applications as interviewed."""
        queryset.update(status='interviewed')
        count = queryset.count()
        messages.success(request, f'Successfully marked {count} application(s) as interviewed')

    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected."""
        queryset.update(status='rejected')
        count = queryset.count()
        messages.success(request, f'Successfully marked {count} application(s) as rejected')

    def mark_as_accepted(self, request, queryset):
        """Mark selected applications as accepted."""
        queryset.update(status='accepted')
        count = queryset.count()
        messages.success(request, f'Successfully marked {count} application(s) as accepted')

    # Action descriptions
    send_follow_up_email.short_description = "Send follow-up emails"
    mark_as_interviewed.short_description = "Mark as interviewed"
    mark_as_rejected.short_description = "Mark as rejected"
    mark_as_accepted.short_description = "Mark as accepted"
