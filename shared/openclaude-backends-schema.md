---
description: Generic BACKENDS.json schema for any agent using OpenClaude as the harness
audience: all-agents
---

# BACKENDS.json

Any agent may define `BACKENDS.json` in its agent directory to declare one or more backend model targets behind the same OpenClaude harness.

Path:
- `agents/<agent>/BACKENDS.json`

## Shape

```json
{
  "version": 2,
  "selection": "first|random|hash",
  "backends": [
    {
      "name": "human-readable-backend-name",
      "profile": "anthropic|openai|gemini|ollama|<other-openclaude-profile>",
      "provider": "anthropic|openai|gemini|...",
      "model": "provider-specific-model-name",
      "base_url": "https://optional-provider-endpoint.example/v1",
      "api_key_env": "OPTIONAL_ENV_VAR_NAME",
      "api_key_ref": "optional/pass/store/reference",
      "env_passthrough": ["OPTIONAL_ENV_1", "OPTIONAL_ENV_2"],
      "extra_env": {
        "OPTIONAL_ENV_NAME": "value"
      }
    }
  ]
}
```

## Required fields

Top-level:
- `backends` — non-empty array

Per backend:
- `name`
- `profile`
- `model`

## Selection modes

- `first` — always use the first backend in the list
- `random` — choose a random backend when the pod boots
- `hash` — deterministically choose a backend from the pod name; useful for multi-replica agents

## Notes

- `profile` describes the OpenClaude harness mode.
- `provider` is optional; if omitted, it defaults to `profile`.
- `base_url` is typically used for `openai`, `ollama`, or other compatible endpoints.
- `api_key_env` should usually be preferred over embedding secrets in generated files.
- `api_key_ref` may still be carried as metadata, but runtime auth should come from pod env vars.
- `env_passthrough` and `extra_env` are optional escape hatches for provider-specific setup.

## Example

```json
{
  "version": 2,
  "selection": "hash",
  "backends": [
    {
      "name": "anthropic-opus",
      "profile": "anthropic",
      "provider": "anthropic",
      "model": "claude-opus-4-6",
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    {
      "name": "deepseek-reasoner",
      "profile": "openai",
      "provider": "openai",
      "model": "deepseek-reasoner",
      "base_url": "https://api.deepseek.com",
      "api_key_env": "DEEPSEEK_API_KEY"
    }
  ]
}
```

## Operational intent

This file is generic and may be used by any agent. It lets multiple pods for the same logical agent role run different backends while preserving a single skill/identity surface.
