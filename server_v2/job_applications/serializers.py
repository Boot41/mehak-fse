"""Serializers for job applications."""

from rest_framework import serializers
from .models import JobApplication, Communication


class CommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta options for CommunicationSerializer."""
        model = Communication
        fields = [
            'id',
            'type',
            'date',
            'notes',
            'follow_up_date'
        ]
        read_only_fields = ['id', 'date']


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications.
    
    This serializer handles the conversion between JobApplication model instances
    and JSON representations, including validation and field type conversions.
    """
    communications = CommunicationSerializer(many=True, read_only=True)
    
    class Meta:
        """Meta options for JobApplicationSerializer."""
        model = JobApplication
        fields = [
            'id',
            'company_name',
            'position',
            'job_description',
            'application_date',
            'status',
            'last_updated',
            'next_follow_up',
            'notes',
            'salary_range',
            'location',
            'remote_option',
            'source',
            'url',
            'communications'
        ]
        read_only_fields = ['id', 'last_updated', 'application_date']
