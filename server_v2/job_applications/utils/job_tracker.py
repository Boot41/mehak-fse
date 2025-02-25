"""Utility module for tracking job applications."""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from ..models import JobApplication

class JobTracker:
    """Class for tracking job applications."""

    def __init__(self, user):
        """Initialize with a user.
        
        Args:
            user: User instance to track applications for.
        """
        self.user = user

    def get_application_stats(self):
        """Get statistics for the user's job applications.
        
        Returns:
            dict: Dictionary containing application statistics.
        """
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        
        # Get all applications for the user
        applications = JobApplication.objects.filter(user=self.user)
        total_applications = applications.count()
        
        # Get recent applications
        recent_applications = applications.filter(application_date__gte=thirty_days_ago)
        
        # Calculate statistics
        stats = {
            'total_applications': total_applications,
            'applications_last_30_days': recent_applications.count(),
            'applications_last_7_days': applications.filter(
                application_date__gte=seven_days_ago
            ).count(),
            'status_breakdown': dict(
                applications.values_list('status').annotate(count=Count('id'))
            ),
            'recent_status_breakdown': dict(
                recent_applications.values_list('status').annotate(count=Count('id'))
            ),
            'interview_rate': 0.0,
            'offer_rate': 0.0,
            'response_rate': 0.0,
            'ghosted_applications': applications.filter(
                status='applied',
                application_date__lte=thirty_days_ago
            ).count()
        }
        
        # Calculate rates if there are applications
        if total_applications > 0:
            interviewed = applications.filter(
                status__in=['interview_scheduled', 'interviewing']
            ).count()
            offers = applications.filter(status='offer_received').count()
            responses = applications.exclude(status='applied').count()
            
            stats.update({
                'interview_rate': round(interviewed / total_applications * 100, 1),
                'offer_rate': round(offers / total_applications * 100, 1),
                'response_rate': round(responses / total_applications * 100, 1)
            })
        
        return stats

    def get_follow_up_reminders(self):
        """Get follow-up reminders for applications.
        
        Returns:
            list: List of applications needing follow-up.
        """
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        
        # Get applications that might need follow-up
        reminders = []
        
        # Applications with no response for 7+ days
        no_response = JobApplication.objects.filter(
            user=self.user,
            status='applied',
            application_date__lte=seven_days_ago
        )
        for app in no_response:
            reminders.append({
                'id': app.id,
                'company': app.company_name,
                'position': app.position,
                'type': 'no_response',
                'days_since_application': (today - app.application_date).days
            })
        
        # Applications with upcoming interviews
        upcoming_interviews = JobApplication.objects.filter(
            user=self.user,
            status='interview_scheduled'
        )
        for app in upcoming_interviews:
            if app.next_follow_up and app.next_follow_up > today:
                reminders.append({
                    'id': app.id,
                    'company': app.company_name,
                    'position': app.position,
                    'type': 'upcoming_interview',
                    'interview_date': app.next_follow_up
                })
        
        # Applications with recent interviews needing follow-up
        recent_interviews = JobApplication.objects.filter(
            user=self.user,
            status='interviewing',
            last_updated__lte=seven_days_ago
        )
        for app in recent_interviews:
            reminders.append({
                'id': app.id,
                'company': app.company_name,
                'position': app.position,
                'type': 'post_interview_followup',
                'days_since_interview': (today - app.last_updated).days
            })
        
        return reminders

    def update_application_status(self, application_id, new_status, notes=None):
        """Update the status of a job application.
        
        Args:
            application_id: ID of the application to update.
            new_status: New status to set.
            notes: Optional notes about the status change.
            
        Returns:
            tuple: (success, message)
        """
        try:
            application = JobApplication.objects.get(id=application_id)
            
            # Validate the new status
            if new_status not in JobApplication.STATUS_DICT:
                return False, f"Invalid status. Must be one of: {', '.join(JobApplication.STATUS_DICT.keys())}"
            
            # Update the application
            application.status = new_status
            if notes:
                application.notes = notes
            application.last_updated = timezone.now()
            application.save()
            
            return True, "Status updated successfully"
            
        except JobApplication.DoesNotExist:
            return False, "Application not found"
        except Exception as e:
            return False, str(e)
