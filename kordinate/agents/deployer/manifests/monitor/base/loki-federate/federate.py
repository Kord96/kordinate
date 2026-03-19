#!/usr/bin/env python3
"""Loki federation sidecar.

Stateless HTTP server that exposes a /federate endpoint.  On each request it
queries the local Loki instance for recent logs and returns them in the Loki
push-API JSON format so that a remote Alloy (or Promtail) can ingest them
via ``loki.source.api`` or a direct POST to ``/loki/api/v1/push``.

Optionally writes log batches as JSON Lines files to a directory (e.g. an
NFS mount) with automatic rotation/cleanup.

No third-party dependencies -- stdlib only.
"""

import argparse
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


def _ns(epoch: float) -> str:
    """Convert a Unix epoch (float seconds) to a nanosecond string."""
    return str(int(epoch * 1_000_000_000))


def _query_loki(window: int) -> dict:
    """Query Loki query_range and return a push-API payload.

    The push-API format expected by ``/loki/api/v1/push`` is::

        {
          "streams": [
            {
              "stream": {"label": "value", ...},
              "values": [["<nanosecond-ts>", "<log line>"], ...]
            },
            ...
          ]
        }

    Loki ``query_range`` returns results grouped by stream (matrix /
    streams result type) which maps naturally to the push format.
    """
    now = time.time()
    start = now - window
    params = urllib.parse.urlencode({
        "query": '{__name__=~".+"}',  # match all streams
        "start": _ns(start),
        "end": _ns(now),
        "direction": "forward",
        "limit": 5000,
    })
    url = f"http://localhost:3100/loki/api/v1/query_range?{params}"

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    # data.data.result is a list of stream entries.
    # Each entry: {"stream": {labels}, "values": [["ts","line"], ...]}
    streams = []
    for entry in data.get("data", {}).get("result", []):
        streams.append({
            "stream": entry.get("stream", {}),
            "values": entry.get("values", []),
        })
    return {"streams": streams}


class FederateHandler(BaseHTTPRequestHandler):
    """Minimal request handler -- only /federate is served."""

    window: int = 90  # set from CLI args before server starts

    def do_GET(self):  # noqa: N802 (stdlib naming)
        if self.path.split("?")[0] != "/federate":
            self.send_error(404, "Not Found -- use /federate")
            return

        try:
            payload = _query_loki(self.window)
        except urllib.error.URLError as exc:
            self.send_error(502, f"Loki unreachable: {exc.reason}")
            return
        except Exception as exc:
            self.send_error(500, f"Internal error: {exc}")
            return

        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # Silence per-request log lines (too noisy under periodic scraping).
    def log_message(self, fmt, *args):
        pass


# ─── File-based log writer ─────────────────────────────────────────


def _write_batch(output_dir: str, window: int):
    """Query Loki and write a JSON Lines file to output_dir.

    Each line is a JSON object:
        {"stream": {labels}, "ts": "<nano-ts>", "line": "..."}
    """
    try:
        payload = _query_loki(window)
    except Exception as exc:
        print(f"file-writer: loki query failed: {exc}", flush=True)
        return

    lines = []
    for stream_entry in payload.get("streams", []):
        labels = stream_entry.get("stream", {})
        for ts, line in stream_entry.get("values", []):
            lines.append(json.dumps({
                "stream": labels,
                "ts": ts,
                "line": line,
            }))

    if not lines:
        return

    ts_str = str(int(time.time()))
    filename = os.path.join(output_dir, f"{ts_str}.json")
    with open(filename, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")

    print(f"file-writer: wrote {len(lines)} entries to {filename}", flush=True)


def _cleanup_old_files(output_dir: str, retention: int):
    """Delete files older than retention seconds from output_dir."""
    cutoff = time.time() - retention
    try:
        for name in os.listdir(output_dir):
            path = os.path.join(output_dir, name)
            if not os.path.isfile(path):
                continue
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
                print(f"file-writer: removed expired {name}", flush=True)
    except Exception as exc:
        print(f"file-writer: cleanup error: {exc}", flush=True)


def _file_writer_loop(output_dir: str, interval: int, retention: int,
                      window: int):
    """Background loop: write batches and clean up old files."""
    print(f"file-writer: output_dir={output_dir} interval={interval}s "
          f"retention={retention}s window={window}s", flush=True)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    while True:
        _write_batch(output_dir, window)
        _cleanup_old_files(output_dir, retention)
        time.sleep(interval)


# ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Loki federation sidecar")
    parser.add_argument(
        "--port", type=int, default=3101,
        help="Port to listen on (default: 3101)",
    )
    parser.add_argument(
        "--window", type=int, default=90,
        help="Lookback window in seconds (default: 90)",
    )
    parser.add_argument(
        "--output-dir", type=str, default="",
        help="Directory for JSON Lines file output (empty = disabled)",
    )
    parser.add_argument(
        "--interval", type=int, default=60,
        help="Seconds between file writes (default: 60)",
    )
    parser.add_argument(
        "--retention", type=int, default=3600,
        help="Delete files older than this many seconds (default: 3600)",
    )
    args = parser.parse_args()

    FederateHandler.window = args.window

    # Start file writer thread if output-dir is set
    if args.output_dir:
        # Use interval+30s as the query window so no logs are missed
        file_window = args.interval + 30
        writer = threading.Thread(
            target=_file_writer_loop,
            args=(args.output_dir, args.interval, args.retention, file_window),
            daemon=True,
        )
        writer.start()

    server = HTTPServer(("0.0.0.0", args.port), FederateHandler)
    print(f"loki-federate listening on :{args.port}  window={args.window}s",
          flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("loki-federate shut down", flush=True)


if __name__ == "__main__":
    main()
