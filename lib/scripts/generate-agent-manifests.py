#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import yaml


def q(v: str) -> str:
    return '"' + v.replace('"', '\\"') + '"'


def emit_agent(agent: dict) -> str:
    name = agent['name']
    customization = agent['image']['customization']
    image = 'REGISTRY/agent-base:latest' if customization in (None, 'none') else f'REGISTRY/{customization}:latest'
    minr = agent['deploy']['replicas']['min']
    maxr = agent['deploy']['replicas']['max']
    cooldown = agent['deploy']['replicas']['cooldown']
    req_topic = agent['runtime']['kafka']['request_topic']
    project_dir = agent['runtime']['state']['project_dir']
    state_dir = agent['runtime']['state']['state_dir']
    req_cpu = agent['deploy']['resources']['requests']['cpu']
    req_mem = agent['deploy']['resources']['requests']['memory']
    lim_mem = agent['deploy']['resources']['limits']['memory']
    return f'''---
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
              bash /app/scripts/setup-agent-dir.sh {name}
              KORDINATE_HOME=/app KORD_RUNTIME=/runtime bash /app/scripts/deploy-runtime.sh {name}
          volumeMounts:
            - {{ name: runtime, mountPath: /kord }}
            - {{ name: agent-runtime, mountPath: /runtime }}
      containers:
        - name: agent
          image: {image}
          imagePullPolicy: Always
          command: ["/bin/bash", "-c"]
          args:
            - |
              exec openclaude-daemon
          env:
            - {{ name: AGENT_NAME, value: {name} }}
            - {{ name: AGENT_PROJECT_DIR, value: {project_dir} }}
            - {{ name: AGENT_STATE_DIR, value: {state_dir} }}
            - {{ name: KAFKA_BROKERS, value: "kafka-kafka-bootstrap.dev.svc.cluster.local:9092" }}
            - {{ name: HOME, value: /home/claude }}
            - {{ name: KORDINATE_HOME, value: /app }}
            - {{ name: PROJECTS_ROOT, value: /kord/shared/repos }}
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
''', f'''---
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
''', f'''---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: {req_topic}
  labels:
    strimzi.io/cluster: kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: "604800000"
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('spec')
    parser.add_argument('--agents-out', required=True)
    parser.add_argument('--keda-out', required=True)
    parser.add_argument('--kafka-out', required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(Path(args.spec).read_text())
    agents = spec['agents']

    agents_parts = [
        '# Generated from agents/charon/skills/platform/agent-spec.yaml\n'
        '# Klaude owns the runtime semantics; Kordinate owns platform orchestration.\n'
    ]
    keda_parts = [
        '# Generated from agents/charon/skills/platform/agent-spec.yaml\n'
        '# One request topic and one ScaledObject per agent.\n'
    ]
    kafka_parts = [
        '# Generated from agents/charon/skills/platform/agent-spec.yaml\n'
        '# Request topics only; Klaude publishes responses to caller-specified reply_to topics.\n'
    ]

    for agent in agents:
        dep, so, topic = emit_agent(agent)
        agents_parts.append(dep)
        keda_parts.append(so)
        kafka_parts.append(topic)

    kafka_parts.append('''---
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
''')
    kafka_parts.append('''---
# Memory update topics (one per agent, partitions=1 for ordering)
''')
    for agent in agents:
        name = agent['name']
        kafka_parts.append(f'''apiVersion: kafka.strimzi.io/v1beta2
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
''')

    Path(args.agents_out).write_text('\n'.join(agents_parts))
    Path(args.keda_out).write_text('\n'.join(keda_parts))
    Path(args.kafka_out).write_text('\n'.join(kafka_parts))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
