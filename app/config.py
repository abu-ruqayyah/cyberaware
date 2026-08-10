import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-cyberaware-secret-key-3mtt-2026'
    
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # Environment-driven Database configuration
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url:
        # Render PostgreSQL connection strings use 'postgres://', which SQLAlchemy 2.0 requires as 'postgresql://'
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        # Local SQLite fallback
        db_file_path = os.path.join(INSTANCE_DIR, 'platform.db').replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file_path}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Production Debug Control
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Seed Configuration
    SEED_DEMO_DATA = os.environ.get('SEED_DEMO_DATA', 'True').lower() == 'true'
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@cyberaware.local')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'AdminPassword123!')
    
    # Protected Upload Directories (Outside app/static/)
    UPLOAD_ROOT = os.path.join(INSTANCE_DIR, 'uploads')
    REPORTS_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, 'reports')
    LAB_EVIDENCE_UPLOAD_DIR = os.path.join(UPLOAD_ROOT, 'lab_evidence')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EVIDENCE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}
