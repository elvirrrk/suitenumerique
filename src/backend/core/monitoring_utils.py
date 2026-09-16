import json
import logging
import time
from django.utils import timezone
from typing import Literal
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger("monitoring_audit")

CriticalityLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def get_client_ip(request) -> str | None:
    """Extract client IP safely from request headers."""
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def log_audit_event(
    action: str,
    user=None,
    resource_id: str = None,
    request=None,
    criticality: CriticalityLevel = "LOW",
    **extra
):
    user_obj = user or getattr(request, "user", None)
    user_id = str(user_obj.id) if (user_obj and getattr(user_obj, "is_authenticated", False)) else None
    normalized_criticality = str(criticality).upper() if criticality else "LOW"

    payload = {
        "timestamp": time.time(),
        "datetime": timezone.now().isoformat(),
        "action": action,
        "criticality": normalized_criticality,
        "user_id": user_id,
        "resource_id": str(resource_id) if resource_id is not None else None,
        "ip": get_client_ip(request),
        "metadata": extra,
    }

    try:
        logger.info(json.dumps(payload, cls=DjangoJSONEncoder))
    except Exception as e:
        logger.error(
            json.dumps({
                "action": "audit_logging_failed",
                "original_action": action,
                "error": str(e),
            })
        )
