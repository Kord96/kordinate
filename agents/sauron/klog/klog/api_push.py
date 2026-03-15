"""
APIPushHandler - async batched log pushing to an HTTP API.

This is an optional component for infrastructure environments.
It is only activated when LOG_API_URL (or ENV_API_URL) is set.
"""

import atexit
import json
import logging
import queue
import sys
import threading
import time
import urllib.request
from typing import List


class APIPushHandler(logging.Handler):
    """Batches logs and sends async to per-env API."""

    def __init__(
        self,
        api_url: str,
        app_name: str,
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        super().__init__()
        self.api_url = api_url.rstrip("/")
        self.app_name = app_name
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: queue.Queue = queue.Queue()
        self._shutdown = False
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()
        atexit.register(self._shutdown_handler)

    def emit(self, record: logging.LogRecord) -> None:
        if self._shutdown:
            return
        try:
            msg = self.format(record)
            if msg:
                self._queue.put(msg)
        except Exception:
            self.handleError(record)

    def _flush_loop(self) -> None:
        batch = []
        last_flush = time.time()

        while not self._shutdown:
            try:
                try:
                    msg = self._queue.get(timeout=1.0)
                    batch.append(msg)
                except queue.Empty:
                    pass

                now = time.time()
                if len(batch) >= self.batch_size or (
                    batch and now - last_flush >= self.flush_interval
                ):
                    self._send_batch(batch)
                    batch = []
                    last_flush = now
            except Exception:
                pass

        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: List[str]) -> None:
        if not batch:
            return
        try:
            entries = []
            for msg in batch:
                try:
                    entries.append(json.loads(msg))
                except json.JSONDecodeError:
                    entries.append(
                        {"event": msg, "level": "info", "logger": "unknown"}
                    )

            payload = json.dumps({"service": self.app_name, "entries": entries}).encode(
                "utf-8"
            )
            req = urllib.request.Request(
                f"{self.api_url}/logs",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status >= 400:
                    print(
                        f"[APIPushHandler] API returned {resp.status}: {resp.read().decode()}",
                        file=sys.stderr,
                    )
        except urllib.error.HTTPError as e:
            print(
                f"[APIPushHandler] API error {e.code}: {e.read().decode()}",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"[APIPushHandler] Failed to send logs: {e}", file=sys.stderr)

    def _shutdown_handler(self) -> None:
        self._shutdown = True
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
