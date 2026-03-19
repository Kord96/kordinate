#!/usr/bin/env python3
"""
Generate master alloy.yaml and gateway-registry.yaml from config sources.

Reads:
  - profile/config.yaml          (cluster names, service ports)
  - master/gateway-ips.yaml      (gateway Tailscale IPs, NFS status)

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
PROFILE_CONFIG = os.path.join(SCRIPT_DIR, "..", "..", "..", "..", "profile", "config.yaml")
GATEWAY_IPS = os.path.join(SCRIPT_DIR, "gateway-ips.yaml")

# Default ports if not overridden in gateway-ips.yaml
DEFAULT_PORTS = {
    "metrics": 9090,
    "logs_federate": 3101,
    "nfs": 2049,
}


def load_configs():
    """Load profile config and gateway IPs."""
    with open(PROFILE_CONFIG) as f:
        profile = yaml.safe_load(f)

    with open(GATEWAY_IPS) as f:
        gw_ips = yaml.safe_load(f)

    return profile, gw_ips


def build_gateway_list(profile, gw_ips):
    """Build ordered list of gateways with all needed fields."""
    gateways = []
    for name in sorted(profile["clusters"].keys()):
        if name not in gw_ips["gateways"]:
            print(f"WARNING: cluster '{name}' in config.yaml but not in gateway-ips.yaml — skipping",
                  file=sys.stderr)
            continue
        gw = gw_ips["gateways"][name]
        ports = {k: gw.get(k, v) for k, v in DEFAULT_PORTS.items()}
        gateways.append({
            "name": name,
            "tailscale_ip": gw["tailscale_ip"],
            "nfs_enabled": gw.get("nfs_enabled", True),
            "ports": ports,
        })
    return gateways


def comment_block(text):
    """Comment out a block of YAML lines."""
    lines = []
    for line in text.splitlines():
        if line.strip():
            lines.append("# " + line)
        else:
            lines.append("#")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# alloy.yaml generation
# ---------------------------------------------------------------------------

def gen_nfs_pv_pvc(gw):
    """Generate NFS PV + PVC block for a single gateway."""
    name = gw["name"]
    ip = gw["tailscale_ip"]

    return f"""\
apiVersion: v1
kind: PersistentVolume
metadata:
  name: alloy-nfs-{name}
  labels:
    app: monitoring
    component: alloy
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadOnlyMany
  mountOptions:
    - nfsvers=4
    - ro
  nfs:
    server: "{ip}"
    path: /federate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: alloy-nfs-{name}
  labels:
    app: monitoring
    component: alloy
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 1Gi
  volumeName: alloy-nfs-{name}
  storageClassName: \"\""""


