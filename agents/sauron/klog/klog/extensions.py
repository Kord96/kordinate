"""
Optional logging extensions — filters, validation, trace context, custom processors.

These are wired into core.py automatically when available.
Import directly if you need fine-grained control.

Usage:
    from klog.extensions import add_filter, trace_context, require_context

    add_filter("logger", ["run", "state"])

    with trace_context(service="my_service"):
        log.info("start")  # Has service + trace_id

    with require_context("task_id"):
        log.info("step", task_id=123)  # OK
        log.info("step")  # Raises RuntimeError
"""

import os
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, List, Optional, Set, Union

import structlog


# =============================================================================
# Field-Based Filtering
# =============================================================================

_filters: Dict[str, Set[str]] = {}
_excludes: Dict[str, Set[str]] = {}


def _parse_filter_string(filter_str: str) -> Dict[str, Set[str]]:
    """Parse "field1=val1,field2=val2" into {field: {values}}."""
    result: Dict[str, Set[str]] = {}
    if not filter_str:
        return result
    for part in filter_str.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        field, value = part.split("=", 1)
        field, value = field.strip(), value.strip()
        if field and value:
            result.setdefault(field, set()).add(value)
    return result


def add_filter(field: str, values: Union[str, List[str], Set[str], None]) -> None:
    """Only emit logs where field value is in allowed set. None to clear."""
    if values is None:
        _filters.pop(field, None)
        return
    if isinstance(values, str):
        values = {v.strip() for v in values.split(",")} if "," in values else {values}
    else:
        values = set(values)
    _filters[field] = values


def add_exclude(field: str, values: Union[str, List[str], Set[str], None]) -> None:
    """Drop logs where field value is in excluded set. None to clear."""
    if values is None:
        _excludes.pop(field, None)
        return
    if isinstance(values, str):
        values = {v.strip() for v in values.split(",")} if "," in values else {values}
    else:
        values = set(values)
    _excludes[field] = values


def clear_filter(field: str) -> None:
    _filters.pop(field, None)


def clear_exclude(field: str) -> None:
    _excludes.pop(field, None)


def clear_filters() -> None:
    _filters.clear()
    _excludes.clear()


def get_filters() -> Dict[str, Set[str]]:
    return {k: v.copy() for k, v in _filters.items()}


def get_excludes() -> Dict[str, Set[str]]:
    return {k: v.copy() for k, v in _excludes.items()}


def _apply_filters(logger, method_name, event_dict):
    """Structlog processor: drop logs not matching filters."""
    for field, excluded_values in _excludes.items():
        value = event_dict.get(field)
        if value is not None and value in excluded_values:
            raise structlog.DropEvent
    for field, allowed_values in _filters.items():
        value = event_dict.get(field)
        if value is not None and value not in allowed_values:
            raise structlog.DropEvent
    return event_dict


# =============================================================================
# Dimension Validation
# =============================================================================

_required_dims: ContextVar[Set[str]] = ContextVar("required_dims", default=set())
_global_required_dims: Set[str] = set()


def get_required_dims() -> Set[str]:
    return _required_dims.get() | _global_required_dims


@contextmanager
def require_context(*keys: str):
    """
    Require dimensions in all logs within scope. Raises RuntimeError if missing.

    Example:
        with require_context("task_id", "message"):
            log.info("step", task_id=123, message="foo")  # OK
            log.info("step")  # Raises RuntimeError
    """
    old = _required_dims.get()
    token = _required_dims.set(old | set(keys))
    try:
        yield
    finally:
        _required_dims.reset(token)


def require_dimensions(keys: List[str]) -> None:
    """Set global required dimensions (applies to all logs)."""
    global _global_required_dims
    _global_required_dims = set(keys)


def clear_required_dimensions() -> None:
    global _global_required_dims
    _global_required_dims = set()


def _validate_required_dims(event_dict: Dict[str, Any]) -> None:
    """Validate required dimensions are present. Raises RuntimeError."""
    required = get_required_dims()
    if not required:
        return
    missing = required - set(event_dict.keys())
    if missing:
        event = event_dict.get("event", "unknown")
        raise RuntimeError(
            f"Log missing required dimensions: {missing}. "
            f"Event: '{event}', got: {set(event_dict.keys())}"
        )


# =============================================================================
# Trace Context
# =============================================================================

_trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
_service_var: ContextVar[Optional[str]] = ContextVar("service", default=None)


def get_trace_id() -> Optional[str]:
    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    _trace_id_var.set(trace_id)


def clear_trace_id() -> None:
    _trace_id_var.set(None)


def get_service() -> Optional[str]:
    return _service_var.get()


def set_service(service: str) -> None:
    _service_var.set(service)


def clear_service() -> None:
    _service_var.set(None)


@contextmanager
def trace_context(service: str = None, trace_id: str = None):
    """
    Bind service and trace_id to all logs in scope.

    Example:
        with trace_context(service="my_service") as tid:
            log.info("start")  # Has service + trace_id
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())[:8]
    old_trace = _trace_id_var.get()
    old_service = _service_var.get()
    _trace_id_var.set(trace_id)
    if service:
        _service_var.set(service)
    try:
        yield trace_id
    finally:
        _trace_id_var.set(old_trace)
        _service_var.set(old_service)


def _add_trace_context(logger, method_name, event_dict):
    """Structlog processor: add trace_id and service from context."""
    trace_id = _trace_id_var.get()
    if trace_id:
        event_dict["trace_id"] = trace_id
    service = _service_var.get()
    if service:
        event_dict.setdefault("service", service)
    return event_dict


# =============================================================================
# Custom Processors
# =============================================================================

_custom_processors: List[Callable] = []


def add_processor(processor: Callable) -> None:
    """Register a custom structlog processor."""
    if processor not in _custom_processors:
        _custom_processors.append(processor)


def remove_processor(processor: Callable) -> None:
    if processor in _custom_processors:
        _custom_processors.remove(processor)


def clear_processors() -> None:
    _custom_processors.clear()


def _apply_custom_processors(logger, method_name, event_dict):
    for processor in _custom_processors:
        event_dict = processor(logger, method_name, event_dict)
    return event_dict


# =============================================================================
# Validation Hook
# =============================================================================

_validation_hook: Optional[Callable] = None


def set_validation_hook(hook: Optional[Callable]) -> None:
    """Register a validation hook called before each log."""
    global _validation_hook
    _validation_hook = hook


def get_validation_hook() -> Optional[Callable]:
    return _validation_hook


def _apply_validation_hook(logger, method_name, event_dict):
    if _validation_hook is not None:
        return _validation_hook(event_dict)
    return event_dict


# =============================================================================
# Integration with core.py
# =============================================================================


def _setup_filters(filters: Dict = None) -> None:
    """Called by configure_logging to set up filters from env + args."""
    for field, values in _parse_filter_string(os.getenv("LOG_FILTER", "")).items():
        add_filter(field, values)
    for field, values in _parse_filter_string(os.getenv("LOG_EXCLUDE", "")).items():
        add_exclude(field, values)
    if filters:
        for field, values in filters.items():
            add_filter(field, values)


def _get_processors() -> list:
    """Return extension processors for the structlog chain."""
    return [
        _apply_filters,
        _apply_validation_hook,
        _add_trace_context,
        _apply_custom_processors,
    ]
