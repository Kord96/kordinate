#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO_ROOT = Path("/kord/workstation/home/project/kordinate")
AGENT_METADATA_DIR = REPO_ROOT / "shared" / "runtime" / "agent-metadata"
PATH_CONFIG = json.loads((REPO_ROOT / "shared" / "runtime" / "path-config.json").read_text(encoding="utf-8"))
PLATFORM_SPEC_HEADER = "# Generated from agents/charon/skills/platform/agent-spec.yaml\n"
PROJECTS_ROOT = PATH_CONFIG["projectsRoot"]
KORDINATE_HOME = PATH_CONFIG["kordinateHome"]
AGENTS_RUNTIME_ROOT = PATH_CONFIG["agentsRuntimeRoot"]
RUNTIME_ROOT = PATH_CONFIG["runtimeRoot"]
SHARED_ROOT = PATH_CONFIG["sharedRoot"]
AUGUR_RELEASE_STORE = PATH_CONFIG["augurReleaseStore"]
RUNTIME_MOUNT = ("runtime", RUNTIME_ROOT)
SHARED_MOUNT = ("kord-shared", SHARED_ROOT)
DEFAULT_POD_SECURITY = [
    "      securityContext:",
    "        fsGroup: 1000",
    "        seccompProfile:",
    "          type: RuntimeDefault",
]
DEFAULT_REFLECTION_PROMPT = "\n".join([
    "Based on the completed task, return strict JSON only with exactly these keys:",
    '{"project":"...","general":"..."}',
    "project: lessons specific to the current project/repo/context.",
    "general: lessons that transfer to any project.",
    "Use strings only. If there is no strong lesson for a key, return an empty string.",
])
DEFAULT_RUNTIME_PROFILES = {
    "gemini-sdk": {
        "kind": "gemini-sdk",
        "toolGuidance": [
            "Rely on the runtime's advertised tool schema instead of assuming tool names from other runtimes.",
            "Do not invent helper names or wrap nonexistent tools inside Bash.",
        ],
        "runArtifactGuidance": [
            "Use the prepared run artifact tools for generated analysis artifacts when available.",
            "Treat index.json as the authoritative inventory for optional fact and derived files in this run.",
        ],
    },
    "claude-agent-sdk": {"kind": "claude-agent-sdk", "toolGuidance": []},
    "openclaude-harness": {
        "kind": "openclaude-harness",
        "toolGuidance": [
            "Rely on the runtime's advertised tool schema instead of assuming tool names from other runtimes.",
            "Do not invent helper names or wrap nonexistent tools inside Bash.",
        ],
    },
    "codex-sdk": {"kind": "codex-sdk", "toolGuidance": []},
}
SPECIAL_FLAVORS = {"augur", "charon", "alfred", "sauron"}


@dataclass(frozen=True)
class VolumeMount:
    name: str
    mount_path: str


@dataclass(frozen=True)
class Volume:
    name: str
    kind: str
    value: str
    extra_type: str | None = None


def yaml_block(text: str, spaces: int = 14) -> str:
    return textwrap.indent(text, " " * spaces)


def normalize_flavor(agent: dict) -> str:
    explicit = agent.get("flavor")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    name = str(agent["name"])
    return name if name in SPECIAL_FLAVORS else "generic"


def infer_supported_agent_params(agent: dict) -> list[str]:
    return ["bundle_mode"] if normalize_flavor(agent) == "augur" else []


def load_agent_metadata(agent: dict) -> dict:
    flavor = normalize_flavor(agent)
    metadata_path = AGENT_METADATA_DIR / f"{flavor}.json"
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {
        "name": agent["name"],
        "description": "",
        "capabilities": [],
    }


def render_path_template(template: str, **values: str) -> str:
    return template.format(**values)


def build_discovery_record(agent: dict, generated_at: str) -> dict:
    identity = load_agent_metadata(agent)
    daemon = agent.get("runtime", {}).get("daemon", {})
    return {
        "name": agent["name"],
        "capabilities": identity["capabilities"],
        "backend_provider": daemon.get("provider", "unknown"),
        "backend_model": str(daemon.get("model", "unknown")),
        "supported_agent_params": infer_supported_agent_params(agent),
        "active": False,
        "specialization": normalize_flavor(agent),
        "runtime": daemon.get("kind", "openclaude-harness"),
        "health_url": f"http://agent-{agent['name']}:9090/health",
        "default_working_dir": daemon.get("default_working_dir"),
        "default_timeout_ms": daemon.get("default_timeout_ms"),
        "registered_at": generated_at,
        "last_seen_at": generated_at,
        "request_topic": agent["runtime"]["kafka"]["request_topic"],
    }


