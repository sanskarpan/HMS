# Hospital Management System (HMS)

A full-stack web application for managing hospital operations including appointments, patients, doctors, departments, treatments, and payments. Built with Flask (backend) and Vue.js 3 (frontend) with role-based access control for Admin, Doctor, and Patient users.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [User Roles & Workflows](#user-roles--workflows)
- [Background Tasks (Celery)](#background-tasks-celery)
- [Caching Strategy](#caching-strategy)
- [Testing](#testing)
- [PWA Features](#pwa-features)
- [Milestones](#milestones)
- [Troubleshooting](#troubleshooting)

---

## Features

### Core Features

- **JWT-based Authentication** with role-based access control
- **Three User Roles**: Admin, Doctor, Patient
- **Appointment Management** with conflict prevention (no double-booking)
- **Doctor Availability Scheduling** (morning/evening slots for 7 days)
- **Treatment Records** with diagnosis, prescriptions, and follow-ups
- **Payment Processing** (Card, Cash, Insurance - simulated)
- **Medical History Tracking** with export to CSV
- **Analytics Dashboards** with interactive charts
- **PDF/HTML Reports** (monthly reports, receipts, activity reports)
- **Email Notifications** for appointment reminders

### Advanced Features

- **Redis Caching** for API performance optimization
- **Celery Background Tasks** for async operations
- **Scheduled Jobs** (daily reminders, monthly reports)
- **Progressive Web App (PWA)** with offline support
- **Responsive Design** for mobile and desktop
- **Real-time Status Updates** for appointments
- **Audit Logging** for appointment status changes

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Flask 3.0.0 | REST API framework |
| **ORM** | SQLAlchemy 2.0.23 | Database operations |
| **Database** | SQLite | Data storage |
| **Authentication** | Flask-JWT-Extended | JWT token management |
| **Caching** | Redis + Flask-Caching | Performance optimization |
| **Task Queue** | Celery 5.3.4 | Background job processing |
| **Scheduler** | Celery Beat | Periodic task scheduling |
| **Frontend** | Vue.js 3 (CDN) | Single Page Application |
| **Routing** | Vue Router 4 | Client-side routing |
| **UI Framework** | Bootstrap 5.3.2 | Responsive styling |
| **Charts** | Chart.js 4.4.1 | Data visualization |
| **Icons** | Bootstrap Icons | UI icons |

---

## Project Structure

```
hospital-management-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── user.py              # User model (auth)
│   │   │   ├── doctor.py            # Doctor profile model
│   │   │   ├── patient.py           # Patient profile model
│   │   │   ├── department.py        # Department model
│   │   │   ├── appointment.py       # Appointment model
│   │   │   ├── availability.py      # Doctor availability model
│   │   │   ├── treatment.py         # Treatment records model
│   │   │   ├── payment.py           # Payment transactions model
│   │   │   └── status_log.py        # Appointment status history
│   │   ├── routes/                  # API blueprints
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── admin.py             # Admin management endpoints
│   │   │   ├── doctor.py            # Doctor endpoints
│   │   │   ├── patient.py           # Patient endpoints
│   │   │   ├── payment.py           # Payment endpoints
│   │   │   └── reports.py           # Report generation endpoints
│   │   ├── services/                # Business logic
│   │   │   ├── cache_service.py     # Redis caching utilities
│   │   │   ├── notification_service.py  # Email notifications
│   │   │   └── validation_service.py    # Input validation
│   │   ├── tasks/                   # Celery tasks
│   │   │   ├── reminders.py         # Appointment reminder tasks
│   │   │   ├── reports.py           # Report generation tasks
│   │   │   └── exports.py           # CSV export tasks
│   │   ├── utils/                   # Utilities
│   │   │   └── decorators.py        # Auth decorators
│   │   └── templates/               # Email/report templates
│   ├── app.py                       # Application entry point
│   ├── celery_app.py                # Celery configuration
│   ├── config.py                    # Configuration classes
│   └── init_db.py                   # Database initialization script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.js            # Navigation component
│   │   ├── views/
│   │   │   ├── Login.js             # Login page
│   │   │   ├── Register.js          # Registration page
│   │   │   ├── admin/               # Admin views
│   │   │   │   ├── AdminDashboard.js
│   │   │   │   ├── DoctorManagement.js
│   │   │   │   ├── PatientManagement.js
│   │   │   │   ├── AppointmentManagement.js
│   │   │   │   ├── AdminCharts.js
│   │   │   │   └── AdminPayments.js
│   │   │   ├── doctor/              # Doctor views
│   │   │   │   ├── DoctorDashboard.js
│   │   │   │   ├── DoctorAppointments.js
│   │   │   │   ├── DoctorPatients.js
│   │   │   │   ├── DoctorProfile.js
│   │   │   │   ├── DoctorAvailability.js
│   │   │   │   └── DoctorCharts.js
│   │   │   └── patient/             # Patient views
│   │   │       ├── PatientDashboard.js
│   │   │       ├── DepartmentList.js
│   │   │       ├── DepartmentDetails.js
│   │   │       ├── DoctorSearch.js
│   │   │       ├── DoctorDetails.js
│   │   │       ├── PatientAppointments.js
│   │   │       ├── PatientHistory.js
│   │   │       ├── PatientTreatments.js
│   │   │       ├── PatientProfile.js
│   │   │       └── PatientPayments.js
│   │   ├── services/                # API services
│   │   │   ├── api.js               # HTTP client
│   │   │   ├── auth.js              # Auth service
│   │   │   ├── admin.js             # Admin API calls
│   │   │   ├── doctor.js            # Doctor API calls
│   │   │   └── patient.js           # Patient API calls
│   │   ├── router/
│   │   │   └── index.js             # Vue Router configuration
│   │   └── main.js                  # Vue app initialization
│   ├── index.html                   # SPA entry point
│   ├── manifest.json                # PWA manifest
│   └── sw.js                        # Service worker
├── config/
│   └── .env.example                 # Environment variables template
├── requirements.txt                 # Python dependencies
├── conftest.py                      # Pytest configuration
└── README.md                        # This file
```

---

## Installation

### Prerequisites

- Python 3.9+
- Redis Server
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/23f3003478/hospital-management-system
cd hospital-management-system
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and Start Redis

```bash
# macOS (using Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows (using WSL or download from https://redis.io/download)
```

### Step 5: Configure Environment Variables

```bash
cp config/.env.example .env
```

Edit `.env` file with your settings (see [Configuration](#configuration) section).

### Step 6: Initialize the Database

```bash
python backend/init_db.py
```

This creates the SQLite database and seeds it with:
- 1 Admin user
- 5 Departments (Cardiology, Neurology, Orthopedics, Pediatrics, Dermatology)
- 5 Sample doctors
- 3 Sample patients
- Sample appointments and availability data

---

## Configuration

### Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400

# Database
DATABASE_URL=sqlite:///hospital.db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=RedisCache

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@hospital.com

# Admin Credentials (for initial setup)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@hospital.com
ADMIN_PASSWORD=admin123
```

### Cache Configuration

The application uses multi-level cache TTLs:

| Cache Type | TTL | Use Case |
|------------|-----|----------|
| Static | 30 min | Departments, roles |
| Semi-static | 10 min | User profiles, doctor info |
| Dynamic | 5 min | Appointments, treatments |
| Real-time | 2 min | Dashboard statistics |
| Search | 5 min | Search results |

---

## Running the Application

### Development Mode

**Terminal 1: Start Flask Backend**
```bash
cd hospital-management-system
source venv/bin/activate
python backend/app.py
```
Server runs at: http://localhost:5000

**Terminal 2: Start Celery Worker (for background tasks)**
```bash
cd hospital-management-system
source venv/bin/activate
celery -A backend.celery_app worker --loglevel=info
```

**Terminal 3: Start Celery Beat (for scheduled tasks)**
```bash
cd hospital-management-system
source venv/bin/activate
celery -A backend.celery_app beat --loglevel=info
```

### Access the Application

Open http://localhost:5000 in your browser.

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `dr_chen` | `doctor123` |
| Doctor | `dr_patel` | `doctor123` |
| Patient | `john_smith` | `patient123` |
| Patient | `jane_doe` | `patient123` |

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │     │   Doctor    │     │  Department │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │────<│ user_id(FK) │     │ id (PK)     │
│ username    │     │ department_id────>│ name        │
│ email       │     │ full_name   │     │ description │
│ password    │     │ qualification│    │ is_active   │
│ role        │     │ experience  │     └─────────────┘
│ is_active   │     │ phone       │
│ is_blacklist│     │ consultation│            │
└─────────────┘     │ bio         │            │
       │            │ is_active   │            │
       │            └─────────────┘            │
       │                   │                   │
       ▼                   │                   │
┌─────────────┐           │                   │
│   Patient   │           │                   │
├─────────────┤           │                   │
│ user_id(FK) │           │                   │
│ full_name   │           ▼                   │
│ dob         │    ┌─────────────┐           │
│ gender      │    │Availability │           │
│ phone       │    ├─────────────┤           │
│ address     │    │ doctor_id(FK│           │
│ blood_group │    │ date        │           │
│ emergency   │    │ morning_start           │
│ medical_hist│    │ morning_end │           │
└─────────────┘    │ evening_start           │
       │           │ evening_end │           │
       │           │ is_available│           │
       │           │ slot_duration           │
       │           └─────────────┘           │
       │                                      │
       ▼                                      ▼
┌───────────────────────────────────────────────┐
│                 Appointment                    │
├───────────────────────────────────────────────┤
│ id (PK)                                       │
│ patient_id (FK) ──────────────────────────────│
│ doctor_id (FK) ───────────────────────────────│
│ department_id (FK) ───────────────────────────│
│ appointment_date, appointment_time            │
│ duration, status (booked/completed/cancelled) │
│ reason, notes, cancelled_at, cancelled_by     │
└───────────────────────────────────────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐     ┌─────────────────┐
│  Treatment  │     │AppointmentStatus│
├─────────────┤     │      Log        │
│ appt_id(FK) │     ├─────────────────┤
│ diagnosis   │     │ appointment_id  │
│ prescription│     │ old_status      │
│ notes       │     │ new_status      │
│ tests       │     │ changed_by_role │
│ follow_up   │     │ changed_at      │
│ visit_type  │     │ reason          │
└─────────────┘     └─────────────────┘

┌─────────────┐
│   Payment   │
├─────────────┤
│ appt_id(FK) │
│ patient_id  │
│ amount      │
│ method      │
│ card_last4  │
│ status      │
│ transaction │
│ paid_at     │
└─────────────┘
```

### Tables Summary

| Table | Purpose |
|-------|---------|
| `user` | Authentication and role management |
| `doctor` | Doctor profiles and professional info |
| `patient` | Patient profiles and medical info |
| `department` | Hospital departments/specializations |
| `appointment` | Appointment scheduling |
| `doctor_availability` | Doctor working hours |
| `treatment` | Medical records per appointment |
| `payment` | Payment transactions |
| `appointment_status_log` | Audit trail for status changes |

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | User login | No |
| POST | `/api/auth/register` | Patient registration | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/refresh` | Refresh JWT token | Yes |
| POST | `/api/auth/logout` | User logout | Yes |
| POST | `/api/auth/change-password` | Change password | Yes |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard/stats` | Dashboard statistics |
| GET | `/api/admin/doctors` | List all doctors |
| POST | `/api/admin/doctors` | Create new doctor |
| PUT | `/api/admin/doctors/<id>` | Update doctor |
| POST | `/api/admin/doctors/<id>/blacklist` | Blacklist doctor |
| DELETE | `/api/admin/doctors/<id>` | Deactivate doctor |
| GET | `/api/admin/patients` | List all patients |
| PUT | `/api/admin/patients/<id>` | Update patient |
| POST | `/api/admin/patients/<id>/blacklist` | Blacklist patient |
| GET | `/api/admin/appointments` | List all appointments |
| POST | `/api/admin/appointments/<id>/cancel` | Cancel appointment |
| GET | `/api/admin/departments` | List departments |
| POST | `/api/admin/departments` | Create department |
| GET | `/api/admin/charts/*` | Analytics data |
| GET | `/api/admin/payments` | List all payments |
| POST | `/api/admin/payments/<id>/refund` | Refund payment |

### Doctor Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/doctor/dashboard/stats` | Dashboard statistics |
| GET | `/api/doctor/appointments` | List appointments |
| POST | `/api/doctor/appointments/<id>/complete` | Complete appointment |
| POST | `/api/doctor/appointments/<id>/cancel` | Cancel appointment |
| POST | `/api/doctor/appointments/<id>/no-show` | Mark no-show |
| GET | `/api/doctor/patients` | List patients |
| GET | `/api/doctor/patients/<id>/history` | Patient history |
| PUT | `/api/doctor/treatments/<id>` | Update treatment |
| GET | `/api/doctor/availability` | Get availability |
| POST | `/api/doctor/availability` | Set availability |
| POST | `/api/doctor/availability/bulk` | Set bulk availability |
| GET | `/api/doctor/profile` | Get profile |
| PUT | `/api/doctor/profile` | Update profile |
| GET | `/api/doctor/charts/*` | Analytics data |

### Patient Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/patient/dashboard/stats` | Dashboard statistics |
| GET | `/api/patient/departments` | List departments |
| GET | `/api/patient/departments/<id>` | Department details |
| GET | `/api/patient/doctors` | Search doctors |
| GET | `/api/patient/doctors/<id>` | Doctor details |
| GET | `/api/patient/doctors/<id>/slots` | Get available slots |
| GET | `/api/patient/appointments` | List appointments |
| POST | `/api/patient/appointments` | Book appointment |
| GET | `/api/patient/appointments/<id>` | Appointment details |
| POST | `/api/patient/appointments/<id>/cancel` | Cancel appointment |
| POST | `/api/patient/appointments/<id>/reschedule` | Reschedule |
| GET | `/api/patient/treatments` | List treatments |
| GET | `/api/patient/treatments/<id>` | Treatment details |
| GET | `/api/patient/history` | Medical history |
| POST | `/api/patient/export-history` | Export to CSV (async) |
| GET | `/api/patient/export-status/<task_id>` | Check export status |
| GET | `/api/patient/download-export/<file_id>` | Download export |
| GET | `/api/patient/profile` | Get profile |
| PUT | `/api/patient/profile` | Update profile |

### Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payment/initiate` | Initiate payment |
| POST | `/api/payment/process` | Process payment |
| GET | `/api/payment/history` | Payment history |
| GET | `/api/payment/pending` | Pending payments |
| GET | `/api/payment/<id>` | Payment details |
| GET | `/api/payment/appointment/<apt_id>` | Payment for appointment |

### Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/admin/monthly` | Monthly hospital report (HTML) |
| GET | `/api/reports/admin/monthly/data` | Monthly report data (JSON) |
| GET | `/api/reports/doctor/activity` | Doctor activity report |
| GET | `/api/reports/patient/receipt/<id>` | Payment receipt |
| GET | `/api/reports/patient/history` | Patient history report |

---

## User Roles & Workflows

### Admin Workflow

1. **Login** with admin credentials
2. **Dashboard** shows total doctors, patients, appointments, revenue
3. **Doctor Management**: Add, edit, blacklist doctors
4. **Patient Management**: View, edit, blacklist patients
5. **Appointment Management**: View all, cancel if needed
6. **Analytics**: View charts for trends, department stats, revenue
7. **Payments**: View all payments, process refunds
8. **Reports**: Generate monthly hospital reports

### Doctor Workflow

1. **Login** with credentials provided by admin
2. **Dashboard** shows today's appointments, week schedule
3. **Set Availability**: Configure working hours for next 7 days
4. **View Appointments**: See scheduled patients
5. **Complete Visit**: Mark appointment complete, add treatment details
6. **Treatment Records**: Add diagnosis, prescriptions, follow-up dates
7. **View Patient History**: Access medical records of patients
8. **Analytics**: View personal performance charts
9. **Reports**: Download activity reports

### Patient Workflow

1. **Register** new account or login
2. **Browse Departments**: View available specializations
3. **Search Doctors**: Filter by department, name, qualification
4. **View Availability**: Check doctor's available slots
5. **Book Appointment**: Select date, time, provide reason
6. **Make Payment**: Pay for appointment (card/cash/insurance)
7. **View Appointments**: Track upcoming and past appointments
8. **View Treatments**: Access diagnosis, prescriptions, follow-ups
9. **Export History**: Download medical history as CSV
10. **Download Receipts**: Get payment receipts

---

## Background Tasks (Celery)

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `send_daily_reminders` | 8:00 AM daily | Sends appointment reminders |
| `send_monthly_reports` | 1st of month, 9:00 AM | Sends doctor activity reports |
| `cleanup_exports_task` | 2:00 AM daily | Cleans up old export files |

### Async Tasks

| Task | Trigger | Description |
|------|---------|-------------|
| `send_appointment_reminder` | Daily job | Individual appointment reminder |
| `generate_monthly_report` | Monthly job | Generate doctor's monthly report |
| `export_patient_history_task` | User request | Export patient data to CSV |

### Testing Celery Tasks

**Start Redis:**
```bash
redis-server
```

**Start Worker:**
```bash
celery -A backend.celery_app worker --loglevel=info
```

**Start Beat Scheduler:**
```bash
celery -A backend.celery_app beat --loglevel=info
```

**Test Manually (Python shell):**
```python
from backend.celery_app import celery
from backend.app.tasks.reminders import send_daily_reminders

# Trigger immediately
result = send_daily_reminders.delay()
print(result.get())
```

---

## Caching Strategy

The application implements Redis caching with multiple TTL levels:

```python
# Cache key patterns
CACHE_KEYS = {
    'dash:admin:stats': 120,      # 2 minutes
    'dash:doctor:{id}': 120,      # 2 minutes
    'dash:patient:{id}': 120,     # 2 minutes
    'dept:{id}': 1800,            # 30 minutes
    'doctor:{id}': 600,           # 10 minutes
    'apt:{id}': 300,              # 5 minutes
    'search:{hash}': 300,         # 5 minutes
}
```

### Cache Invalidation

Cache is automatically invalidated when:
- Appointments are created, updated, or cancelled
- Doctor profiles are modified
- Patient profiles are updated
- Treatments are added or modified

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test models
pytest backend/tests/test_models.py

# Test routes
pytest backend/tests/test_routes.py

# Test with coverage
pytest --cov=backend
```

### Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `dr_chen` | `doctor123` |
| Patient | `john_smith` | `patient123` |

---

## PWA Features

The application includes Progressive Web App capabilities:

### Features

- **Offline Support**: Basic offline functionality via service worker
- **Install Prompt**: "Add to Home Screen" capability
- **App Shortcuts**: Quick access to "Book Appointment" and "My Appointments"
- **Responsive Design**: Works on mobile, tablet, and desktop

### Manifest Configuration

```json
{
    "name": "Hospital Management System",
    "short_name": "HMS",
    "display": "standalone",
    "theme_color": "#0d6efd",
    "background_color": "#ffffff"
}
```

---

## Milestones

### Milestone 1: Database Models and Schema Setup (15%)
- User, Doctor, Patient, Department, Appointment, Treatment, Payment models
- Relationships and constraints defined
- Admin user pre-created programmatically

### Milestone 2: Authentication and Role-Based Access (10%)
- JWT-based authentication with Flask-JWT-Extended
- Role-based access control (Admin, Doctor, Patient)
- Login, register, logout, password change

### Milestone 3: Admin Dashboard and Management (15%)
- Dashboard with statistics
- Doctor CRUD operations
- Patient management
- Appointment oversight
- Blacklist functionality

### Milestone 4: Doctor Dashboard & Appointment/Treatment Management (15%)
- Doctor dashboard with appointments
- Appointment status management (complete, cancel, no-show)
- Treatment record management
- Patient history access

### Milestone 5: Patient Dashboard and Appointment System (13%)
- Patient dashboard
- Department and doctor browsing
- Appointment booking, cancellation, rescheduling
- Medical history view

### Milestone 6: Appointment History and Conflict Prevention (12%)
- Double-booking prevention
- Status tracking and history
- Treatment record storage

### Milestone 7: Backend Jobs - Daily Reminders & Monthly Reports (10%)
- Celery + Redis setup
- Daily appointment reminders
- Monthly doctor reports
- CSV export functionality

### Milestone 8: API Performance Optimization & Caching (5%)
- Redis caching implementation
- Multi-level TTL strategy
- Cache invalidation

### Milestone 9: UI/UX Enhancements & PWA Features
- Responsive Bootstrap design
- Progressive Web App features
- Service worker implementation

### Milestone 10: Reports, Charts & Payments
- Chart.js analytics dashboards
- Payment processing (simulated)
- PDF/HTML report generation

---

## Troubleshooting

### Common Issues

**1. Charts Not Loading**
- Hard refresh the page: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Clear browser cache
- Check browser console for errors

**2. 401 Unauthorized Errors**
- Token may have expired - login again
- Check if `access_token` is in localStorage

**3. Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
brew services start redis  # macOS
sudo systemctl start redis # Linux
```

**4. Celery Tasks Not Running**
```bash
# Ensure Redis is running
redis-cli ping

# Check Celery worker logs
celery -A backend.celery_app worker --loglevel=debug

# Check Celery beat logs
celery -A backend.celery_app beat --loglevel=debug
```

**5. Database Issues**
```bash
# Reinitialize database
rm backend/hospital.db
python backend/init_db.py
```

**6. Service Worker Cache Issues**
- Open DevTools > Application > Service Workers
- Click "Unregister"
- Hard refresh the page

### Logs Location

- Flask logs: Console output
- Celery worker logs: Console output
- Celery beat logs: Console output

