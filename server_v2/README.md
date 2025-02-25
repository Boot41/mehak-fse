# Job Application Manager

A Django-based API for managing job applications, with automated email parsing and data extraction.

## Features

- Parse job application emails from Gmail
- Extract key information like applicant name, job title, and company
- Store and manage job applications
- RESTful API for accessing application data
- Admin interface for easy management

## Project Structure

```
server/
├── backend/              # Project configuration
│   ├── settings.py      # Django settings
│   └── urls.py          # Main URL routing
├── gmail/               # Gmail integration
│   ├── auth.py         # Gmail API authentication
│   ├── email.py        # Email fetching
│   └── parser.py       # Job application parsing
├── job_applications/    # Main application
│   ├── models.py       # Database models
│   ├── views.py        # API endpoints
│   ├── serializers.py  # API serializers
│   ├── admin.py        # Admin interface
│   └── urls.py         # URL routing
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Gmail API:
   - Place `credentials.json` in the project root
   - Run the application to complete OAuth2 flow

3. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Job Applications

- `GET /api/job_applications/applications/`
  - List job applications
  - Query parameters:
    - `search`: Search term
    - `start_date`: Filter by start date (YYYY-MM-DD)
    - `end_date`: Filter by end date (YYYY-MM-DD)
    - `sort`: Sort field (created_at, applicant_name, job_title, company_name)
    - `order`: Sort order (asc, desc)

- `POST /api/job_applications/applications/`
  - Create job applications from emails
  - Request body:
    ```json
    {
        "email_query": "subject:Application",
        "max_results": 10
    }
    ```

## Admin Interface

Access the admin interface at `/admin` to:
- View and manage job applications
- Monitor application processing
- Track confidence scores

## Dependencies

- Django
- Django REST Framework
- Google API Python Client
- BeautifulSoup4

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   python manage.py test
   ```

3. Check code style:
   ```bash
   flake8
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
