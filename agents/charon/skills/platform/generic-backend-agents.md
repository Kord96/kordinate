# Generic Backend Agents

Generic backend agents are daemon-backed platform entries that do not seed one of the built-in specialist overlays.

Use them when you want:
- a consultation or utility agent with plain runtime/backend behavior
- a deployed agent name that is not one of `augur`, `charon`, `alfred`, or `sauron`
- a Kafka-addressable daemon runtime without creating a bespoke specialist image first

## Recommended Defaults

- `flavor: generic`
- `runtime.command: ["klaude-daemon"]`
- `runtime.daemon.kind`: inferred from the model family
  - GPT family -> `codex-sdk`
  - Claude family -> `claude-agent-sdk`
  - everything else -> `openclaude-harness`
- `image.customization: none`

## Creation Path

Use the Charon platform workflow:

```text
/platform create-agent <name> --profile generic --provider <provider> --model <model> --backend <backend>
```

This updates `agent-spec.yaml`, regenerates platform manifests, and prepares the new agent for the normal `/platform deploy <env>` path.

## When Not To Use Generic

Do not use `generic` when:
- the agent should seed one of the built-in specialist overlays
- the agent requires a custom image customization that already exists as a named specialist path
- the runtime needs unique deployment conventions that exceed the normal daemon-backed platform model
