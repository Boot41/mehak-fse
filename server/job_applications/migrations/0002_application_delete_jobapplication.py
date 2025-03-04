# Generated by Django 5.1.6 on 2025-02-23 12:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_applications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant_name', models.CharField(help_text='Name of the job applicant', max_length=255)),
                ('job_title', models.CharField(help_text='Title of the job position', max_length=255)),
                ('company_name', models.CharField(help_text='Name of the company', max_length=255)),
                ('status', models.CharField(choices=[('applied', 'Applied'), ('screening', 'Screening'), ('interviewed', 'Interviewed'), ('offer', 'Offer Received'), ('accepted', 'Offer Accepted'), ('rejected', 'Rejected'), ('ghosted', 'No Response')], default='applied', help_text='Current status of the application', max_length=50)),
                ('email_content', models.TextField(blank=True, help_text='Original email content related to the application', null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Timestamp when the application was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the application was last updated')),
            ],
            options={
                'db_table': 'applications',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['status'], name='application_status_e61111_idx'), models.Index(fields=['company_name'], name='application_company_c9f199_idx'), models.Index(fields=['created_at'], name='application_created_a07231_idx')],
            },
        ),
        migrations.DeleteModel(
            name='JobApplication',
        ),
    ]