def build_agent_contract(spec: dict, agent: dict) -> dict:
    spec_version = str(spec.get("version", "1"))
    flavor = normalize_flavor(agent)
    creation = agent.get("creation", {}) if isinstance(agent.get("creation"), dict) else {}
    agent_home_dir = agent["runtime"]["state"]["agent_home_dir"]
    identity = load_agent_metadata(agent)
    contract = {
        "version": f"agent-spec-v{spec_version}",
        "name": agent["name"],
        "specialization": flavor,
        "description": identity["description"],
        "capabilities": identity["capabilities"],
        "defaultReflectionPrompt": DEFAULT_REFLECTION_PROMPT,
        "supportedAgentParams": infer_supported_agent_params(agent),
        "requiresWorkingDirectory": flavor == "augur",
    }

    accepted_prefixes = agent.get("accepted_request_prefixes")
    if isinstance(accepted_prefixes, list):
        normalized_prefixes = [str(prefix).strip() for prefix in accepted_prefixes if str(prefix).strip()]
        if normalized_prefixes:
            contract["acceptedRequestPrefixes"] = normalized_prefixes

    bundle_refs = {
        "memory": creation.get("memory_bundle"),
        "skill": creation.get("skill_bundle"),
        "runtime": creation.get("runtime_bundle"),
    }
    if any(bundle_refs.values()):
        contract["bundleRefs"] = bundle_refs

    if flavor == "augur":
        augur_home = f"{agent_home_dir}/.augur/current"
        workflow_paths = identity.get("workflow_paths", {}) if isinstance(identity.get("workflow_paths"), dict) else {}
        validation_paths = identity.get("validation_paths", {}) if isinstance(identity.get("validation_paths"), dict) else {}
        template_values = {"agent_home": agent_home_dir, "augur_home": augur_home}
        contract["promptPrefix"] = "You are Augur. Favor design-level reasoning and architecture trade-offs."
        contract["defaultReflectionPrompt"] = "\n".join([
            'Return strict JSON with exactly {"project":"...","general":"..."}.',
            "For project, focus on design decisions, bundle strategy, and architecture-specific lessons.",
            "For general, focus on transferable architecture and review lessons.",
        ])
        contract["workflow"] = {
            "analysisContextScript": render_path_template(
                str(workflow_paths.get("analysis_context_script", "{augur_home}/scripts/run/build_analysis_context.py")),
                **template_values,
            ),
            "repairPromptScript": render_path_template(
                str(workflow_paths.get("repair_prompt_script", "{augur_home}/scripts/run/build_validation_repair_prompt.py")),
                **template_values,
            ),
        }
        validation = {
            "required": True,
            "validatorScript": render_path_template(
                str(validation_paths.get("validator_script", "{augur_home}/skills/analyze/validator/validate.py")),
                **template_values,
            ),
            "finalizeScript": render_path_template(
                str(validation_paths.get("finalize_script", "{augur_home}/scripts/run/finalize_analysis.py")),
                **template_values,
            ),
        }
        authored_validation = agent.get("validation") if isinstance(agent.get("validation"), dict) else {}
        max_attempts = authored_validation.get("max_attempts", authored_validation.get("maxAttempts"))
        if isinstance(max_attempts, int):
            validation["maxAttempts"] = max_attempts
        contract["validation"] = validation

    return contract


def resolve_runtime_profile(spec: dict, agent: dict) -> dict:
    runtime_kind = str(agent.get("runtime", {}).get("daemon", {}).get("kind", ""))
    spec_version = str(spec.get("version", "1"))
    authored_profiles = spec.get("runtime_profiles", {}) if isinstance(spec.get("runtime_profiles"), dict) else {}
    profile = dict(DEFAULT_RUNTIME_PROFILES.get(runtime_kind, {"kind": runtime_kind, "toolGuidance": []}))
    authored = authored_profiles.get(runtime_kind)
    if isinstance(authored, dict):
        profile.update(authored)
    profile["kind"] = runtime_kind
    profile.setdefault("version", f"runtime-profile-v{spec_version}")
    return profile


def image_ref(agent: dict) -> str:
    customization = agent["image"]["customization"]
    return "REGISTRY/agent-base:latest" if customization in (None, "none") else f"REGISTRY/{customization}:latest"


