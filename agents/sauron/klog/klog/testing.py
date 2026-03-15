"""
Log capture for testing.

Usage:
    from klog import log
    from klog.testing import log_capture

    with log_capture() as logs:
        log.info("test", key="value")
    assert logs[0]["event"] == "test"
    assert logs[0]["key"] == "value"
"""

import threading
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, List, Optional


_log_capture: ContextVar[Optional[List[Dict[str, Any]]]] = ContextVar(
    "log_capture", default=None
)
_global_log_capture: Optional[List[Dict[str, Any]]] = None
_global_capture_lock = threading.Lock()


@contextmanager
def log_capture(global_mode: bool = False):
    """
    Capture logs emitted within the context scope.

    Args:
        global_mode: If True, capture across threads. Default is thread-local.

    Example:
        with log_capture() as logs:
            log.info("test", key="value")
        assert logs[0]["event"] == "test"
    """
    global _global_log_capture

    if global_mode:
        captured: List[Dict[str, Any]] = []
        with _global_capture_lock:
            _global_log_capture = captured
        try:
            yield captured
        finally:
            with _global_capture_lock:
                _global_log_capture = None
    else:
        captured = []
        token = _log_capture.set(captured)
        try:
            yield captured
        finally:
            _log_capture.reset(token)


def _capture_log(level: str, event: str, **kwargs) -> None:
    """Capture log to active capture contexts. Called by Logger._log."""
    global _global_log_capture
    entry = {"level": level, "event": event, **kwargs}

    capture = _log_capture.get()
    if capture is not None:
        capture.append(entry)

    if _global_log_capture is not None:
        with _global_capture_lock:
            if _global_log_capture is not None:
                _global_log_capture.append(entry)
