from flask import request
from flask_login import current_user
from . import db
from .models import AuditLog

def log_event(action, resource_type=None, resource_id=None, details=None):
    """
    Helper function to record system events in the AuditLog.
    """
    # Import AuditLog here if needed to avoid circular imports, 
    # but we already imported it above.
    
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    # We don't commit here to allow the caller to commit as part of their transaction
    return log
