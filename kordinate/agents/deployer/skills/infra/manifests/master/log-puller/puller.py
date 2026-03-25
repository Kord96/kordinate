#!/usr/bin/env python3
"""Master log puller — pulls federation logs from gateway MinIO instances.

Periodically lists and downloads JSON Lines files from each gateway's
MinIO federate bucket, writes them to local directories for Alloy to
tail with loki.source.file.

No third-party dependencies — stdlib only.
"""

import argparse
import json
import os
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


def _list_objects(endpoint, bucket="federate"):
    """List objects in a MinIO bucket (anonymous access)."""
    url = f"{endpoint}/{bucket}?list-type=2"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        tree = ET.fromstring(resp.read())
        ns = tree.tag.split("}")[0] + "}" if "}" in tree.tag else ""
        return [
            elem.text
            for elem in tree.findall(f".//{ns}Key")
            if elem.text
        ]
    except Exception as exc:
        print(f"puller: list failed for {endpoint}: {exc}", flush=True)
        return []


def _download_object(endpoint, bucket, key):
    """Download an object from MinIO (anonymous access)."""
    url = f"{endpoint}/{bucket}/{key}"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        return resp.read()
    except Exception as exc:
        print(f"puller: download failed {key}: {exc}", flush=True)
        return None


def _load_gateways(registry_path):
    """Load gateway list from gateway-registry ConfigMap mount."""
    try:
        with open(registry_path) as f:
            data = json.load(f) if registry_path.endswith(".json") else None
            if data is None:
                import yaml
                f.seek(0)
                data = yaml.safe_load(f)
        return data.get("gateways", [])
    except ImportError:
        # No yaml module — parse manually
        gateways = []
        with open(registry_path) as f:
            content = f.read()
        import re
        for match in re.finditer(
            r"name:\s*[\"']?(\w+)[\"']?\s+tailscale_ip:\s*[\"']?([\d.]+)[\"']?",
            content,
        ):
            gateways.append({"name": match.group(1), "tailscale_ip": match.group(2)})
        return gateways
    except Exception as exc:
        print(f"puller: failed to load registry: {exc}", flush=True)
        return []


def _pull_gateway(gateway, output_base, port=9000):
    """Pull new log files from a gateway's MinIO."""
    name = gateway["name"]
    ip = gateway["tailscale_ip"]
    endpoint = f"http://{ip}:{port}"
    output_dir = os.path.join(output_base, name)
    os.makedirs(output_dir, exist_ok=True)

    # List remote objects
    remote_keys = _list_objects(endpoint)
    if not remote_keys:
        return 0

    # Check what we already have
    local_files = set(os.listdir(output_dir))

    downloaded = 0
    for key in remote_keys:
        if key in local_files:
            continue
        data = _download_object(endpoint, "federate", key)
        if data:
            path = os.path.join(output_dir, key)
            with open(path, "wb") as f:
                f.write(data)
            downloaded += 1

    return downloaded


def _cleanup(output_base, retention):
    """Delete local files older than retention seconds."""
    cutoff = time.time() - retention
    for dirn in os.listdir(output_base):
        dirpath = os.path.join(output_base, dirn)
        if not os.path.isdir(dirpath):
            continue
        for name in os.listdir(dirpath):
            path = os.path.join(dirpath, name)
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)


def main():
    parser = argparse.ArgumentParser(description="Master log puller")
    parser.add_argument(
        "--registry",
        default="/etc/gateway-registry/gateways.yaml",
        help="Path to gateway registry YAML",
    )
    parser.add_argument(
        "--output-dir",
        default="/data/federate",
        help="Directory to write pulled log files",
    )
    parser.add_argument(
        "--interval", type=int, default=60, help="Seconds between pulls"
    )
    parser.add_argument(
        "--retention", type=int, default=7200, help="Seconds to keep local files"
    )
    parser.add_argument(
        "--port", type=int, default=9000, help="MinIO S3 port on gateways"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"puller: starting (interval={args.interval}s, output={args.output_dir})",
          flush=True)

    while True:
        gateways = _load_gateways(args.registry)
        if not gateways:
            print("puller: no gateways found in registry", flush=True)
        else:
            for gw in gateways:
                n = _pull_gateway(gw, args.output_dir, args.port)
                if n > 0:
                    print(f"puller: pulled {n} new files from {gw['name']}",
                          flush=True)

        _cleanup(args.output_dir, args.retention)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
