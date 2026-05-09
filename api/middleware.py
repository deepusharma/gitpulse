"""FastAPI middleware for structured request logging."""

import time
import logging
import structlog

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_struct_logger = structlog.stdlib.get_logger(__name__)
_stdlib_logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with path, method, status code, and latency.

    Also reads an optional ``X-Username`` header so requests can be
    correlated to a user without inspecting the body.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process a request and emit a structured log entry.

        Args:
            request: The incoming Starlette request.
            call_next: The next middleware or route handler.

        Returns:
            The response produced by the downstream handler.
        """
        start = time.perf_counter()
        username = request.headers.get("X-Username", "anonymous")
        status_code = 500  # default if handler raises

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:  # noqa: BLE001
            _stdlib_logger.error("Unhandled exception in request: %s", exc, exc_info=True)
            raise
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            try:
                _struct_logger.info(
                    "request",
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    username=username,
                )
            except Exception as log_exc:  # noqa: BLE001
                _stdlib_logger.warning("Failed to emit structured log: %s", log_exc)
