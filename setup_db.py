# Database setup and initialization script.
# Creates database/tables and registers seed data (departments, settings, users, and logs).

import os
import pymysql
from datetime import datetime, date, time, timedelta

def create_mysql_db_if_not_exists():
    """
    Attempts to connect to MySQL using environment vars,
    creating the target database if it does not exist.
    """
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '')
    dbname = os.environ.get('DB_NAME', 'attendance_db')
    
    try:
        # Connect to MySQL Server (without specifying db)
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        connection.commit()
        cursor.close()
        connection.close()
        print(f"[*] MySQL database '{dbname}' verified/created.")
        return True
    except Exception as e:
        print(f"[!] MySQL Connection/Creation failed: {e}")
        print("[!] Falling back to SQLite database...")
        return False

def seed_database():
    from app import create_app, bcrypt
    from database import db
    from models import User, Employee, Department, Attendance, Setting
    
    app = create_app()
    with app.app_context():
        print("[*] Recreating database tables...")
        # For setup ease, we drop and recreate
        db.drop_all()
        db.create_all()
        
        print("[*] Seeding default system settings...")
        settings_data = {
            'check_in_start_time': ('09:00:00', 'Shift Check-in limit'),
            'check_in_grace_period_mins': ('15', 'Allowed grace period mins'),
            'allowed_gps_latitude': ('12.9716', 'Company Lat'),
            'allowed_gps_longitude': ('77.5946', 'Company Lng'),
            'allowed_gps_radius_meters': ('200.0', 'Proximity radius limit')
        }
        for key, (val, desc) in settings_data.items():
            db.session.add(Setting(key=key, value=val, description=desc))
            
        print("[*] Seeding departments...")
        eng = Department(name="Engineering", code="ENG", description="Product development & QA")
        hr = Department(name="Human Resources", code="HR", description="Employee relations & hiring")
        sales = Department(name="Sales", code="SAL", description="Clients and business growth")
        db.session.add_all([eng, hr, sales])
        db.session.flush() # Populate IDs
        
        print("[*] Seeding user accounts...")
        # Hash passwords via Flask-Bcrypt
        admin_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
        hr_pw = bcrypt.generate_password_hash("hr123").decode('utf-8')
        emp_pw = bcrypt.generate_password_hash("emp123").decode('utf-8')
        
        u_admin = User(username="admin", email="admin@ams.com", password_hash=admin_pw, role="admin")
        u_hr = User(username="hr_user", email="hr@ams.com", password_hash=hr_pw, role="hr")
        u_emp = User(username="emp_user", email="employee@ams.com", password_hash=emp_pw, role="employee")
        
        db.session.add_all([u_admin, u_hr, u_emp])
        db.session.flush() # Populate IDs
        
        print("[*] Seeding employees profiles...")
        # Generate token QR codes
        hr_qr = seed_qr_token(u_hr.id, u_hr.username, app.config['JWT_SECRET_KEY'])
        emp_qr = seed_qr_token(u_emp.id, u_emp.username, app.config['JWT_SECRET_KEY'])
        
        emp_hr = Employee(
            user_id=u_hr.id,
            employee_id="EMP-2026-0001",
            first_name="Sarah",
            last_name="Jenkins",
            email=u_hr.email,
            phone="+1234567890",
            department_id=hr.id,
            designation="HR Manager",
            date_of_joining=date.today() - timedelta(days=100),
            qr_code=hr_qr,
            location_lat=12.9716,
            location_lng=77.5946
        )
        
        emp_dev = Employee(
            user_id=u_emp.id,
            employee_id="EMP-2026-0002",
            first_name="John",
            last_name="Doe",
            email=u_emp.email,
            phone="+1987654321",
            department_id=eng.id,
            designation="Software Engineer",
            date_of_joining=date.today() - timedelta(days=50),
            qr_code=emp_qr,
            location_lat=12.9716,
            location_lng=77.5946
        )
        
        db.session.add_all([emp_hr, emp_dev])
        db.session.flush()
        
        print("[*] Seeding sample attendance records...")
        today = date.today()
        # Log 1: Employee present 2 days ago
        att1 = Attendance(
            employee_id=emp_dev.id,
            date=today - timedelta(days=2),
            check_in_time=time(8, 50, 0),
            check_out_time=time(17, 5, 0),
            check_in_lat=12.9716,
            check_in_lng=77.5946,
            working_hours=8.25,
            overtime=0.25,
            status="Present",
            late_entry=False
        )
        # Log 2: Employee present 1 day ago (Late)
        att2 = Attendance(
            employee_id=emp_dev.id,
            date=today - timedelta(days=1),
            check_in_time=time(9, 20, 0),
            check_out_time=time(17, 0, 0),
            check_in_lat=12.9716,
            check_in_lng=77.5946,
            working_hours=7.66,
            overtime=0.0,
            status="Present",
            late_entry=True
        )
        # Log 3: HR present 1 day ago
        att3 = Attendance(
            employee_id=emp_hr.id,
            date=today - timedelta(days=1),
            check_in_time=time(8, 55, 0),
            check_out_time=time(17, 0, 0),
            check_in_lat=12.9716,
            check_in_lng=77.5946,
            working_hours=8.08,
            overtime=0.08,
            status="Present",
            late_entry=False
        )
        db.session.add_all([att1, att2, att3])
        db.session.commit()
        print("[+] Database seeding completed successfully!")

def seed_qr_token(user_id, username, secret_key):
    import jwt
    return jwt.encode(
        {'user_id': user_id, 'username': username},
        secret_key,
        algorithm='HS256'
    )

if __name__ == '__main__':
    # Determine DB_TYPE config override
    mysql_active = create_mysql_db_if_not_exists()
    
    if not mysql_active:
        # Force SQLite fallback
        os.environ['DB_TYPE'] = 'sqlite'
        print("[*] OS Environment DB_TYPE set to 'sqlite'")
        
    seed_database()