def build_env_entries(spec: dict, agent: dict) -> list[tuple[str, str]]:
    flavor = normalize_flavor(agent)
    agent_home_dir = agent["runtime"]["state"]["agent_home_dir"]
    state_dir = agent["runtime"]["state"]["state_dir"]
    daemon = agent.get("runtime", {}).get("daemon", {})
    backend = daemon.get("backend", {}) if isinstance(daemon.get("backend"), dict) else {}
    creation = agent.get("creation", {}) if isinstance(agent.get("creation"), dict) else {}

    entries: list[tuple[str, str]] = [
        ("AGENT_NAME", agent["name"]),
        ("AGENT_PROFILE", flavor),
        ("AGENT_CONTRACT_JSON", json.dumps(build_agent_contract(spec, agent), separators=(",", ":"))),
        ("RUNTIME_PROFILE_JSON", json.dumps(resolve_runtime_profile(spec, agent), separators=(",", ":"))),
        ("AGENT_HOME_DIR", agent_home_dir),
        ("AGENT_STATE_DIR", state_dir),
        ("DAEMON_WORKING_DIRECTORY", agent_home_dir),
        ("DAEMON_STATE_DIR", f"{agent_home_dir}/.daemon-state"),
        ("DAEMON_SESSION_MAP_PATH", f"{agent_home_dir}/.daemon-state/sessions.json"),
        ("KAFKA_BROKERS", "kafka-kafka-bootstrap.dev.svc.cluster.local:9092"),
        ("KAFKA_SESSION_TIMEOUT_MS", "30000"),
        ("KAFKA_HEARTBEAT_INTERVAL_MS", "3000"),
        ("HOME", "/home/node"),
        ("KORDINATE_HOME", KORDINATE_HOME),
        ("PROJECTS_ROOT", PROJECTS_ROOT),
        ("DISCOVERY_SERVER_URL", "http://kord-api:9091"),
        ("DAEMON_HEALTH_URL", f"http://agent-{agent['name']}:9090/health"),
    ]

    optional_entries = [
        ("DAEMON_RUNTIME", daemon.get("kind")),
        ("DAEMON_PROVIDER", daemon.get("provider")),
        ("DAEMON_MODEL", str(daemon["model"]) if daemon.get("model") else None),
        ("DAEMON_BACKEND", backend.get("name")),
        ("BACKEND_BASE_URL", backend.get("base_url")),
        ("CODEX_WORKING_DIRECTORY", daemon.get("default_working_dir")),
        ("CODEX_SANDBOX_MODE", str(daemon["sandbox_mode"]) if daemon.get("sandbox_mode") else None),
        ("AGENT_MEMORY_BUNDLE", creation.get("memory_bundle")),
        ("AGENT_SKILL_BUNDLE", creation.get("skill_bundle")),
        ("AGENT_RUNTIME_BUNDLE", creation.get("runtime_bundle")),
    ]
    entries.extend([(key, value) for key, value in optional_entries if value])

    if daemon.get("skip_git_repo_check") is not None:
        entries.append(("CODEX_SKIP_GIT_REPO_CHECK", "true" if daemon["skip_git_repo_check"] else "false"))
    if agent["name"] == "charon-gpt53-codex":
        entries.extend([
            ("CODEX_NETWORK_ACCESS_ENABLED", "true"),
            ("KUBECONFIG", "/home/node/.kube/config"),
            ("KUBECTL_VERSION", "v1.34.5"),
        ])
    if flavor == "alfred":
        entries.extend([
            ("PASSWORD_STORE_DIR", "/kord/alfred/pass"),
            ("GNUPGHOME", "/kord/alfred/gnupg"),
        ])
    if flavor == "augur":
        entries.extend([
            ("AUGUR_HOME", f"{agent_home_dir}/.augur/current"),
            ("AUGUR_RELEASE_STORE", AUGUR_RELEASE_STORE),
            ("AUGUR_RELEASE_CHANNEL", "stable"),
        ])

    return entries


