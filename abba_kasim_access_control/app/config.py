import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
UPLOADS_DIR = os.path.join(INSTANCE_DIR, 'uploads')
REPORTS_DIR = os.path.join(UPLOADS_DIR, 'reports')
LAB_EVIDENCE_DIR = os.path.join(UPLOADS_DIR, 'lab_evidence')

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LAB_EVIDENCE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'abba-kasim-access-control-audit-key-2026-secure')
    
    # Environment-driven database configuration
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and not raw_db_url.startswith("sqlite:///"):
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        db_path = os.path.abspath(os.path.join(INSTANCE_DIR, 'access_audit.db')).replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload paths outside static directory
    UPLOAD_FOLDER = UPLOADS_DIR
    REPORTS_FOLDER = REPORTS_DIR
    LAB_EVIDENCE_FOLDER = LAB_EVIDENCE_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'pcap', 'pcapng', 'txt', 'json', 'xml', 'csv'}
    
    # Security Session Flags
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Admin Pre-seeding
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'abba_auditor')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'abba@accessaudit.local')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'AuditAdminPassword123!')
    SEED_DEMO_DATA = os.environ.get('SEED_DEMO_DATA', 'True').lower() == 'true'
