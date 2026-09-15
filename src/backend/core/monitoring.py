import json
import logging
import time
from django.utils import timezone

logger = logging.getLogger("watch_behavior")

def log_audit_event(action: str, user=None, resource_id: str = None, request=None, **extra):
    user_id = None
    if user and getattr(user, "is_authenticated", False):
        user_id = str(user.id)
    elif request and hasattr(request, "user") and request.user.is_authenticated:
        user_id = str(request.user.id)

    ip_address = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")

    payload = {
        "timestamp": time.time(),
        "datetime": timezone.now().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource_id": str(resource_id) if resource_id else None,
        "ip": ip_address,
        "metadata": extra,
    }
    logger.info(json.dumps(payload))
