"""Drive core API endpoints"""

import logging
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError

from drf_standardized_errors.handler import exception_handler as drf_exception_handler
from rest_framework import exceptions as drf_exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from ..monitoring_utils import log_audit_event

def exception_handler(exc, context):
    """Handle Django ValidationError as an accepted exception.

    For the parameters, see ``exception_handler``
    This code comes from twidi's gist:
    https://gist.github.com/twidi/9d55486c36b6a51bdcb05ce3a763e79f
    """
    if isinstance(exc, DjangoValidationError):
        exc = drf_exceptions.ValidationError(as_serializer_error(exc))

    response = drf_exception_handler(exc, context)
    request = context.get("request")
    view = context.get("view")

    view_name = view.__class__.__name__ if view else "UnknownView"
    resource_id = context.get("kwargs", {}).get("pk") or context.get("kwargs", {}).get("id")

    if isinstance(exc, drf_exceptions.PermissionDenied):
        request = context.get("request")
        view = context.get("view")

        view_name = view.__class__.__name__ if view else "UnknownView"
        resource_id = context.get("kwargs", {}).get("pk") or context.get("kwargs", {}).get("id")

        log_audit_event(
            action="PERMISSION_DENIED",
            user=getattr(request, "user", None),
            resource_id=resource_id,
            request=request,
            criticality="HIGH",
            view=view_name,
            path=request.path if request else None,
            method=request.method if request else None,
            reason=str(exc.detail) if hasattr(exc, "detail") else str(exc),
        )

    return response

# pylint: disable=unused-argument
@api_view(["GET"])
def get_frontend_configuration(request):
    """Returns the frontend configuration dict as configured in settings."""
    frontend_configuration = {
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
    }
    frontend_configuration.update(settings.FRONTEND_CONFIGURATION)
    return Response(frontend_configuration)
