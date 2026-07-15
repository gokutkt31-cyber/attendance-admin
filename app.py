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
    """Seed default admin user and departments if the database is empty (first deploy)."""
    from flask_bcrypt import generate_password_hash
    from models import User, Department
    from database import db

    # Only seed if no users exist
    if User.query.first():
        return

    print("[SEED] No users found. Seeding default admin account and departments...")

    # Create default departments
    departments = [
        Department(name="Engineering", code="ENG", description="Software & Systems Engineering"),
        Department(name="Human Resources", code="HR", description="HR & People Operations"),
        Department(name="Sales", code="SAL", description="Sales & Business Development"),
    ]
    for dept in departments:
        db.session.add(dept)

    # Create default admin user
    admin_pw = generate_password_hash("admin123").decode("utf-8")
    admin = User(
        username="admin",
        email="admin@ams.com",
        password_hash=admin_pw,
        role="admin",
        is_active=True,
    )
    db.session.add(admin)
    db.session.commit()
    print("[SEED] Default admin created: username=admin, password=admin123")


if __name__ == '__main__':
    app = create_app()
    # In production, debug is automatically False when FLASK_ENV=production
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
