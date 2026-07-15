from datetime import datetime
from flask_login import UserMixin
from database import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'admin', 'hr', 'employee'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employee_profile = db.relationship('Employee', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref='department', lazy=True)
    
    def __repr__(self):
        return f"<Department {self.name}>"

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False) # e.g. EMP-2026-0001
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    designation = db.Column(db.String(100))
    date_of_joining = db.Column(db.Date, nullable=False)
    profile_pic = db.Column(db.String(255), default='default.jpg')
    status = db.Column(db.String(20), default='active') # 'active', 'inactive'
    qr_code = db.Column(db.String(255)) # String for verification token
    
    # Coordinates for GPS Verification (Null value falls back to default system settings)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    
    # Relationships
    attendances = db.relationship('Attendance', backref='employee', lazy=True, cascade="all, delete-orphan")
    leave_requests = db.relationship('LeaveRequest', backref='employee', lazy=True, cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    def __repr__(self):
        return f"<Employee {self.full_name} ({self.employee_id})>"

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)
    
    # GPS Verification details
    check_in_lat = db.Column(db.Float, nullable=True)
    check_in_lng = db.Column(db.Float, nullable=True)
    check_out_lat = db.Column(db.Float, nullable=True)
    check_out_lng = db.Column(db.Float, nullable=True)
    
    # Selfie paths
    check_in_selfie = db.Column(db.String(255), nullable=True)
    check_out_selfie = db.Column(db.String(255), nullable=True)
    
    working_hours = db.Column(db.Float, default=0.0)
    overtime = db.Column(db.Float, default=0.0)
    
    # Statuses: 'Present', 'Absent', 'Leave', 'Half Day', 'Holiday'
    status = db.Column(db.String(20), default='Absent', nullable=False)
    
    late_entry = db.Column(db.Boolean, default=False)
    early_exit = db.Column(db.Boolean, default=False)
    
    # Approval
    approval_status = db.Column(db.String(20), default='Approved') # 'Pending', 'Approved', 'Rejected'
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f"<Attendance Employee={self.employee_id} Date={self.date} Status={self.status}>"

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # 'Casual', 'Medical', 'Earned', 'Maternity', 'Paternity'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # 'Pending', 'Approved', 'Rejected'
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LeaveRequest Employee={self.employee_id} Type={self.leave_type} Status={self.status}>"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(20), default='system')  # 'system', 'attendance', 'leave'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Notification User={self.user_id} Title={self.title} Read={self.is_read}>"

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"
