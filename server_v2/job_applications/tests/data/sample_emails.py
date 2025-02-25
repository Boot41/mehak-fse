"""Sample email data for testing."""

SAMPLE_HTML_EMAIL = """
<html>
<body>
<p>Name: Mike Brown</p>
<p>Position: Full Stack Developer</p>
<p>Company: Tech Solutions Inc</p>
<p>Skills: Python, React, Node.js, MongoDB</p>
<p>Next Steps: Technical interview scheduled for next Tuesday</p>
<p>Dear Hiring Manager,</p>
<p>I am writing to express my interest in the Full Stack Developer position at Tech Solutions Inc. 
I have extensive experience in full-stack development using Python, React, and Node.js.</p>
<p>Best regards,<br>Mike Brown</p>
</body>
</html>
"""

SAMPLE_PLAIN_TEXT_EMAIL = """
Name: John Smith
Position: Senior Software Engineer
Company: Tech Corp
Skills: Python, Java, AWS, REST APIs
Next Steps: Technical interview scheduled for next week

Dear Hiring Manager,

I am writing to express my interest in the Senior Software Engineer position at Tech Corp.
I have extensive experience in Python development and building REST APIs.

Best regards,
John Smith
"""

SAMPLE_COMPLEX_EMAIL = """
From: Sarah Johnson <sarah.j@email.com>
To: hiring@techcompany.com
Subject: Application for Data Science Position

Name: Sarah Johnson
Position: Senior Data Scientist
Company: Data Analytics Corp
Skills: Python, R, Machine Learning, TensorFlow, SQL, Big Data
Next Steps: Team interview scheduled for Friday

Dear Hiring Team,

I am excited to apply for the Senior Data Scientist position at Data Analytics Corp.
With my background in machine learning and big data analytics, I believe I would be
a great addition to your team.

Technical Skills:
- Advanced Python and R programming
- Machine Learning frameworks (TensorFlow, PyTorch)
- SQL and NoSQL databases
- Big Data technologies (Hadoop, Spark)
- Data visualization (Tableau, D3.js)

Education:
- Ph.D. in Computer Science
- M.S. in Data Science

Best regards,
Sarah Johnson
"""

SAMPLE_MINIMAL_EMAIL = """
Name: Alex Lee
Position: Junior Developer
Company: StartUp Tech
Skills: JavaScript
Next Steps: Phone screening

I'm interested in the Junior Developer position.
"""

SAMPLE_EDGE_CASE_EMAIL = """
RE: Job Application - Development Role
    
To whom it may concern,
    
This is regarding the open position. I have attached my resume.
    
Thanks
"""

SAMPLE_MULTI_PERSON_EMAIL = """
Team Lead: David Wilson
Team Members: Sarah Chen, Michael Rodriguez
Position: Senior Backend Engineer
Company: Enterprise Solutions Inc.
Required Skills: Go, Microservices, Kafka
    
Project team composition for the new backend service.
"""
