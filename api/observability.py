"""Observability bootstrap for GitPulse API.

Call configure_observability() once at startup (before app creation).
"""

import logging
import os
import structlog

logger = logging.getLogger(__name__)


def configure_observability() -> None:
    """Initialise structlog and, if SENTRY_DSN is set, Sentry.

    Structlog renders as JSON in production (LOG_FORMAT=json, the default)
    or as human-readable console output when LOG_FORMAT=console.

    Sentry is completely optional — if SENTRY_DSN is not set this function
    is a no-op for Sentry and adds zero overhead.
    """
    log_format = os.getenv("LOG_FORMAT", "json").lower()

    if log_format == "console":
        renderer = structlog.dev.ConsoleRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _init_sentry()


def _init_sentry() -> None:
    """Initialise Sentry SDK if SENTRY_DSN is present in the environment.

    Imported lazily so the SDK is not even loaded when the DSN is absent.
    """
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        logger.info("SENTRY_DSN not set — Sentry disabled.")
        return

    try:
        import sentry_sdk  # noqa: PLC0415 — intentional lazy import

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
        logger.info("Sentry initialised.")
    except ImportError:
        logger.warning(
            "sentry-sdk is not installed. "
            "Install with: uv pip install 'gitpulse[observability]'"
        )