def gen_alloy_config_inner(gateways):
    """Generate the inner Alloy config (the config.alloy content)."""
    lines = []

    # Metrics section
    lines.append("// " + "=" * 51)
    lines.append("// METRICS — pull from all Gateway Proms via /federate")
    lines.append("// " + "=" * 51)
    lines.append("")

    for gw in gateways:
        name = gw["name"]
        ip = gw["tailscale_ip"]
        port = gw["ports"]["metrics"]
        lines.append(f'prometheus.scrape "federate_{name}" {{')
        lines.append(f"  targets = [{{")
        lines.append(f'    __address__ = "{ip}:{port}",')
        lines.append(f"  }}]")
        lines.append(f'  metrics_path    = "/federate"')
        lines.append(f'  params          = {{ "match[]" = ["{{__name__=~\\".+\\"}}"] }}')
        lines.append(f'  scrape_interval = "60s"')
        lines.append(f'  scrape_timeout  = "25s"')
        lines.append(f"  honor_labels    = true")
        lines.append(f"  forward_to      = [prometheus.remote_write.master.receiver]")
        lines.append(f"}}")
        lines.append("")

    lines.append('prometheus.remote_write "master" {')
    lines.append("  endpoint {")
    lines.append('    url = "http://prometheus.master.svc.cluster.local:9191/api/v1/write"')
    lines.append("  }")
    lines.append("}")
    lines.append("")

    # Logs section
    lines.append("// " + "=" * 51)
    lines.append("// LOGS — tail JSON Lines files from gateway NFS shares")
    lines.append("// Sidecar on each cluster writes files to /data/federate/")
    lines.append("// Master mounts via NFS over Tailscale, tails with loki.source.file")
    lines.append("// " + "=" * 51)
    lines.append("")

    for gw in gateways:
        name = gw["name"]
        enabled = gw["nfs_enabled"]

        log_block = [
            f'local.file_match "logs_{name}" {{',
            f"  path_targets = [{{",
            f'    __path__ = "/data/federate/{name}/*.json",',
            f'    cluster  = "{name}",',
            f"  }}]",
            f"}}",
            f"",
            f'loki.source.file "logs_{name}" {{',
            f"  targets    = local.file_match.logs_{name}.targets",
            f"  forward_to = [loki.process.federate.receiver]",
            f"}}",
        ]

        if not enabled:
            lines.append(f"// -- {name} cluster logs -- (disabled: NFS not deployed)")
            for line in log_block:
                if line:
                    lines.append(f"// {line}")
                else:
                    lines.append("//")
        else:
            lines.append(f"// -- {name} cluster logs --")
            lines.extend(log_block)
        lines.append("")

    # Log processing pipeline (static)
    lines.append('// -- Parse federated log lines --')
    lines.append('// Each line: {"stream": {labels}, "ts": "...", "line": "..."}')
    lines.append('loki.process "federate" {')
    lines.append("  // Extract the embedded stream labels and original log line")
    lines.append("  stage.json {")
    lines.append("    expressions = {")
    lines.append('      stream_app       = "stream.app",')
    lines.append('      stream_component = "stream.component",')
    lines.append('      stream_namespace = "stream.namespace",')
    lines.append('      stream_cluster   = "stream.cluster",')
    lines.append('      stream_node      = "stream.node",')
    lines.append('      stream_pod       = "stream.pod",')
    lines.append('      stream_container = "stream.container",')
    lines.append('      stream_level     = "stream.level",')
    lines.append('      stream_consumer  = "stream.consumer",')
    lines.append('      original_line    = "line",')
    lines.append("    }")
    lines.append("  }")
    lines.append("")
    lines.append("  // Apply the original labels")
    lines.append("  stage.labels {")
    lines.append("    values = {")
    lines.append('      app       = "stream_app",')
    lines.append('      component = "stream_component",')
    lines.append('      namespace = "stream_namespace",')
    lines.append('      cluster   = "stream_cluster",')
    lines.append('      node      = "stream_node",')
    lines.append('      pod       = "stream_pod",')
    lines.append('      container = "stream_container",')
    lines.append('      level     = "stream_level",')
    lines.append('      consumer  = "stream_consumer",')
    lines.append("    }")
    lines.append("  }")
    lines.append("")
    lines.append("  // Replace the log line with the original content")
    lines.append("  stage.output {")
    lines.append('    source = "original_line"')
    lines.append("  }")
    lines.append("")
    lines.append("  forward_to = [loki.write.master.receiver]")
    lines.append("}")
    lines.append("")
    lines.append("// Write to Master Loki in master namespace")
    lines.append('loki.write "master" {')
    lines.append("  endpoint {")
    lines.append('    url = "http://loki.master.svc.cluster.local:3100/loki/api/v1/push"')
    lines.append("  }")
    lines.append("}")

    return lines


