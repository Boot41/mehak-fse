-- Create user and database
CREATE USER job_tracker_user WITH PASSWORD 'development_password_only';
ALTER USER job_tracker_user WITH CREATEDB;
CREATE DATABASE job_tracker_db;
GRANT ALL PRIVILEGES ON DATABASE job_tracker_db TO job_tracker_user;

-- Connect to the job_tracker_db
\c job_tracker_db postgres

-- Grant schema permissions
ALTER DATABASE job_tracker_db OWNER TO job_tracker_user;
GRANT ALL ON SCHEMA public TO job_tracker_user;
ALTER SCHEMA public OWNER TO job_tracker_user;
