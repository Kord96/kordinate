---
name: prompt-agent
description: Send work to a daemon-backed agent pod through Kafka. Use when you need to invoke alfred, augur, charon, sauron, or warden without memorizing the request envelope, reply-topic handling, working_dir hint, or discovery lookup.
---

# Prompt Agent

Use this skill when you need to invoke a pod agent through the shared `klaude-daemon` contract.

Two modes:
- `discover` — return the live discovery response for all agents or one agent
- `prompt` — send one request and wait for the matching reply

## Workflow

1. Resolve the target agent from discovery when available. If discovery is unavailable, fall back to the known request topic equal to the agent name.
2. Create a unique reply topic for the caller.
   - for sticky multi-turn sessions, reuse the same reply topic or use `--session-id` in the helper
3. Publish one Kafka request message to the agent request topic.
4. Wait on the reply topic for a matching `correlation_id`.
5. Return the `output`, `status`, any `errors`, and timing metadata.

## Recommended Helper

Use [agent_prompt.py](/kord/workstation/home/project/kordinate/lib/scripts/agent_prompt.py) when available.

It supports both:
- direct discovery HTTP when the discovery service is reachable
- `kubectl exec` fallback into `deploy/klaude-discovery` when discovery is cluster-only

Examples:

```bash
python lib/scripts/agent_prompt.py discover
python lib/scripts/agent_prompt.py discover --agent alfred
python lib/scripts/agent_prompt.py prompt alfred "Use your /kord alfred get skill with arguments: key kordinate/deepseek/api-key" --working-dir /kord/shared/repos/kordinate
python lib/scripts/agent_prompt.py prompt augur-opus "Analyze the auth layer" --working-dir /kord/shared/repos/kordinate --session-id auth-review
```

## Request Contract

Publish to topic `<agent>`, for example `alfred` or `charon`.

Required fields:

```json
{
  "type": "request",
  "sender": "caller-reply-topic",
  "correlation_id": "unique-id",
  "prompt": "Do the task"
}
```

Optional fields:

```json
{
  "working_dir": "/kord/shared/repos/kordinate",
  "timeout_ms": 120000,
  "reflect": false,
  "reflection_prompt": "optional override",
  "agent_params": {}
}
```

Rules:
- `sender` is the reply topic. Do not use `reply_to`.
- reusing the same `sender` value across related requests keeps them on the same Kafka partition when the publisher uses sender-keyed routing
- `working_dir` is a hint for where the agent should focus first.
- `correlation_id` must be caller-generated and unique per request.
- `agent_params` is for agent-specific structured flags only.

## Response Contract

Expect one response on the reply topic:

```json
{
  "type": "response",
  "sender": "alfred",
  "correlation_id": "same-id",
  "status": "success|error|timeout|cancelled",
  "output": "...",
  "reflection": {
    "project": "...",
    "general": "..."
  },
  "errors": [],
  "metadata": {
    "timing": {
      "received_at": "...",
      "started_at": "...",
      "completed_at": "...",
      "total_ms": 0,
      "session_prepare_ms": 0,
      "execute_prompt_ms": 0,
      "persist_sessions_ms": 0,
      "publish_response_ms": 0
    }
  }
}
```

Timing guidance:
- `metadata.timing.*` is daemon-side timing
- caller-side wall time from “skill invoked” to “reply received” should be measured by the caller and reported separately
- compare caller wall time against `metadata.timing.total_ms` to spot queueing, rebalance, or transport delay

## Discovery

When a discovery endpoint exists, use it before sending the request. Discovery should provide:
- `agent`
- `request_topic`
- `request_schema.required`
- `request_schema.optional`
- `supported_agent_params`
- `working_dir_supported`
- `request_example`
- `provider`
- `runtime`
- `model`
- `health_url`

If discovery is unavailable, use these defaults:
- request topic = agent name
- reply topic = caller-generated Kafka topic
- `working_dir` supported

## Example

```json
{
  "type": "request",
  "sender": "master-replies-20260409-01",
  "correlation_id": "req-20260409-01",
  "prompt": "Use your /kord alfred get skill with arguments: key kordinate/deepseek/api-key",
  "working_dir": "/kord/shared/repos/kordinate",
  "timeout_ms": 120000
}
```

## Notes

- Prefer one request per reply topic when testing manually.
- For Alfred, phrase prompts in terms of its `store` and `get` skills.
- For Charon, include deploy intent and target environment explicitly.
- For Augur, use `working_dir` whenever the repo scope matters.
