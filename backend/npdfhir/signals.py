import structlog
from django.dispatch import receiver
from django_structlog import signals
from django_structlog.middlewares.request import get_request_header
import hashlib


@receiver(signals.bind_extra_request_metadata)
def bind_trace_id(request, logger, **kwargs):
    trace_id = get_request_header(request, "x-amzn-trace-id", "HTTP_X_AMZN_TRACE_ID")
    if trace_id:
        structlog.contextvars.bind_contextvars(trace_id=trace_id)


@receiver(signals.bind_extra_request_metadata)
def bind_user_id(request, logger, **kwargs):
    if hasattr(request, "user") and request.user.is_authenticated:
        # using a hashed id to make it opaque
        user_id = hashlib.sha256(str(request.user.id).encode()).hexdigest()

        structlog.contextvars.bind_contextvars(user_id=user_id, username=request.user.username)
