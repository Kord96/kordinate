#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import yaml


SPECIAL_FLAVORS = {"augur", "charon", "alfred", "sauron", "warden"}


def infer_supported_agent_params(agent: dict) -> list[str]:
    flavor = agent.get("flavor") or (agent["name"] if agent["name"] in SPECIAL_FLAVORS else "generic")
    if flavor == "augur":
        return ["bundle_mode"]
    return []


def parse_identity(agent: dict) -> dict:
    flavor = agent.get("flavor") or (agent["name"] if agent["name"] in SPECIAL_FLAVORS else "generic")
    identity_path = Path(f"/kord/workstation/home/project/kordinate/agents/{flavor}/IDENTITY.md")
    if not identity_path.exists():
        return {
            "name": agent["name"],
            "description": "",
            "capabilities": [],
        }

    text = identity_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line and not line.lstrip().startswith("- "):
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

    capabilities: list[str] = []
    in_capabilities = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Capabilities":
            in_capabilities = True
            continue
        if in_capabilities and stripped.startswith("## "):
            break
        if in_capabilities and stripped.startswith("- "):
            capabilities.append(stripped[2:].strip())

    return {
        "name": frontmatter.get("name", agent["name"]),
        "description": frontmatter.get("description", ""),
        "capabilities": capabilities,
    }


def build_discovery_record(agent: dict, generated_at: str) -> dict:
    name = agent["name"]
    flavor = agent.get("flavor") or (name if name in SPECIAL_FLAVORS else "generic")
    identity = parse_identity(agent)
    daemon = agent.get("runtime", {}).get("daemon", {})
    default_working_dir = daemon.get("default_working_dir")
    return {
        "name": name,
        "capabilities": identity["capabilities"],
        "backend_provider": daemon.get("provider", "unknown"),
        "backend_model": str(daemon.get("model", "unknown")),
        "supported_agent_params": infer_supported_agent_params(agent),
        "active": False,
        "specialization": flavor,
        "runtime": daemon.get("kind", "openclaude-harness"),
        "health_url": f"http://agent-{name}:9090/health",
        "default_working_dir": default_working_dir,
        "registered_at": generated_at,
        "last_seen_at": generated_at,
        "request_topic": agent["runtime"]["kafka"]["request_topic"],
    }


def image_ref(agent: dict) -> str:
    customization = agent["image"]["customization"]
    if customization in (None, "none"):
        return "REGISTRY/agent-base:latest"
    return f"REGISTRY/{customization}:latest"


def emit_env_lines(agent: dict) -> list[str]:
    name = agent["name"]
    flavor = agent.get("flavor") or (name if name in SPECIAL_FLAVORS else "generic")
    agent_home_dir = agent["runtime"]["state"]["agent_home_dir"]
    state_dir = agent["runtime"]["state"]["state_dir"]
    daemon = agent.get("runtime", {}).get("daemon", {})
    backend = daemon.get("backend", {}) if isinstance(daemon.get("backend"), dict) else {}
    creation = agent.get("creation", {}) if isinstance(agent.get("creation"), dict) else {}

    env = [
        ("AGENT_NAME", name),
        ("AGENT_PROFILE", flavor),
        ("AGENT_HOME_DIR", agent_home_dir),
        ("AGENT_STATE_DIR", state_dir),
        ("DAEMON_WORKING_DIRECTORY", agent_home_dir),
        ("DAEMON_STATE_DIR", f"{agent_home_dir}/.daemon-state"),
        ("DAEMON_SESSION_MAP_PATH", f"{agent_home_dir}/.daemon-state/sessions.json"),
        ("KAFKA_BROKERS", "kafka-kafka-bootstrap.dev.svc.cluster.local:9092"),
        ("KAFKA_SESSION_TIMEOUT_MS", "30000"),
        ("KAFKA_HEARTBEAT_INTERVAL_MS", "3000"),
        ("HOME", "/home/node"),
        ("KORDINATE_HOME", "/app"),
        ("PROJECTS_ROOT", "/kord/shared/repos"),
        ("DISCOVERY_SERVER_URL", "http://kord-api:9091"),
        ("DAEMON_HEALTH_URL", f"http://agent-{name}:9090/health"),
    ]

    if daemon.get("kind"):
        env.append(("DAEMON_RUNTIME", daemon["kind"]))
    if daemon.get("provider"):
        env.append(("DAEMON_PROVIDER", daemon["provider"]))
    if daemon.get("model"):
        env.append(("DAEMON_MODEL", str(daemon["model"])))
    if backend.get("name"):
        env.append(("DAEMON_BACKEND", backend["name"]))
    if backend.get("base_url"):
        env.append(("BACKEND_BASE_URL", backend["base_url"]))
    if daemon.get("default_working_dir"):
        env.append(("CODEX_WORKING_DIRECTORY", daemon["default_working_dir"]))
    if daemon.get("skip_git_repo_check") is not None:
        env.append(("CODEX_SKIP_GIT_REPO_CHECK", "true" if daemon["skip_git_repo_check"] else "false"))
    if creation.get("memory_bundle"):
        env.append(("AGENT_MEMORY_BUNDLE", creation["memory_bundle"]))
    if creation.get("skill_bundle"):
        env.append(("AGENT_SKILL_BUNDLE", creation["skill_bundle"]))
    if creation.get("runtime_bundle"):
        env.append(("AGENT_RUNTIME_BUNDLE", creation["runtime_bundle"]))
    if flavor == "alfred":
        env.append(("PASSWORD_STORE_DIR", "/kord/alfred/pass"))
        env.append(("GNUPGHOME", "/kord/alfred/gnupg"))

    env_lines = [f"            - {{ name: {key}, value: {json.dumps(value)} }}" for key, value in env]

    secret = daemon.get("secret", {}) if isinstance(daemon.get("secret"), dict) else {}
    if secret.get("env") and secret.get("name") and secret.get("key"):
        env_lines.extend([
            f"            - name: {secret['env']}",
            "              valueFrom:",
            "                secretKeyRef:",
            f"                  name: {secret['name']}",
            f"                  key: {secret['key']}",
        ])

    return env_lines


