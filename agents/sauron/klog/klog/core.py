"""
Core structured logging — configure once, use everywhere.

Usage:
    from klog import log, configure_logging

    configure_logging(app_name="my_service")
    log.info("processing", phase="startup", items=10)

    with log.context(stage="execute"):
        log.info("step")  # Has stage

Environment Variables:
    LOG_LEVEL: DEBUG, INFO, WARNING, ERROR (default: INFO)
    LOG_FILTER: Comma-separated field=value filters
    LOG_EXCLUDE: Comma-separated field=value exclusions
    LOG_API_URL: API endpoint for log pushes (optional)
"""

import logging
import os
import sys
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, List, Optional, Set, Union

import structlog
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_API_URL = os.getenv("LOG_API_URL", os.getenv("ENV_API_URL", ""))

_session_id: Optional[str] = None
_configured = False


def get_session_id() -> Optional[str]:
    """Get the current session_id (set during configure_logging)."""
    return _session_id


def is_configured() -> bool:
    """Check if logging has been configured."""
    return _configured


class LoggingAlreadyConfiguredError(Exception):
    """Raised when configure_logging is called more than once."""
    pass


# =============================================================================
# Log Context — dimension binding
# =============================================================================

_log_context_dims: ContextVar[Dict[str, Any]] = ContextVar("log_context_dims", default={})


def get_log_context() -> Dict[str, Any]:
    """Get current log context dimensions."""
    return _log_context_dims.get().copy()


@contextmanager
def log_context(**dims: Any):
    """
    Bind dimensions to all logs in scope.

    Dimensions are inherited by nested contexts (inner overrides outer).

    Example:
        with log_context(stage="execute", service="scheduler"):
            log.info("processing")  # Has stage + service
            with log_context(batch_id="abc123"):
                log.info("step")  # Has stage + service + batch_id
    """
    old_dims = _log_context_dims.get()
    new_dims = {**old_dims, **dims}
    token = _log_context_dims.set(new_dims)
    try:
        yield
    finally:
        _log_context_dims.reset(token)


@contextmanager
def get_context(**dims: Any):
    """
    Like log_context but filters out None values.

    Convenient when building contexts from optional parameters.
    """
    filtered = {k: v for k, v in dims.items() if v is not None}
    with log_context(**filtered):
        yield


# =============================================================================
# Structlog Processors
# =============================================================================


def _add_session_id(logger, method_name, event_dict):
    """Add session_id to all logs."""
    if _session_id:
        event_dict["session_id"] = _session_id
    return event_dict


def _add_log_id(logger, method_name, event_dict):
    """Add unique log_id to each log entry."""
    event_dict["log_id"] = str(uuid.uuid4())[:8]
    return event_dict


# =============================================================================
# Logger
# =============================================================================


class Logger:
    """
    Structured logger with context integration.

    Merges log_context dimensions into every log call automatically.

    Usage:
        log.info("event", key="value")

        with log.context(stage="execute"):
            log.info("processing")  # Auto-includes stage
    """

    def __init__(self):
        self._bound_context: Dict[str, Any] = {}
        # Extension hooks — set by extensions.py and testing.py
        self._validate_hook: Optional[Callable] = None
        self._capture_hook: Optional[Callable] = None

    def _log(self, level: str, event: str, **kwargs) -> None:
        """Log with context dimensions merged in."""
        ctx_dims = get_log_context()
        merged = {**self._bound_context, **ctx_dims, **kwargs}

        if self._validate_hook:
            self._validate_hook({"event": event, **merged})

        if self._capture_hook:
            self._capture_hook(level, event, **merged)

        logger = structlog.get_logger()
        getattr(logger, level)(event, **merged)

    @property
    def context(self):
        """Get the log_context context manager."""
        return log_context

    @property
    def get_context(self):
        """Get the get_context context manager (filters None values)."""
        return get_context

    def bind(self, **kwargs):
        """Return a new logger with bound context."""
        new_logger = Logger()
        new_logger._bound_context = {**self._bound_context, **kwargs}
        new_logger._validate_hook = self._validate_hook
        new_logger._capture_hook = self._capture_hook
        return new_logger

    def unbind(self, *keys):
        """Return a new logger without specified keys."""
        new_logger = Logger()
        new_logger._bound_context = {
            k: v for k, v in self._bound_context.items() if k not in keys
        }
        new_logger._validate_hook = self._validate_hook
        new_logger._capture_hook = self._capture_hook
        return new_logger

    def debug(self, event: str, **kwargs) -> None:
        self._log("debug", event, **kwargs)

    def info(self, event: str, **kwargs) -> None:
        self._log("info", event, **kwargs)

    def warning(self, event: str, **kwargs) -> None:
        self._log("warning", event, **kwargs)

    def error(self, event: str, **kwargs) -> None:
        self._log("error", event, **kwargs)

    def exception(self, event: str, **kwargs) -> None:
        self._log("exception", event, **kwargs)

    def critical(self, event: str, **kwargs) -> None:
        self._log("critical", event, **kwargs)

    warn = warning
    fatal = critical


