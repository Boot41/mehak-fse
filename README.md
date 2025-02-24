# **AI Job Application Email Summarizer & Ghosting Tracker**  

Welcome to the **AI Job Application Email Summarizer & Ghosting Tracker**! This project is designed to help job seekers streamline their job application process by automatically summarizing job application emails, tracking application statuses, detecting ghosting, and providing AI-powered follow-up recommendations.

---

## **✨ Key Features**  

### **1. Email Summarization**  
- Automatically fetches job application emails from **Gmail/Outlook**.  
- Uses **AI (spaCy/OpenAI API)** to extract key details:  
  - **Applicant Name**  
  - **Job Title**  
  - **Company Name**  
  - **Key Skills/Qualifications**  
  - **Call to Action (Next Steps)**  

### **2. Application Tracking**  
- Tracks the status of each job application:  
  - **Applied**  
  - **Interview Scheduled**  
  - **Ghosted**  
  - **Closed**  
- Provides a **dashboard** to view all applications in one place.  

### **3. Ghosting Detection**  
- Detects if a job application has been **ghosted** by:  
  - Checking if the job listing **still exists** (via web scraping).  
  - Tracking the **time elapsed** since the last response.  
- Sends **alerts** for ghosted applications.  

### **4. AI-Powered Follow-Up Recommendations**  
- Generates **personalized follow-up emails** using **OpenAI API**.  
- Provides **one-click sending** for follow-ups.  

### **5. Job Success Insights**  
- Tracks **which companies respond the most**.  
- Shows **which job applications have the highest success rate**.  

---

## **🛠️ Tech Stack**  

### **Frontend**  
- **React** (with **Tailwind CSS** for styling).  
- **Axios** for API calls.  

### **Backend**  
- **Django** (Python) for the backend API.  
- **PostgreSQL** for database storage.  

### **AI/ML**  
- **spaCy** for text processing.  
- **OpenAI API** for summarization and follow-up email generation.  

### **DevOps**  
- **Docker** for containerization.  
- **GitHub** for version control.  

---

## **🚀 Deployment Guide**  

### **Prerequisites**  

- Docker
- Docker Compose
- Git

### **Setup Instructions**  

1. Clone the repository:
```bash
git clone https://github.com/your-username/ai-job-application-tracker.git
cd ai-job-application-tracker
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update the `.env` file with your settings:
- Generate a secure `SECRET_KEY`
- Set strong database passwords
- Update `DJANGO_ALLOWED_HOSTS` if needed
- Configure other environment variables

4. Build and start the containers:
```bash
docker compose build
docker compose up -d
```

5. Initialize the database:
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### **Project Structure**  

```
ai-job-application-tracker/
├── backend/             # Django backend
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── Dockerfile
│   └── package.json
├── nginx/              # Nginx configuration
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

### **Services**  

- Frontend: http://localhost:3000
- Backend API: http://localhost/api
- Django Admin: http://localhost/admin
- Database: PostgreSQL (Internal)

### **Maintenance**  

- View logs:
```bash
docker compose logs -f
```

- Restart services:
```bash
docker compose restart
```

- Stop all services:
```bash
docker compose down
```

- Remove all data (including database):
```bash
docker compose down -v
```

### **Security Notes**  

1. Never commit the `.env` file
2. Regularly update dependencies
3. Use strong passwords
4. Keep Docker and all packages updated

### **Troubleshooting**  

1. If the frontend can't connect to the backend:
   - Check if the `VITE_API_URL` is correctly set
   - Verify nginx configuration

2. If the backend can't connect to the database:
   - Check database credentials in `.env`
   - Verify database container is running

3. For permission issues:
   - Check file ownership in volumes
   - Verify user permissions in Dockerfiles

---

## **📂 Project Structure**  

```  
ai-job-application-tracker/  
├── backend/                  # Django backend  
│   ├── manage.py  
│   ├── requirements.txt  
│   ├── Dockerfile  
│   └── ...  
├── frontend/                 # React frontend  
│   ├── src/  
│   ├── public/  
│   ├── package.json  
│   ├── Dockerfile  
│   └── ...  
├── docker-compose.yml        # Docker configuration  
└── README.md  
```  

---

## **🔧 Configuration**  

### **Environment Variables**  
Create a `.env` file in the `backend` folder with the following variables:  

```  
# Django  
SECRET_KEY=your-secret-key  
DEBUG=True  
DATABASE_URL=postgres://user:password@db:5432/jobtracker  

# Email API  
GMAIL_API_KEY=your-gmail-api-key  
OUTLOOK_API_KEY=your-outlook-api-key  

# OpenAI API  
OPENAI_API_KEY=your-openai-api-key  
```  

---

## **📈 Future Enhancements**  
- **Multi-platform integration** (LinkedIn, Indeed tracking).  
- **Success prediction** using advanced AI models.  
- **Refined job insights & analytics**.  
- **Mobile app** for on-the-go tracking.  

---

## **🚀 Setup Instructions**  

### **1. Google OAuth Setup**  

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)  
2. Create a new project or select an existing one  
3. Enable the Gmail API for your project  
4. Configure the OAuth consent screen:  
   - Set the application type to "Web application"  
   - Add authorized domains  
   - Add scopes for Gmail API  
5. Create OAuth 2.0 credentials:  
   - Create a new OAuth client ID  
   - Set application type to "Web application"  
   - Add authorized redirect URIs:  
     - `http://localhost:3000/auth/callback` (for development)  
6. Download the client configuration file  
7. Save it as `client_secret.json` in the `server` directory  

### **2. Backend Setup**  

1. Install Python dependencies:  
```bash  
cd server  
pip install -r requirements.txt  
```  

2. Apply database migrations:  
```bash  
python manage.py migrate  
```  

3. Start the Django development server:  
```bash  
python manage.py runserver  
```  

### **3. Frontend Setup**  

1. Install Node.js dependencies:  
```bash  
cd client  
npm install  
```  

2. Start the React development server:  
```bash  
npm start  
```  

### **4. Using Docker (Optional)**  

To run the entire application using Docker:  

```bash  
docker compose up --build  
```  

---

## **📈 Troubleshooting Guide**  

### **Common Issues**  

1. 404 Not Found for /api/auth/login/:  
   - Ensure Django server is running  
   - Check URL configuration in `urls.py`  

2. OAuth Errors:  
   - Verify `client_secret.json` is properly configured  
   - Check redirect URIs match exactly  
   - Ensure Gmail API is enabled in Google Cloud Console  

3. CORS Issues:  
   - Check CORS settings in Django  
   - Verify frontend URL is allowed  

---

## **🙏 Contributing**  
Contributions are welcome! Please fork the repository and submit a pull request.  

Happy job hunting! 🚀