# HRMS Lite

## Overview
HRMS Lite is a lightweight Human Resource Management System that provides the core HR workflows:
1. Employee management (create, list, delete)
2. Daily attendance tracking per employee (Present/Absent)
3. A dashboard with quick insights and date-range filtering
4. REST-style JSON APIs for all backend operations

The UI is built using Django templates with Bootstrap and custom styling to resemble a modern production dashboard.

## Tech Stack
- Backend: Python, Django
- Frontend: Django templates, Bootstrap 5, custom CSS
- Charts: Chart.js (dashboard charts)
- Database: SQLite by default (optional MySQL support)
- Deployment: Gunicorn + WhiteNoise for static file serving

## Data Model
### `Employee`
- `employee_id` (unique)
- `full_name`
- `email` (unique, validated by Django `EmailField`)
- `department`

### `Attendance`
- `employee` (FK to `Employee`)
- `date`
- `status` (`present` or `absent`)
- Uniqueness constraint: one attendance entry per `(employee, date)`

## Implemented Features
### Employee Management
- Add employee (server-side validation)
- List employees with actions
- Delete employee

### Attendance Management
- Mark attendance for an employee by `date` and `status`
- Duplicate prevention via DB constraint and graceful error handling
- Attendance history per employee

### Dashboard & Search
- Dashboard date range filter (`from`, `to`)
- Dashboard counts (Total employees, Attendance records, Present, Absent) reflect the selected date range
- “Present Days per Employee” table for the selected date range
- Employee search on the employee list page:
  - Matches against full name, email, employee ID, and department

## REST API (JSON)
Base path: `/employees/`

### Employees
- `GET  /employees/api/employees/`
- `POST /employees/api/employees/`

### Attendance (per employee)
- `GET  /employees/api/employees/<id>/attendance/`
- `POST /employees/api/employees/<id>/attendance/`

## Validation & Error Handling
- Required fields are validated by Django forms/models.
- Duplicate employees (same `employee_id` or `email`) return a `400` with a meaningful error message.
- Duplicate attendance entries for the same `(employee, date)` return a `400`.
- Correct HTTP status codes are used for success and failure responses.

## Local Development Setup
### 1) Create and activate a virtual environment
```bash
cd /home/saket/Desktop/project/assignment
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run migrations
```bash
python manage.py migrate
```

### 4) Start the server
```bash
python manage.py runserver
```

Open:
- UI (Dashboard): `http://127.0.0.1:8000/`
- Employees: `http://127.0.0.1:8000/employees/`
- Attendance: `http://127.0.0.1:8000/employees/<id>/attendance/`

## Deployment (Render - Free-Friendly)
This project can be deployed as a single Django service (UI and API are served from the same app).

### Render Web Service Configuration
- Build command:
  ```bash
  pip install -r requirements.txt
  ```
- Start command:
  ```bash
  gunicorn hrms_lite.wsgi:application --bind 0.0.0.0:$PORT
  ```
- Recommended Pre-deploy command (if available in your Render plan):
  ```bash
  python manage.py migrate --noinput && python manage.py collectstatic --noinput
  ```

### Environment Variables
Required for production-style mode:
- `DEBUG=0`
- `DJANGO_SECRET_KEY` (set any long random string)

Database (defaults to SQLite):
- `DJANGO_DB_ENGINE=sqlite`

Optional MySQL configuration:
- `DJANGO_DB_ENGINE=mysql`
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`