def build_init_script(agent: dict) -> str:
    name = agent["name"]
    flavor = agent.get("flavor") or (name if name in SPECIAL_FLAVORS else "generic")
    creation = agent.get("creation", {}) if isinstance(agent.get("creation"), dict) else {}
    env_prefix = []
    if creation.get("memory_bundle"):
        env_prefix.append(f"AGENT_MEMORY_BUNDLE={shlex.quote(str(creation['memory_bundle']))}")
    if creation.get("skill_bundle"):
        env_prefix.append(f"AGENT_SKILL_BUNDLE={shlex.quote(str(creation['skill_bundle']))}")
    if creation.get("runtime_bundle"):
        env_prefix.append(f"AGENT_RUNTIME_BUNDLE={shlex.quote(str(creation['runtime_bundle']))}")
    env_prefix.append("KORDINATE_HOME=/app")
    env_prefix.append("KORD_RUNTIME=/runtime")
    prefix = " ".join(env_prefix)
    lines = [f"bash /app/scripts/setup-agent-dir.sh {shlex.quote(name)}"]
    if flavor in SPECIAL_FLAVORS:
        if flavor == name:
            lines.append(f"{prefix} bash /app/scripts/deploy-runtime.sh {shlex.quote(name)}")
        else:
            lines.append(
                f"{prefix} bash /app/scripts/deploy-runtime.sh "
                f"{shlex.quote(flavor)} {shlex.quote(name)}"
            )
    return "\n".join(lines)


def build_exec_script(agent: dict) -> str:
    command = agent.get("runtime", {}).get("command") or ["klaude-daemon"]
    return "exec " + " ".join(shlex.quote(part) for part in command)


def yaml_block(text: str, spaces: int = 14) -> str:
    return textwrap.indent(text, " " * spaces)


def emit_agent(agent: dict) -> tuple[str, str, str]:
    name = agent["name"]
    image = image_ref(agent)
    minr = agent["deploy"]["replicas"]["min"]
    maxr = agent["deploy"]["replicas"]["max"]
    cooldown = agent["deploy"]["replicas"]["cooldown"]
    req_topic = agent["runtime"]["kafka"]["request_topic"]
    req_cpu = agent["deploy"]["resources"]["requests"]["cpu"]
    req_mem = agent["deploy"]["resources"]["requests"]["memory"]
    lim_mem = agent["deploy"]["resources"]["limits"]["memory"]
    env_lines = "\n".join(emit_env_lines(agent))
    init_script = yaml_block(build_init_script(agent))
    exec_script = yaml_block(build_exec_script(agent))

    deployment = f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-{name}
  labels: {{ app: kord-agent, agent: {name} }}
