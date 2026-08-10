import os
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Verify that file extension is explicitly permitted."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EVIDENCE_EXTENSIONS']

def get_secure_filename(filename):
    """Generate a clean, sanitized filename."""
    return secure_filename(filename)

def admin_required(f):
    """Custom decorator enforcing Admin role access control."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
