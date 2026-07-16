import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production-1234567890')
    
    # SQLAlchemy Database Settings
    # Default to MySQL, fallback to SQLite if DATABASE_URL not specified or MySQL not set up
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'attendance_db')
    
    # We can explicitly configure DB_TYPE as 'sqlite' or 'mysql'
    DB_TYPE = os.environ.get('DB_TYPE', 'mysql')
    
    if DB_TYPE == 'sqlite':
        # On Render / cloud: use /tmp for writable SQLite storage
        # In local dev: use the project directory
        _is_render = os.environ.get('RENDER') == 'true'
        _sqlite_path = '/tmp/attendance.db' if _is_render else os.path.join(BASE_DIR, 'attendance.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_sqlite_path}"
    else:
        # mysql+pymysql://username:password@host/dbname
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL', 
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Authentication settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-9876543210')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    # Flask Mail Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@employeeattendance.com')
    
    # File Upload Directory — use env var override for cloud deployments (e.g. Render /tmp/uploads)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    
    # App Settings
    CHECK_IN_START_TIME = os.environ.get('CHECK_IN_START_TIME', '09:00:00')
    CHECK_IN_GRACE_PERIOD_MINS = int(os.environ.get('CHECK_IN_GRACE_PERIOD_MINS', 15))
    ALLOWED_GPS_LATITUDE = float(os.environ.get('ALLOWED_GPS_LATITUDE', 12.9716)) # Example Lat
    ALLOWED_GPS_LONGITUDE = float(os.environ.get('ALLOWED_GPS_LONGITUDE', 77.5946)) # Example Lng
    ALLOWED_GPS_RADIUS_METERS = float(os.environ.get('ALLOWED_GPS_RADIUS_METERS', 200.0)) # Allowed distance from coordinates
