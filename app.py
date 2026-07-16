import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from config import Config
from database import db
from mail_service import mail
from models import User, Setting

# Create instances
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Login Manager
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register Blueprints
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors.html', code=404, message="Page Not Found"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors.html', code=403, message="Access Forbidden"), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors.html', code=500, message="Internal Server Error"), 500
        
    # Setup folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'selfies'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
    
    # Auto-initialize database tables and seed default admin on first run
    with app.app_context():
        try:
            db.create_all()
            _seed_initial_data()
        except Exception as e:
            app.logger.warning(f"DB init warning: {e}")

        try:
            # Sync key-value rules to current running context
            settings = Setting.query.all()
            for s in settings:
                key_upper = s.key.upper()
                if s.key == 'check_in_grace_period_mins':
                    app.config[key_upper] = int(s.value)
                elif s.key.startswith('allowed_gps_') or s.key == 'allowed_gps_radius_meters':
                    app.config[key_upper] = float(s.value)
                else:
                    app.config[key_upper] = s.value
        except Exception:
            # Table may not exist yet during migrations/creation
            pass

    return app


def _seed_initial_data():
    """Seed default admin, HR, sample employees and departments on first deploy."""
    from flask_bcrypt import generate_password_hash
    from datetime import date
    import jwt as pyjwt
    from models import User, Department, Employee
    from database import db

    # Only seed if no users exist
    if User.query.first():
        return

    print("[SEED] No users found. Seeding demo data...")

    # ── Departments ───────────────────────────────────────────
    eng  = Department(name="Engineering",      code="ENG", description="Software & Systems Engineering")
    hr   = Department(name="Human Resources",  code="HR",  description="HR & People Operations")
    sal  = Department(name="Sales",            code="SAL", description="Sales & Business Development")
    mkt  = Department(name="Marketing",        code="MKT", description="Marketing & Brand")
    for d in [eng, hr, sal, mkt]:
        db.session.add(d)
    db.session.flush()  # get dept IDs

    # ── Admin user ────────────────────────────────────────────
    admin_pw = generate_password_hash("admin123").decode("utf-8")
    admin = User(username="admin", email="admin@ams.com",
                 password_hash=admin_pw, role="admin", is_active=True)
    db.session.add(admin)

    # ── HR user ───────────────────────────────────────────────
    hr_pw = generate_password_hash("hr1234").decode("utf-8")
    hr_user = User(username="hrmanager", email="hr@ams.com",
                   password_hash=hr_pw, role="hr", is_active=True)
    db.session.add(hr_user)
    db.session.flush()

    # Add HR employee profile
    hr_emp = Employee(
        user_id=hr_user.id, employee_id="EMP-2026-0001",
        first_name="Priya", last_name="Sharma",
        email="hr@ams.com", phone="9876543210",
        department_id=hr.id, designation="HR Manager",
        date_of_joining=date(2024, 1, 15), status="active",
    )
    db.session.add(hr_emp)

    # ── Sample employee users + profiles ─────────────────────
    sample_employees = [
        # (username, email, password,  fname,    lname,      dept,   designation,              joining,             phone)
        ("rajesh_k",   "rajesh@ams.com",   "emp123", "Rajesh",   "Kumar",     eng,  "Senior Developer",       date(2023, 3, 1),  "9000000001"),
        ("anita_v",    "anita@ams.com",    "emp123", "Anita",    "Verma",     eng,  "Frontend Engineer",       date(2023, 6, 15), "9000000002"),
        ("suresh_p",   "suresh@ams.com",   "emp123", "Suresh",   "Patel",     sal,  "Sales Executive",         date(2024, 2, 1),  "9000000003"),
        ("meena_r",    "meena@ams.com",    "emp123", "Meena",    "Reddy",     sal,  "Sales Manager",           date(2022, 11, 1), "9000000004"),
        ("kiran_d",    "kiran@ams.com",    "emp123", "Kiran",    "Das",       mkt,  "Marketing Analyst",       date(2024, 4, 10), "9000000005"),
        ("pooja_m",    "pooja@ams.com",    "emp123", "Pooja",    "Mishra",    mkt,  "Content Strategist",      date(2023, 9, 20), "9000000006"),
        ("amit_s",     "amit@ams.com",     "emp123", "Amit",     "Singh",     eng,  "Backend Engineer",        date(2025, 1, 5),  "9000000007"),
        ("lakshmi_n",  "lakshmi@ams.com",  "emp123", "Lakshmi",  "Nair",      hr,   "Recruitment Specialist",  date(2024, 7, 1),  "9000000008"),
    ]

    for idx, (uname, email, pw, fname, lname, dept, desig, joined, phone) in enumerate(sample_employees, start=2):
        emp_pw = generate_password_hash(pw).decode("utf-8")
        user = User(username=uname, email=email, password_hash=emp_pw,
                    role="employee", is_active=True)
        db.session.add(user)
        db.session.flush()

        emp_code = f"EMP-2026-{idx:04d}"
        emp = Employee(
            user_id=user.id, employee_id=emp_code,
            first_name=fname, last_name=lname,
            email=email, phone=phone,
            department_id=dept.id, designation=desig,
            date_of_joining=joined, status="active",
        )
        db.session.add(emp)

    db.session.commit()
    print("[SEED] Demo data seeded: admin/admin123 | hrmanager/hr1234 | employees: emp123")


if __name__ == '__main__':
    app = create_app()
    # In production, debug is automatically False when FLASK_ENV=production
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
