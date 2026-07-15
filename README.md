# Glassmorphism Full Stack Employee Attendance Management System

A state-of-the-art Full Stack Employee Attendance Management System utilizing a modern, premium Glassmorphism design language with dark/light themes, real-time analytics graphs, QR Code attendance scanner/badging, GPS location boundary verification, webcam selfie check-ins, leave workflow approvals, and comprehensive XLS/PDF reports.

---

## 🌟 Features

* **Glassmorphism UI**: Beautifully designed responsive layout utilizing modern CSS variables for Dark/Light mode theme switching, glass card structures, smooth hover micro-animations, and Animate On Scroll (AOS).
* **Role-Based Auth (Admin, HR, Employee)**: Secure password hashing using Bcrypt, session management via Flask-Login, and JWT token encryption.
* **Webcam Selfie Check-In/Out**: Access client webcams via HTML5 to capture verification photos at check-in/out.
* **GPS Location boundary matching**: Calculates employee check-in distance from office boundary parameters using the Haversine formula, restricting logs outside authorized coordinates.
* **QR Attendance & Badging**: Generates personal employee ID cards with integrated dynamic QR verification keys. Scan physical cards via kiosk terminal QR readers.
* **Leave Management**: Submissions forms, balance allocations, and HR/Admin comment workflows with automatic attendance log population for approved dates.
* **Analytics Dashboards**: Visualizes attendance stats, recent activity streams, and departments distributions using interactive Chart.js graphs.
* **Comprehensive Audit Reports**: Sort logs by date range and select specific employees. Supports instant Excel spreadsheet exports, PDF logs, and digital verification certificates downloads.
* **Email Notifications**: Triggers notification messages using Flask-Mail for check-ins and leave status updates.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, CSS3 (Glassmorphic variables design), JS (ES6), Bootstrap 5, Chart.js, Font Awesome 6, SweetAlert2, Toastify JS, AOS (Animate On Scroll).
* **Backend**: Python 3, Flask, Flask-Login, Flask-WTF, Flask-Mail, Flask-Bcrypt, Flask-Migrate, SQLAlchemy ORM.
* **Database**: MySQL (falls back to local SQLite database automatically for simplified zero-config development).
* **Deployment/Server**: Python-dotenv, PyMySQL, Gunicorn.

---

## 📦 Project Directory Layout

```text
Employee-Attendance-System/
│── static/
│   ├── css/
│   │   └── style.css            # Core Glassmorphic visual variables & layouts
│   ├── js/
│   │   ├── main.js              # Theme switcher, Toastify wrappers, CSRF fetch helpers
│   │   ├── attendance.js        # Webcam capturer, GPS locator, QR reader bindings
│   │   └── dashboard.js         # Chart.js analytics graphs & custom Heatmap Calendar
│   ├── images/
│   │   └── default.jpg          # Silhouette avatar placeholder fallback
│   └── uploads/
│       ├── selfies/             # Uploaded selfie verification logs
│       └── avatars/             # Custom profile pictures uploads
│── templates/
│   ├── base.html                # Sidebar navigations, theme toggler structure
│   ├── login.html               # Centered login panel
│   ├── register.html            # Credentials and details forms
│   ├── dashboard.html           # Unified stats cards and charts container
│   ├── attendance.html          # Camera feed previewer & Heatmap Calendar
│   ├── employees.html           # Employee directory management modals
│   ├── reports.html             # Advanced audit filters and tabular logs list
│   ├── profile.html             # Profile editor, file uploader, change password
│   ├── id_card.html             # Physical digital badge rendering
│   ├── leave_apply.html         # Personal leave request forms & log
│   ├── leaves_manage.html       # Leave approval comments modals
│   ├── settings.html            # Latitude/Longitude coordinates configuration
│   └── errors.html              # Custom page handler for status 403, 404, 500
│── app.py                       # Application factory, extensions initialization
│── config.py                    # Environment loads, limits, and variables mapper
│── database.py                  # SQLAlchemy db object builder
│── models.py                    # Database schema class maps
│── routes.py                    # Authentication controller & API endpoints
│── forms.py                     # WTForms input validation models
│── mail_service.py              # Flask-Mail sending alerts
│── requirements.txt             # Backend dependencies lists
│── schema.sql                   # MySQL database tables DDL structure
│── sample_data.sql              # MySQL baseline datasets insertions
│── setup_db.py                  # DB auto-generation and tables seeding runner
│── .env                         # Local configuration variables parameters
└── README.md                    # Setup documentation
```

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed. If running MySQL, verify your SQL server is running (e.g. XAMPP, WampServer, or native MySQL service).

### 2. Clone and Setup Environment
Navigate to the directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Customize parameters inside `.env` at the root directory:
```env
# Flask configuration
SECRET_KEY=dev-key-please-change-in-production-1234567890
JWT_SECRET_KEY=jwt-secret-key-9876543210

# Database configurations
# Set DB_TYPE=sqlite to bypass MySQL requirement entirely
DB_TYPE=mysql
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_NAME=attendance_db

# Email notifications SMTP parameters (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_username@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=noreply@attendance.com
```

### 4. Initialize and Seed Database
Run the setup script. This script automatically checks MySQL connectivity, creates the database if not found, runs tables creation, and injects seed users, settings, and attendance logs:
```bash
python setup_db.py
```
*Note: If local MySQL service is inactive or configuration fails, the script automatically changes configuration to fall back to a local SQLite file (`attendance.db`) so the system runs immediately.*

### 5. Launch local server
Start the Flask application:
```bash
python app.py
```
The portal will be running locally at: `http://localhost:5000`

---

## 🔑 Seed User Logins

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | Admin | Access system settings, logs, employee directory, and departments creation. |
| `hr_user` | `hr123` | HR Manager | Approve/Reject leave requests, manage employees, and filter reports logs. |
| `emp_user` | `emp123` | Employee | Selfie check-in/out, apply leaves, download reports, view dynamic badge. |
