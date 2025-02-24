"""Serializers for job applications."""

from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications.
    
    This serializer handles the conversion between Application model instances
    and JSON representations, including validation and field type conversions.
    """

    class Meta:
        """Meta options for ApplicationSerializer."""
        model = Application
        fields = [
            'id',
            'user',
            'applicant_name',
            'job_title',
            'company_name',
            'status',
            'email_content',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_status(self, value):
        """Validate that the status is one of the allowed choices."""
        valid_statuses = dict(Application.STATUS_CHOICES).keys()
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value

    def create(self, validated_data):
        """Create and return a new Application instance."""
        return Application.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update and return an existing Application instance."""
        instance.applicant_name = validated_data.get('applicant_name', instance.applicant_name)
        instance.job_title = validated_data.get('job_title', instance.job_title)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.status = validated_data.get('status', instance.status)
        instance.email_content = validated_data.get('email_content', instance.email_content)
        instance.save()
        return instance
