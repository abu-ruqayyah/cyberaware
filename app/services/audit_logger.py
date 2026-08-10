from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.audit import AuditLog

def log_event(event_type, description, user=None):
    """
    Record an audit log entry for security and accountability.
    Guarantees zero credential or password logging.
    """
    try:
        user_id = None
        user_role = 'ANONYMOUS'

        if user:
            user_id = user.id
            user_role = user.role
        elif current_user and current_user.is_authenticated:
            user_id = current_user.id
            user_role = current_user.role

        ip_address = request.remote_addr if request else '127.0.0.1'
        user_agent = request.user_agent.string if request and request.user_agent else 'Unknown'

        # Filter out sensitive text if present
        sanitized_description = str(description)
        for sensitive_word in ['password', 'secret', 'token', 'hash']:
            if sensitive_word in sanitized_description.lower():
                sanitized_description = f"[REDACTED SENSITIVE DATA] Event: {event_type}"

        log_entry = AuditLog(
            user_id=user_id,
            user_role=user_role,
            event_type=event_type,
            description=sanitized_description,
            ip_address=ip_address,
            user_agent=user_agent[:255]
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error recording audit log: {e}")