def render_env_lines(spec: dict, agent: dict) -> list[str]:
    env_lines: list[str] = []
    for key, value in build_env_entries(spec, agent):
        if key == "HOME":
            env_lines.append("            # Standard Unix home for shells and CLIs that implicitly read $HOME.")
        if key == "KORDINATE_HOME":
            env_lines.append("            # Baked Kordinate code root inside the image; keep distinct from $HOME and AGENT_HOME_DIR.")
        env_lines.append(f"            - {{ name: {key}, value: {json.dumps(value)} }}")

    daemon = agent.get("runtime", {}).get("daemon", {})
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
    flavor = normalize_flavor(agent)
    creation = agent.get("creation", {}) if isinstance(agent.get("creation"), dict) else {}
    env_prefix = []
    if creation.get("memory_bundle"):
        env_prefix.append(f"AGENT_MEMORY_BUNDLE={shlex.quote(str(creation['memory_bundle']))}")
    if creation.get("skill_bundle"):
        env_prefix.append(f"AGENT_SKILL_BUNDLE={shlex.quote(str(creation['skill_bundle']))}")
    if creation.get("runtime_bundle"):
        env_prefix.append(f"AGENT_RUNTIME_BUNDLE={shlex.quote(str(creation['runtime_bundle']))}")
    env_prefix.extend([
        f"KORDINATE_HOME={shlex.quote(KORDINATE_HOME)}",
        f"KORD_RUNTIME={shlex.quote(AGENTS_RUNTIME_ROOT)}",
    ])
    prefix = " ".join(env_prefix)
    lines = [f"bash /app/scripts/setup-agent-dir.sh {shlex.quote(agent['name'])}"]
    if flavor in SPECIAL_FLAVORS:
        if flavor == agent["name"]:
            lines.append(f"{prefix} bash /app/scripts/deploy-runtime.sh {shlex.quote(agent['name'])}")
        else:
            lines.append(f"{prefix} bash /app/scripts/deploy-runtime.sh {shlex.quote(flavor)} {shlex.quote(agent['name'])}")
    return "\n".join(lines)


def build_exec_script(agent: dict) -> str:
    command = agent.get("runtime", {}).get("command") or ["klaude-daemon"]
    if agent["name"] != "charon-gpt53-codex":
        return "exec " + " ".join(shlex.quote(part) for part in command)
    lines = [
        "set -e",
        "if ! command -v bwrap >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then",
        "  export DEBIAN_FRONTEND=noninteractive",
        "  apt-get update >/dev/null",
        "  apt-get install -y --no-install-recommends bubblewrap curl ca-certificates >/dev/null",
        "fi",
        "if ! command -v kubectl >/dev/null 2>&1; then",
        "  curl -fsSL -o /usr/local/bin/kubectl https://dl.k8s.io/release/${KUBECTL_VERSION:-v1.34.5}/bin/linux/amd64/kubectl",
        "  chmod +x /usr/local/bin/kubectl",
        "fi",
        "mkdir -p /home/node/.kube",
        "TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)",
        "CA=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
        "SERVER=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}",
        "cat > /home/node/.kube/config <<KUBECONFIG_EOF",
        "apiVersion: v1",
        "kind: Config",
        "clusters:",
        "- cluster:",
        "    certificate-authority: ${CA}",
        "    server: ${SERVER}",
        "  name: in-cluster",
        "contexts:",
        "- context:",
        "    cluster: in-cluster",
        "    namespace: kord",
        "    user: serviceaccount",
        "  name: in-cluster",
        "current-context: in-cluster",
        "users:",
        "- name: serviceaccount",
        "  user:",
        "    token: ${TOKEN}",
        "KUBECONFIG_EOF",
        "chmod 600 /home/node/.kube/config",
        "exec " + " ".join(shlex.quote(part) for part in command),
    ]
    return "\n".join(lines)


def container_security_lines(agent: dict) -> list[str]:
    daemon = agent.get("runtime", {}).get("daemon", {})
    if agent["name"] == "charon-gpt53-codex":
        return [
            "            privileged: true",
            "            allowPrivilegeEscalation: true",
            "            runAsNonRoot: false",
            "            runAsUser: 0",
            "            runAsGroup: 0",
            "            capabilities:",
            "              add:",
            "                - SYS_ADMIN",
        ]
    if daemon.get("kind") == "codex-sdk":
        return [
            "            runAsNonRoot: true",
            "            runAsUser: 1000",
            "            runAsGroup: 1000",
            "            capabilities:",
            "              add:",
            "                - SETUID",
            "                - SETGID",
        ]
    return [
        "            runAsNonRoot: true",
        "            runAsUser: 1000",
        "            runAsGroup: 1000",
    ]


def volume_mounts_for(agent: dict) -> list[VolumeMount]:
    mounts = [VolumeMount(*RUNTIME_MOUNT), VolumeMount(*SHARED_MOUNT)]
    if normalize_flavor(agent) == "augur":
        mounts.append(VolumeMount("docker-sock", "/var/run/docker.sock"))
    return mounts


def volumes_for(agent: dict) -> list[Volume]:
    volumes = [
        Volume("runtime", "persistentVolumeClaim", "agent-runtime"),
        Volume("kord-shared", "persistentVolumeClaim", "kord"),
    ]
    if normalize_flavor(agent) == "augur":
        volumes.append(Volume("docker-sock", "hostPath", "/var/run/docker.sock", extra_type="Socket"))
    return volumes


def render_volume_mounts(indent: str, mounts: list[VolumeMount]) -> str:
    return "\n".join(f"{indent}- {{ name: {mount.name}, mountPath: {mount.mount_path} }}" for mount in mounts)


