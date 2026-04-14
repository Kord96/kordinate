# Augur E2E Checklist

Use this checklist before treating a live Augur `/analyze` run as trustworthy system evidence.

## Execution

Verify:

- the intended agent/backend responded successfully
- the intended repo and pinned SHA were used
- outputs were written under the expected runtime path

## Output

Verify:

- `blast.json`
- `facts/`
- `atlas.json`
- `stories/`
- `narratives.yaml`

and confirm they parse and validate successfully.

## Telemetry

Verify:

- timing is captured
- token usage is captured when available
- provider/runtime identity is present

## Caching

Verify repeated runs expose cache behavior when the backend supports it.

## Reflection

Verify reflection is captured and stored when enabled.
