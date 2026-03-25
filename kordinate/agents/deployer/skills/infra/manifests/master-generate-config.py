#!/usr/bin/env python3
"""
Generate master alloy.yaml and gateway-registry.yaml from profile/config.yaml.

Single source of truth — all gateway IPs, ports, and cluster names come
from profile/config.yaml. No separate gateway-ips.yaml needed.

Reads:
  - profile/config.yaml  (clusters.*.gateway_tailscale_ip, services.registry)

Writes:
  - master/base/alloy.yaml
  - master/base/gateway-registry.yaml

Usage:
  python3 generate-config.py                   # from the master/ directory
  python3 generate-config.py --dry-run         # print to stdout, don't write
"""

import argparse
import os
import sys

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, "base")
PROFILE_CONFIG = os.path.join(
    SCRIPT_DIR, "..", "..", "..", "..", "profile", "config.yaml"
)

PORTS = {"metrics": 9090, "minio": 9000}


def load_config():
    with open(PROFILE_CONFIG) as f:
        return yaml.safe_load(f)


def build_gateway_list(profile):
    gateways = []
    for name in sorted(profile["clusters"].keys()):
        cluster = profile["clusters"][name]
        gw_ip = cluster.get("gateway_tailscale_ip")
        if not gw_ip:
            print(
                f"WARNING: cluster '{name}' has no gateway_tailscale_ip — skipping",
                file=sys.stderr,
            )
            continue
        registry = cluster.get("services", {}).get("registry", {})
        gateways.append(
            {
                "name": name,
                "tailscale_ip": gw_ip,
                "ports": dict(PORTS),
                "registry": f"{registry.get('host', 'localhost')}:{registry.get('port', 5000)}"
                if registry
                else None,
            }
        )
    return gateways


# ---------------------------------------------------------------------------
# alloy.yaml
# ---------------------------------------------------------------------------


def gen_alloy_config(gateways):
    L = []

    L.append("// " + "=" * 51)
    L.append("// METRICS — pull from all Gateway Proms via /federate")
    L.append("// " + "=" * 51)
    L.append("")

    for gw in gateways:
        L.append(f'prometheus.scrape "federate_{gw["name"]}" {{')
        L.append(f"  targets = [{{")
        L.append(f'    __address__ = "{gw["tailscale_ip"]}:{gw["ports"]["metrics"]}",')
        L.append(f"  }}]")
        L.append(f'  metrics_path    = "/federate"')
        L.append(f'  params          = {{ "match[]" = ["{{__name__=~\\".+\\"}}"] }}')
        L.append(f'  scrape_interval = "60s"')
        L.append(f'  scrape_timeout  = "25s"')
        L.append(f"  honor_labels    = true")
        L.append(f"  forward_to      = [prometheus.remote_write.master.receiver]")
        L.append(f"}}")
        L.append("")

    L.append('prometheus.remote_write "master" {')
    L.append("  endpoint {")
    L.append(
        '    url = "http://prometheus.master.svc.cluster.local:9191/api/v1/write"'
    )
    L.append("  }")
    L.append("}")
    L.append("")

    L.append("// " + "=" * 51)
    L.append("// LOGS — tail files fetched by puller sidecar from gateway MinIO")
    L.append("// " + "=" * 51)
    L.append("")

    for gw in gateways:
        n = gw["name"]
        L.append(f'local.file_match "logs_{n}" {{')
        L.append(f"  path_targets = [{{")
        L.append(f'    __path__ = "/data/federate/{n}/*.jsonl",')
        L.append(f'    cluster  = "{n}",')
        L.append(f"  }}]")
        L.append(f"}}")
        L.append("")
        L.append(f'loki.source.file "logs_{n}" {{')
        L.append(f"  targets    = local.file_match.logs_{n}.targets")
        L.append(f"  forward_to = [loki.process.federate.receiver]")
        L.append(f"}}")
        L.append("")

    L.append('loki.process "federate" {')
    L.append("  stage.json {")
    L.append("    expressions = {")
    for label in [
        "app",
        "component",
        "namespace",
        "cluster",
        "node",
        "pod",
        "container",
        "level",
        "consumer",
    ]:
        L.append(f'      stream_{label:12s} = "stream.{label}",')
    L.append('      original_line    = "line",')
    L.append("    }")
    L.append("  }")
    L.append("  stage.labels {")
    L.append("    values = {")
    for label in [
        "app",
        "component",
        "namespace",
        "cluster",
        "node",
        "pod",
        "container",
        "level",
        "consumer",
    ]:
        L.append(f'      {label:12s} = "stream_{label}",')
    L.append("    }")
    L.append("  }")
    L.append('  stage.output { source = "original_line" }')
    L.append("  forward_to = [loki.write.master.receiver]")
    L.append("}")
    L.append("")
    L.append('loki.write "master" {')
    L.append("  endpoint {")
    L.append(
        '    url = "http://loki.master.svc.cluster.local:3100/loki/api/v1/push"'
    )
    L.append("  }")
    L.append("}")

    return L


