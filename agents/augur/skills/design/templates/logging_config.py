"""
Structured JSON logging — configure once, use everywhere.

Usage:
    from logging_config import log, configure_logging

    configure_logging(app_name="my_service")
    log.info("processing", component="api", items=10)
"""

import logging
import sys

import structlog


def configure_logging(app_name: str, level: str = "INFO", json_output: bool = True):
    """Configure structured logging. Call once at startup."""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers = [logging.StreamHandler(sys.stdout)]

    for name in ["kafka", "urllib3", "requests"]:
        logging.getLogger(name).setLevel(logging.WARNING)


log = structlog.get_logger()