spec:
  selector:
    matchLabels: {{ app: kord-agent, agent: {name} }}
  template:
    metadata:
      labels: {{ app: kord-agent, agent: {name} }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      serviceAccountName: kord
      initContainers:
        - name: setup
          image: {image}
          imagePullPolicy: Always
          command: ["/bin/bash", "-c"]
          args:
            - |
{init_script}
          volumeMounts:
            - {{ name: runtime, mountPath: /kord }}
            - {{ name: agent-runtime, mountPath: /runtime }}
      containers:
        - name: agent
          image: {image}
          imagePullPolicy: Always
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            runAsGroup: 1000
          command: ["/bin/bash", "-c"]
          args:
            - |
{exec_script}
          env:
{env_lines}
          resources:
            requests: {{ cpu: {req_cpu}, memory: {req_mem} }}
            limits: {{ memory: {lim_mem} }}
          ports:
            - {{ containerPort: 9090, name: status }}
          readinessProbe:
            httpGet: {{ path: /health, port: 9090 }}
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet: {{ path: /health, port: 9090 }}
            initialDelaySeconds: 30
            periodSeconds: 30
          volumeMounts:
            - {{ name: runtime, mountPath: /kord }}
            - {{ name: agent-runtime, mountPath: /runtime }}
      volumes:
        - name: runtime
          persistentVolumeClaim: {{ claimName: agent-runtime }}
        - name: agent-runtime
          emptyDir: {{}}
      securityContext:
        fsGroup: 1000
"""

    service = f"""---
apiVersion: v1
kind: Service
metadata:
  name: agent-{name}
  labels: {{ app: kord-agent, agent: {name} }}
spec:
  selector:
    app: kord-agent
    agent: {name}
  ports:
    - name: health
      port: 9090
      targetPort: 9090
"""

    scaled_object = f"""---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agent-{name}
spec:
  pollingInterval: 30
  minReplicaCount: {minr}
  maxReplicaCount: {maxr}
  cooldownPeriod: {cooldown}
  advanced:
    restoreToOriginalReplicaCount: true
    horizontalPodAutoscalerConfig:
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 300
        scaleUp:
          stabilizationWindowSeconds: 300
  scaleTargetRef:
    name: agent-{name}
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka-kafka-bootstrap.dev.svc.cluster.local:9092
        consumerGroup: {req_topic}
        topic: {req_topic}
        lagThreshold: "1"
        activationLagThreshold: "0"
        offsetResetPolicy: earliest
"""

    topic_partitions = 1 if int(maxr) <= 1 else 3

    topic = f"""---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: {req_topic}
  labels:
    strimzi.io/cluster: kafka
spec:
  partitions: {topic_partitions}
  replicas: 1
  config:
    retention.ms: "604800000"
"""

    return deployment + service, scaled_object, topic


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--agents-out", required=True)
    parser.add_argument("--keda-out", required=True)
    parser.add_argument("--kafka-out", required=True)
    parser.add_argument("--discovery-catalog-out", required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(Path(args.spec).read_text())
    agents = spec["agents"]

    agents_parts = [
        "# Generated from agents/charon/skills/platform/agent-spec.yaml\n"
        "# Agent flavor, runtime kind, and backend selection are declared in the spec.\n"
    ]
    keda_parts = [
        "# Generated from agents/charon/skills/platform/agent-spec.yaml\n"
        "# One request topic and one ScaledObject per agent.\n"
    ]
    kafka_parts = [
        "# Generated from agents/charon/skills/platform/agent-spec.yaml\n"
        "# Request topics only; Klaude publishes responses to caller-specified reply_to topics.\n"
    ]

    for agent in agents:
        dep, so, topic = emit_agent(agent)
        agents_parts.append(dep)
        keda_parts.append(so)
        kafka_parts.append(topic)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    discovery_catalog = [build_discovery_record(agent, generated_at) for agent in agents]

    kafka_parts.append("""---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: agent.dlq
  labels:
    strimzi.io/cluster: kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: "2592000000"
""")
    kafka_parts.append("""---
# Memory update topics (one per agent, partitions=1 for ordering)
""")
    for agent in agents:
        name = agent["name"]
        kafka_parts.append(f"""apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: memory.updates.{name}
  labels:
    strimzi.io/cluster: kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: "86400000"
---
""")

    Path(args.agents_out).write_text("\n".join(agents_parts))
    Path(args.keda_out).write_text("\n".join(keda_parts))
    Path(args.kafka_out).write_text("\n".join(kafka_parts))
    Path(args.discovery_catalog_out).write_text(json.dumps(discovery_catalog, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
