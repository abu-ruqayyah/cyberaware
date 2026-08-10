from app.services.audit_logger import log_event
from app.models.audit import AuditLog
from app.models.user import User

def test_audit_logging_without_credential_leak(app):
    with app.app_context():
        user = User.query.filter_by(username='teststaff').first()
        
        # Log event containing sensitive word 'password'
        log_event('TEST_EVENT', 'Attempted login with password MySecretPass123!', user=user)

        log_entry = AuditLog.query.filter_by(event_type='TEST_EVENT').first()
        assert log_entry is not None
        assert 'MySecretPass123!' not in log_entry.description
        assert 'REDACTED' in log_entry.description
