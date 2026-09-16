import json
import logging
import time
from typing import Literal
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

logger = logging.getLogger("monitoring_audit")

CriticalityLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_client_ip(request) -> str | None:
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
    **extra,
):
    user_obj = user or getattr(request, "user", None)
    user_id = (
        str(user_obj.id)
        if (user_obj and getattr(user_obj, "is_authenticated", False))
        else None
    )
    normalized_criticality = str(criticality).upper() if criticality else "LOW"

    # Nettoyage des extra pour éviter les échecs JSON sur les objets Django
    clean_extra = {}
    for k, v in extra.items():
        if v is None or isinstance(v, (int, float, str, bool, list, dict)):
            clean_extra[k] = v
        else:
            clean_extra[k] = str(v)

    payload = {
        "timestamp": time.time(),
        "datetime": timezone.now().isoformat(),
        "action": action,
        "criticality": normalized_criticality,
        "user_id": user_id,
        "resource_id": str(resource_id) if resource_id is not None else None,
        "ip": get_client_ip(request),
        "metadata": clean_extra,
    }

    try:
        log_entry = json.dumps(payload, cls=DjangoJSONEncoder)
        logger.info(log_entry)
    except Exception as e:
        logger.error(
            json.dumps({
                "action": "audit_logging_failed",
                "original_action": action,
                "error": str(e),
            })
        )