def gen_alloy_yaml(gateways):
    """Generate the full alloy.yaml manifest."""
    out = []

    out.append("## Generated by generate-config.py — do not edit directly.")
    out.append("## Regenerate: cd master && python3 generate-config.py")
    out.append("##")
    out.append("## Master Alloy — pulls metrics and logs from all cluster gateways.")
    out.append("## Metrics: pulls /federate from each gateway's Prom via Tailscale (:9090).")
    out.append("## Logs: tails JSON Lines files from each gateway's NFS share via Tailscale (:2049).")
    out.append("## Writes metrics to Master Prometheus, logs to Master Loki.")
    out.append("##")
    out.append("## NFS PV/PVCs for gateway log federation (NFSv4-only servers)")

    # NFS PV/PVCs
    for gw in gateways:
        pv_pvc = gen_nfs_pv_pvc(gw)
        if not gw["nfs_enabled"]:
            out.append(f"## {gw['name']} cluster NFS — disabled (nfs_enabled: false in gateway-ips.yaml)")
            out.append(comment_block(pv_pvc))
        else:
            out.append(pv_pvc)
    out.append("---")

    # ConfigMap
    alloy_config_lines = gen_alloy_config_inner(gateways)
    # Indent each line by 4 spaces for the YAML literal block
    indented_config = "\n".join("    " + line if line else "" for line in alloy_config_lines)

    out.append("apiVersion: v1")
    out.append("kind: ConfigMap")
    out.append("metadata:")
    out.append("  name: alloy-config")
    out.append("  labels:")
    out.append("    app: monitoring")
    out.append("    component: alloy")
    out.append("data:")
    out.append("  config.alloy: |")
    out.append(indented_config)
    out.append("---")

    # Deployment
    out.append("apiVersion: apps/v1")
    out.append("kind: Deployment")
    out.append("metadata:")
    out.append("  name: alloy")
    out.append("  labels:")
    out.append("    app: monitoring")
    out.append("    component: alloy")
    out.append("spec:")
    out.append("  replicas: 1")
    out.append("  strategy:")
    out.append("    type: Recreate")
    out.append("  selector:")
    out.append("    matchLabels:")
    out.append("      app: monitoring")
    out.append("      component: alloy")
    out.append("  template:")
    out.append("    metadata:")
    out.append("      labels:")
    out.append("        app: monitoring")
    out.append("        component: alloy")
    out.append("    spec:")
    out.append("      containers:")
    out.append("        - name: alloy")
    out.append("          image: grafana/alloy:v1.5.1")
    out.append("          args:")
    out.append("            - run")
    out.append("            - /etc/alloy/config.alloy")
    out.append("            - --stability.level=generally-available")
    out.append("          resources:")
    out.append("            requests:")
    out.append("              cpu: 200m")
    out.append("              memory: 256Mi")
    out.append("            limits:")
    out.append("              memory: 1Gi")
    out.append("          volumeMounts:")
    out.append("            - name: config")
    out.append("              mountPath: /etc/alloy")

    for gw in gateways:
        if gw["nfs_enabled"]:
            out.append(f"            - name: logs-{gw['name']}")
            out.append(f"              mountPath: /data/federate/{gw['name']}")
            out.append(f"              readOnly: true")
        else:
            out.append(f"            # {gw['name']}: NFS not deployed — mount skipped")

    out.append("      volumes:")
    out.append("        - name: config")
    out.append("          configMap:")
    out.append("            name: alloy-config")

    for gw in gateways:
        if gw["nfs_enabled"]:
            out.append(f"        - name: logs-{gw['name']}")
            out.append(f"          persistentVolumeClaim:")
            out.append(f"            claimName: alloy-nfs-{gw['name']}")
            out.append(f"            readOnly: true")
        else:
            out.append(f"        # {gw['name']}: NFS not deployed — volume skipped")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# gateway-registry.yaml generation
# ---------------------------------------------------------------------------

def gen_gateway_registry_yaml(gateways):
    """Generate the gateway-registry ConfigMap."""
    out = []
    out.append("## Generated by generate-config.py — do not edit directly.")
    out.append("## Regenerate: cd master && python3 generate-config.py")
    out.append("##")
    out.append("## Gateway Registry — lists all cluster gateways for master to discover.")
    out.append("##")
    out.append("apiVersion: v1")
    out.append("kind: ConfigMap")
    out.append("metadata:")
    out.append("  name: gateway-registry")
    out.append("  labels:")
    out.append("    app: monitoring")
    out.append("    component: master")
    out.append("data:")
    out.append("  gateways.yaml: |")
    out.append("    gateways:")

    for gw in gateways:
        out.append(f"      - name: {gw['name']}")
        out.append(f'        tailscale_ip: "{gw["tailscale_ip"]}"')
        out.append(f"        nfs_enabled: {str(gw['nfs_enabled']).lower()}")
        out.append(f"        ports:")
        out.append(f"          metrics: {gw['ports']['metrics']}")
        out.append(f"          logs_federate: {gw['ports']['logs_federate']}")
        out.append(f"          nfs: {gw['ports']['nfs']}")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate master manifests from config")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print to stdout instead of writing files")
    args = parser.parse_args()

    profile, gw_ips = load_configs()
    gateways = build_gateway_list(profile, gw_ips)

    if not gateways:
        print("ERROR: No gateways found. Check config.yaml and gateway-ips.yaml.",
              file=sys.stderr)
        sys.exit(1)

    alloy_content = gen_alloy_yaml(gateways)
    registry_content = gen_gateway_registry_yaml(gateways)

    if args.dry_run:
        print("=" * 60)
        print("=== alloy.yaml")
        print("=" * 60)
        print(alloy_content)
        print("=" * 60)
        print("=== gateway-registry.yaml")
        print("=" * 60)
        print(registry_content)
    else:
        alloy_path = os.path.join(BASE_DIR, "alloy.yaml")
        registry_path = os.path.join(BASE_DIR, "gateway-registry.yaml")

        with open(alloy_path, "w") as f:
            f.write(alloy_content)
        print(f"Wrote {alloy_path}")

        with open(registry_path, "w") as f:
            f.write(registry_content)
        print(f"Wrote {registry_path}")


if __name__ == "__main__":
    main()