def gen_alloy_yaml(gateways):
    config_lines = gen_alloy_config(gateways)
    indented = "\n".join("    " + l if l else "" for l in config_lines)

    out = f"""## Generated by generate-config.py — do not edit directly.
## Source: profile/config.yaml
## Regenerate: cd master && python3 generate-config.py
apiVersion: v1
kind: ConfigMap
metadata:
  name: alloy-config
  labels:
    app: monitoring
    component: alloy
data:
  config.alloy: |
{indented}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alloy
  labels:
    app: monitoring
    component: alloy
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: monitoring
      component: alloy
  template:
    metadata:
      labels:
        app: monitoring
        component: alloy
    spec:
      containers:
        - name: alloy
          image: grafana/alloy:v1.5.1
          args: [run, /etc/alloy/config.alloy, --stability.level=generally-available]
          resources:
            requests: {{ cpu: 200m, memory: 256Mi }}
            limits: {{ memory: 1Gi }}
          volumeMounts:
            - name: config
              mountPath: /etc/alloy
            - name: federate-logs
              mountPath: /data/federate
              readOnly: true
        - name: log-puller
          image: docker.io/library/log-puller:latest
          imagePullPolicy: Never
          args:
            - --registry=/etc/gateway-registry/gateways.yaml
            - --output-dir=/data/federate
            - --interval=60
            - --retention=7200
          resources:
            requests: {{ cpu: 50m, memory: 64Mi }}
            limits: {{ memory: 128Mi }}
          volumeMounts:
            - name: federate-logs
              mountPath: /data/federate
            - name: gateway-registry
              mountPath: /etc/gateway-registry
              readOnly: true
      volumes:
        - name: config
          configMap: {{ name: alloy-config }}
        - name: federate-logs
          emptyDir: {{}}
        - name: gateway-registry
          configMap: {{ name: gateway-registry }}
"""
    return out


# ---------------------------------------------------------------------------
# gateway-registry.yaml
# ---------------------------------------------------------------------------


def gen_registry_yaml(gateways):
    entries = []
    for gw in gateways:
        entries.append(f"      - name: {gw['name']}")
        entries.append(f'        tailscale_ip: "{gw["tailscale_ip"]}"')
        entries.append(f"        ports:")
        for k, v in gw["ports"].items():
            entries.append(f"          {k}: {v}")

    return f"""## Generated by generate-config.py — do not edit directly.
## Source: profile/config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gateway-registry
  labels:
    app: monitoring
    component: master
data:
  gateways.yaml: |
    gateways:
{chr(10).join(entries)}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Generate master manifests")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    profile = load_config()
    gateways = build_gateway_list(profile)

    if not gateways:
        print("ERROR: No gateways found. Add gateway_tailscale_ip to profile/config.yaml.",
              file=sys.stderr)
        sys.exit(1)

    alloy = gen_alloy_yaml(gateways)
    registry = gen_registry_yaml(gateways)

    if args.dry_run:
        print(alloy)
        print("---")
        print(registry)
    else:
        for name, content in [("alloy.yaml", alloy), ("gateway-registry.yaml", registry)]:
            path = os.path.join(BASE_DIR, name)
            with open(path, "w") as f:
                f.write(content)
            print(f"Wrote {path}")


if __name__ == "__main__":
    main()
