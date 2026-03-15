"""
klog - Structured JSON logging with context binding and validation.

Quick start:
    from klog import log, configure_logging

    configure_logging(app_name="my_service")
    log.info("hello", key="value")

Context binding:
    with log.context(stage="execute"):
        log.info("step")  # Has stage

Extensions (optional):
    from klog.extensions import trace_context, require_context, add_filter
    from klog.testing import log_capture
"""

# Core — always available
from klog.core import (
    Logger,
    LoggingAlreadyConfiguredError,
    configure_logging,
    get_context,
    get_log_context,
    get_session_id,
    is_configured,
    log,
    log_context,
)

# Extensions — optional, imported for convenience
try:
    from klog.extensions import (
        add_exclude,
        add_filter,
        add_processor,
        clear_exclude,
        clear_filter,
        clear_filters,
        clear_processors,
        clear_required_dimensions,
        clear_service,
        clear_trace_id,
        get_excludes,
        get_filters,
        get_required_dims,
        get_service,
        get_trace_id,
        get_validation_hook,
        remove_processor,
        require_context,
        require_dimensions,
        set_service,
        set_trace_id,
        set_validation_hook,
        trace_context,
    )
except ImportError:
    pass

# Testing — optional
try:
    from klog.testing import log_capture
except ImportError:
    pass

__all__ = [
    # Core
    "Logger",
    "LoggingAlreadyConfiguredError",
    "configure_logging",
    "get_context",
    "get_log_context",
    "get_session_id",
    "is_configured",
    "log",
    "log_context",
    # Extensions
    "add_exclude",
    "add_filter",
    "add_processor",
    "clear_exclude",
    "clear_filter",
    "clear_filters",
    "clear_processors",
    "clear_required_dimensions",
    "clear_service",
    "clear_trace_id",
    "get_excludes",
    "get_filters",
    "get_required_dims",
    "get_service",
    "get_trace_id",
    "get_validation_hook",
    "remove_processor",
    "require_context",
    "require_dimensions",
    "set_service",
    "set_trace_id",
    "set_validation_hook",
    "trace_context",
    # Testing
    "log_capture",
]