def render_volumes(indent: str, volumes: list[Volume]) -> str:
    lines: list[str] = []
    for volume in volumes:
        lines.append(f"{indent}- name: {volume.name}")
        if volume.kind == "persistentVolumeClaim":
            lines.append(f"{indent}  persistentVolumeClaim: {{ claimName: {volume.value} }}")
        elif volume.kind == "hostPath":
            lines.append(f"{indent}  hostPath:")
            lines.append(f"{indent}    path: {volume.value}")
            if volume.extra_type:
                lines.append(f"{indent}    type: {volume.extra_type}")
        elif volume.kind == "emptyDir":
            lines.append(f"{indent}  emptyDir: {{}}")
        else:
            raise ValueError(f"unsupported volume kind: {volume.kind}")
    return "\n".join(lines)


def emit_agent(spec: dict, agent: dict) -> tuple[str, str, str]:
    image = image_ref(agent)
    flavor = normalize_flavor(agent)
    mounts = volume_mounts_for(agent)
    volumes = volumes_for(agent)
    minr = agent["deploy"]["replicas"]["min"]
    maxr = agent["deploy"]["replicas"]["max"]
    cooldown = agent["deploy"]["replicas"]["cooldown"]
    req_topic = agent["runtime"]["kafka"]["request_topic"]
    req_cpu = agent["deploy"]["resources"]["requests"]["cpu"]
    req_mem = agent["deploy"]["resources"]["requests"]["memory"]
    lim_mem = agent["deploy"]["resources"]["limits"]["memory"]
    strategy_block = "  strategy:\n    type: Recreate\n" if maxr == 1 else ""
    env_block = "\n".join(render_env_lines(spec, agent))
    deployment = f"""---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-{agent["name"]}
  labels: {{ app: kord-agent, agent: {agent["name"]} }}
spec:
{strategy_block}  selector:
    matchLabels: {{ app: kord-agent, agent: {agent["name"]} }}
  template:
    metadata:
      labels: {{ app: kord-agent, agent: {agent["name"]} }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
{chr(10).join(DEFAULT_POD_SECURITY)}
      serviceAccountName: kord
      initContainers:
        - name: setup
          image: {image}
          imagePullPolicy: Always
          command: ["/bin/bash", "-c"]
          args:
            - |
{yaml_block(build_init_script(agent))}
          env:
{env_block}
          volumeMounts:
{render_volume_mounts("            ", mounts)}
      containers:
        - name: agent
          image: {image}
          imagePullPolicy: Always
          securityContext:
{chr(10).join(container_security_lines(agent))}
          command: ["/bin/bash", "-c"]
          args:
            - |
{yaml_block(build_exec_script(agent))}
          env:
{env_block}
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
{render_volume_mounts("            ", mounts)}
      volumes:
{render_volumes("        ", volumes)}
"""

    service = f"""---
apiVersion: v1
kind: Service
metadata:
  name: agent-{agent["name"]}
  labels: {{ app: kord-agent, agent: {agent["name"]} }}
spec:
  selector:
    app: kord-agent
    agent: {agent["name"]}
  ports:
    - name: health
      port: 9090
      targetPort: 9090
"""

    scaled_object = f"""---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agent-{agent["name"]}
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
    name: agent-{agent["name"]}
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

    topic = f"""---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: {req_topic}
  labels:
    strimzi.io/cluster: kafka
spec:
  partitions: {max(1, int(maxr))}
  replicas: 1
  config:
    retention.ms: "604800000"
"""

    return deployment + service, scaled_object, topic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--agents-out", required=True)
    parser.add_argument("--keda-out", required=True)
    parser.add_argument("--kafka-out", required=True)
    parser.add_argument("--discovery-catalog-out", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = yaml.safe_load(Path(args.spec).read_text())
    agents = spec["agents"]

    agents_parts = [
        PLATFORM_SPEC_HEADER + "# Agent flavor, runtime kind, and backend selection are declared in the spec.\n"
    ]
    keda_parts = [
        PLATFORM_SPEC_HEADER + "# One request topic and one ScaledObject per agent.\n"
    ]
    kafka_parts = [
        PLATFORM_SPEC_HEADER + "# Request topics only; Klaude publishes responses to caller-specified reply_to topics.\n"
    ]

    for agent in agents:
        deployment, scaled_object, topic = emit_agent(spec, agent)
        agents_parts.append(deployment)
        keda_parts.append(scaled_object)
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
        kafka_parts.append(f"""apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: memory.updates.{agent["name"]}
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
