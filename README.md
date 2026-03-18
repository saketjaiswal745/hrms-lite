# HRMS Lite (Full-Stack Assignment)

## Project Overview
HRMS Lite is a lightweight Human Resource Management System that lets an admin:
- Manage employees (create, view, delete)
- Manage daily attendance per employee (mark Present/Absent)

It includes:
- A **production-ready styled UI** (Django templates + Bootstrap + custom CSS)
- **REST-style JSON APIs** for employees and attendance
- Server-side validation with proper error handling and HTTP status codes

## Tech Stack
- **Backend:** Python + **Django** (MVC)
- **Database:** Default **SQLite** for easy deployment; supports **MySQL** (optional)
- **Frontend:** Django templates, Bootstrap, custom CSS
- **Charts:** Chart.js (for dashboard charts)
- **Deployment helpers (free-friendly):** Gunicorn + WhiteNoise

## Features
- Employee Management
  - Unique `employee_id`
  - Unique `email` + valid email format
  - Department field
- Attendance Management
  - Mark attendance with `date` + `status` (Present/Absent)
  - Prevents duplicate attendance for the same `employee + date`
- Dashboard
  - Date range filtering (`from`, `to`)
  - Present/Absent counts
  - “Present Days per Employee” table for a selected date range
- Search
  - Search employees by `name`, `email`, `employee_id`, `department`

## REST API Endpoints
Base path: `/employees/`

- Employees
  - `GET  /employees/api/employees/` (list employees)
  - `POST /employees/api/employees/` (create employee)
- Attendance (per employee)
  - `GET  /employees/api/employees/<id>/attendance/` (list attendance)
  - `POST /employees/api/employees/<id>/attendance/` (create attendance)

## Assumptions / Limitations
- **No authentication**: single admin experience (no login system implemented).
- Attendance is tracked only by **date + status** (no leave/payroll features).
- For deployment, the project defaults to **SQLite** to stay free and easy to run; MySQL requires additional configuration.

## How to Run Locally

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
- UI: `http://127.0.0.1:8000/`
- Employees: `http://127.0.0.1:8000/employees/`

## Environment Variables (Optional)
The app uses SQLite by default. To use MySQL, set:
- `DJANGO_DB_ENGINE=mysql`
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`

Other:
- `DEBUG=1` (local dev)
- `DJANGO_SECRET_KEY` (recommended for production)
- `ALLOWED_HOSTS` (comma-separated)

