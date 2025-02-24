"""Service for calculating job application metrics.

This module provides functionality for analyzing job application data and calculating metrics.
"""

from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, FloatField
from django.db.models.functions import Cast

from job_applications.models import Application, ApplicationMetrics


class MetricsService:
    """Service class for calculating job application metrics."""

    @staticmethod
    def calculate_metrics(user) -> dict:
        """Calculate job application metrics for a user.

        Args:
            user: User instance to calculate metrics for.

        Returns:
            dict: Dictionary containing calculated metrics.
        """
        # Get all applications for the user
        applications = Application.objects.filter(user=user)
        total_applications = applications.count()

        if total_applications == 0:
            return {
                'total_applications': 0,
                'response_rate': 0.0,
                'interview_rate': 0.0,
                'ghosted_rate': 0.0,
                'avg_response_time': 0.0,
                'best_companies': {},
                'worst_companies': {}
            }

        # Count applications by status
        responded = applications.exclude(status__in=['applied', 'ghosted']).count()
        interviewed = applications.filter(status='interviewed').count()
        ghosted = applications.filter(status='ghosted').count()

        # Calculate rates
        response_rate = round((responded / total_applications) * 100, 2)
        interview_rate = round((interviewed / total_applications) * 100, 2)
        ghosted_rate = round((ghosted / total_applications) * 100, 2)

        # Calculate average response time
        responded_apps = applications.exclude(
            status__in=['applied', 'ghosted']
        ).exclude(updated_at=None)
        total_days = 0
        count = 0
        for app in responded_apps:
            days = (app.updated_at - app.created_at).days
            if days >= 0:  # Only count positive days
                total_days += days
                count += 1
        avg_response_time = round(total_days / count if count > 0 else 0.0, 2)

        # Calculate company response rates
        company_stats = defaultdict(lambda: {'total': 0, 'responded': 0})
        for app in applications:
            company = app.company_name
            company_stats[company]['total'] += 1
            if app.status not in ['applied', 'ghosted']:
                company_stats[company]['responded'] += 1

        # Convert to response rates and sort
        company_rates = {
            company: {
                'response_rate': round((stats['responded'] / stats['total']) * 100, 2),
                'total_applications': stats['total']
            }
            for company, stats in company_stats.items()
            if stats['total'] >= 2  # Only consider companies with at least 2 applications
        }
        sorted_companies = sorted(
            company_rates.items(),
            key=lambda x: x[1]['response_rate'],
            reverse=True
        )

        # Get top 3 and bottom 3 companies
        best_companies = dict(sorted_companies[:3]) if sorted_companies else {}
        worst_companies = dict(sorted_companies[-3:]) if sorted_companies else {}

        metrics = {
            'total_applications': total_applications,
            'response_rate': response_rate,
            'interview_rate': interview_rate,
            'ghosted_rate': ghosted_rate,
            'avg_response_time': avg_response_time,
            'best_companies': best_companies,
            'worst_companies': worst_companies
        }

        # Store metrics in database
        ApplicationMetrics.objects.create(
            user=user,
            total_applications=total_applications,
            response_rate=response_rate,
            interview_rate=interview_rate,
            ghosted_rate=ghosted_rate,
            avg_response_time=avg_response_time,
            best_companies=best_companies,
            worst_companies=worst_companies
        )

        return metrics
