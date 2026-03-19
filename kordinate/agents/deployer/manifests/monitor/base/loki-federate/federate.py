#!/usr/bin/env python3
"""Loki federation sidecar — MinIO-based.

Periodically queries the local Loki instance for recent logs and writes
them as JSON Lines objects to a MinIO bucket ("federate").  Old objects
are garbage-collected after --retention seconds.

The MinIO "federate" bucket is configured with an anonymous read/write
policy so that no S3 signing is needed — all operations are plain HTTP
via urllib (stdlib only, no boto3).

No HTTP server — this is a pure push-based loop.
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


# ─── Loki helpers ─────────────────────────────────────────────────


def _ns(epoch: float) -> str:
    """Convert a Unix epoch (float seconds) to a nanosecond string."""
    return str(int(epoch * 1_000_000_000))


def _query_loki(window: int) -> list[dict]:
    """Query Loki query_range and return a flat list of log entries.

    Each entry is a dict: {"stream": {labels}, "ts": "nano-ts", "line": "..."}.
    """
    now = time.time()
    start = now - window
    params = urllib.parse.urlencode({
        "query": '{__name__=~".+"}',
        "start": _ns(start),
        "end": _ns(now),
        "direction": "forward",
        "limit": 5000,
    })
    url = f"http://localhost:3100/loki/api/v1/query_range?{params}"

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    entries = []
    for stream_entry in data.get("data", {}).get("result", []):
        labels = stream_entry.get("stream", {})
        for ts, line in stream_entry.get("values", []):
            entries.append({"stream": labels, "ts": ts, "line": line})
    return entries


# ─── MinIO / S3 helpers (anonymous access, no signing) ───────────


def _minio_url(endpoint: str, path: str) -> str:
    """Build a full MinIO URL."""
    return f"{endpoint.rstrip('/')}/{path.lstrip('/')}"


def _ensure_bucket(endpoint: str, bucket: str):
    """Create the bucket if it doesn't exist (PUT /<bucket>).

    Ignores 409 BucketAlreadyOwnedByYou.
    """
    url = _minio_url(endpoint, bucket)
    req = urllib.request.Request(url, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
        print(f"minio: created bucket '{bucket}'", flush=True)
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            print(f"minio: bucket '{bucket}' already exists", flush=True)
        else:
            raise


def _set_bucket_policy(endpoint: str, bucket: str):
    """Set an anonymous read/write policy on the bucket.

    This allows all S3 operations without authentication, which is fine
    for internal cluster traffic.
    """
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket}",
                f"arn:aws:s3:::{bucket}/*",
            ],
        }],
    })
    url = _minio_url(endpoint, f"{bucket}?policy")
    req = urllib.request.Request(
        url,
        method="PUT",
        data=policy.encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
        print(f"minio: set anonymous policy on '{bucket}'", flush=True)
    except urllib.error.HTTPError as exc:
        print(f"minio: failed to set bucket policy: {exc.code} {exc.reason}",
              flush=True)


def _put_object(endpoint: str, bucket: str, key: str, data: bytes):
    """Upload an object (PUT /<bucket>/<key>)."""
    url = _minio_url(endpoint, f"{bucket}/{key}")
    req = urllib.request.Request(
        url,
        method="PUT",
        data=data,
        headers={"Content-Type": "application/x-ndjson"},
    )
    with urllib.request.urlopen(req, timeout=30):
        pass


def _list_objects(endpoint: str, bucket: str) -> list[str]:
    """List object keys in the bucket (GET /<bucket>?list-type=2)."""
    url = _minio_url(endpoint, f"{bucket}?list-type=2")
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read()

    root = ET.fromstring(body)
    # The namespace in the ListBucketResult XML
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    keys = []
    for contents in root.findall(f"{ns}Contents"):
        key_el = contents.find(f"{ns}Key")
        if key_el is not None and key_el.text:
            keys.append(key_el.text)
    return keys


def _delete_object(endpoint: str, bucket: str, key: str):
    """Delete an object (DELETE /<bucket>/<key>)."""
    url = _minio_url(endpoint, f"{bucket}/{key}")
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise


# ─── Main loop ────────────────────────────────────────────────────


def _write_batch(endpoint: str, bucket: str, window: int):
    """Query Loki and write a JSON Lines object to MinIO."""
    try:
        entries = _query_loki(window)
    except Exception as exc:
        print(f"federate: loki query failed: {exc}", flush=True)
        return

    if not entries:
        return

    lines = [json.dumps(e) for e in entries]
    data = ("\n".join(lines) + "\n").encode()

    key = f"{int(time.time())}.jsonl"
    try:
        _put_object(endpoint, bucket, key, data)
        print(f"federate: wrote {len(entries)} entries to {bucket}/{key}",
              flush=True)
    except Exception as exc:
        print(f"federate: failed to write {key}: {exc}", flush=True)


def _cleanup_old_objects(endpoint: str, bucket: str, retention: int):
    """Delete objects older than retention seconds."""
    cutoff = time.time() - retention
    try:
        keys = _list_objects(endpoint, bucket)
    except Exception as exc:
        print(f"federate: list objects failed: {exc}", flush=True)
        return

    for key in keys:
        # Keys are "<epoch>.jsonl" — parse the timestamp from the name
        try:
            ts = int(key.split(".")[0])
        except (ValueError, IndexError):
            continue
        if ts < cutoff:
            try:
                _delete_object(endpoint, bucket, key)
                print(f"federate: removed expired {key}", flush=True)
            except Exception as exc:
                print(f"federate: failed to delete {key}: {exc}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Loki federation sidecar (MinIO-based)")
    parser.add_argument(
        "--window", type=int, default=90,
        help="Lookback window in seconds (default: 90)",
    )
    parser.add_argument(
        "--interval", type=int, default=60,
        help="Seconds between pushes (default: 60)",
    )
    parser.add_argument(
        "--retention", type=int, default=3600,
        help="Delete objects older than this many seconds (default: 3600)",
    )
    args = parser.parse_args()

    endpoint = os.environ.get(
        "MINIO_ENDPOINT", "http://minio.monitor.svc.cluster.local:9000")
    bucket = "federate"

    # Use interval+30s as the query window so no logs are missed between
    # push cycles.
    window = args.interval + 30

    print(f"federate: endpoint={endpoint} bucket={bucket} "
          f"interval={args.interval}s retention={args.retention}s "
          f"window={window}s", flush=True)

    # Create bucket and set anonymous policy on startup
    while True:
        try:
            _ensure_bucket(endpoint, bucket)
            _set_bucket_policy(endpoint, bucket)
            break
        except Exception as exc:
            print(f"federate: waiting for MinIO: {exc}", flush=True)
            time.sleep(5)

    # Main loop
    while True:
        _write_batch(endpoint, bucket, window)
        _cleanup_old_objects(endpoint, bucket, args.retention)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
