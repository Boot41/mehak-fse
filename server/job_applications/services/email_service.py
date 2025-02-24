"""Email service for sending follow-up emails.

This module provides functionality for sending follow-up emails using Gmail API or SMTP.
"""

import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.core.mail import send_mail
from django.conf import settings

from job_applications.models import Application


class EmailService:
    """Service class for handling email operations."""

    @staticmethod
    def send_follow_up_email(application_id: str, user_credentials: dict) -> dict:
        """Send a follow-up email for a job application.

        Args:
            application_id: ID of the job application.
            user_credentials: Gmail API credentials.

        Returns:
            dict: Response containing success status and message.
        """
        try:
            # Convert application_id to int if it's a string
            app_id = int(application_id) if isinstance(application_id, str) else application_id
            
            # Get application
            application = Application.objects.get(id=app_id)
            
            # Generate email content
            email_content = EmailService._generate_follow_up_content(application)
            
            # Try Gmail API first
            try:
                result = EmailService._send_via_gmail_api(
                    from_email=application.user.email,
                    subject=f'Follow-up: {application.job_title} at {application.company_name}',
                    body=email_content,
                    credentials=user_credentials
                )
                return result
            except Exception as e:
                # If Gmail API fails, try SMTP
                result = EmailService._send_via_smtp(
                    to_email=application.user.email,  
                    subject=f'Follow-up: {application.job_title} at {application.company_name}',
                    body=email_content
                )
                return result
        
        except (Application.DoesNotExist, ValueError):
            return {'success': False, 'message': 'Application not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def _generate_follow_up_content(application: Application) -> str:
        """Generate follow-up email content.

        Args:
            application: Job application instance.

        Returns:
            str: Generated email content.
        """
        return f"""Dear Hiring Manager,

I hope this email finds you well. I am writing to follow up on my application for the {application.job_title} position at {application.company_name}. I submitted my application on {application.created_at.strftime('%B %d, %Y')}.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills and experience align with your needs.

Best regards,
{application.applicant_name}"""

    @staticmethod
    def _send_via_gmail_api(from_email: str, subject: str, body: str, credentials: dict) -> dict:
        """Send email using Gmail API.

        Args:
            from_email: Sender's email address.
            subject: Email subject.
            body: Email body content.
            credentials: Gmail API credentials.

        Returns:
            dict: Response containing success status and message.
        """
        try:
            # Create Gmail API service
            creds = Credentials.from_authorized_user_info(credentials)
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = MIMEText(body)
            message['to'] = from_email
            message['from'] = from_email
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Create message body
            body = {'raw': raw_message}
            
            # Send message
            service.users().messages().send(
                userId='me',
                body=body
            ).execute()
            
            return {
                'success': True,
                'message': 'Email sent successfully via Gmail API'
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Gmail API error: {str(e)}'}

    @staticmethod
    def _send_via_smtp(to_email: str, subject: str, body: str) -> dict:
        """Send email using SMTP.

        Args:
            to_email: Recipient's email address.
            subject: Email subject.
            body: Email body content.

        Returns:
            dict: Response containing success status and message.
        """
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email],
                fail_silently=False
            )
            
            return {
                'success': True,
                'message': 'Email sent successfully via SMTP'
            }
        
        except Exception as e:
            return {'success': False, 'message': f'SMTP error: {str(e)}'}