# Single logger instance
log = Logger()


# =============================================================================
# configure_logging
# =============================================================================


def configure_logging(
    app_name: str,
    level: str = None,
    json_output: bool = True,
    filters: Dict[str, Union[List[str], Set[str], str]] = None,
    session_id: str = None,
    api_url: str = None,
    extra_processors: List[Callable] = None,
) -> None:
    """
    Configure structured logging. Call once per process.

    Args:
        app_name: Application name (used for API log routing)
        level: Log level override (default: LOG_LEVEL env var)
        json_output: JSON (True) or pretty console (False)
        filters: Initial filters as dict, e.g. {"logger": ["run", "state"]}
        session_id: Optional session ID (auto-generated if not provided)
        api_url: Optional API URL for log pushing
        extra_processors: Additional structlog processors to include

    Raises:
        LoggingAlreadyConfiguredError: If already configured
    """
    global _configured, _session_id

    if _configured:
        raise LoggingAlreadyConfiguredError(
            "configure_logging() can only be called once per process."
        )

    if session_id:
        _session_id = session_id

    log_level = (level or LOG_LEVEL).upper()

    # Apply filters if extensions are available
    try:
        from klog.extensions import _setup_filters
        _setup_filters(filters)
    except ImportError:
        pass

    # Generate session_id
    if _session_id is None:
        from datetime import datetime
        ts = datetime.now().strftime("%y%m%d-%H%M%S")
        _session_id = f"{ts}-{str(uuid.uuid4())[:4]}"

    # Build processor chain
    processors = [
        structlog.stdlib.filter_by_level,
    ]

    # Add extension processors if available
    try:
        from klog.extensions import _get_processors
        processors.extend(_get_processors())
    except ImportError:
        pass

    processors.extend([
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _add_session_id,
        _add_log_id,
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.MODULE],
            additional_ignores=["klog.core", "klog.logger"],
        ),
    ])

    if extra_processors:
        processors.extend(extra_processors)

    processors.extend([
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        (
            structlog.processors.JSONRenderer()
            if json_output
            else structlog.dev.ConsoleRenderer(pad_event_to=0)
        ),
    ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level))
    root.handlers = []

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(getattr(logging, log_level))
    root.addHandler(stdout_handler)

    # API push handler
    effective_api_url = api_url or LOG_API_URL
    if effective_api_url:
        try:
            from klog.api_push import APIPushHandler
            api_handler = APIPushHandler(effective_api_url, app_name)
            api_handler.setLevel(getattr(logging, log_level))
            root.addHandler(api_handler)
        except ImportError:
            pass

    # Suppress noisy loggers
    for name in ["kafka", "urllib3", "requests"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    _configured = True

    # Wire up extension hooks to the logger
    try:
        from klog.extensions import _validate_required_dims
        log._validate_hook = _validate_required_dims
    except ImportError:
        pass

    try:
        from klog.testing import _capture_log
        log._capture_hook = _capture_log
    except ImportError:
        pass
