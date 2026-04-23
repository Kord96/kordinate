# Augur Release Contract

Augur is moving from a monorepo specialization under `kordinate` to a publishable artifact with a stable runtime contract.

This document defines the intended boundary.

## Why

The current arrangement couples Augur to the `kordinate` source tree:

- some scripts still assume `/app/agents/augur` or `/kord/workstation/home/project/kordinate`
- Charon bakes Augur directly from source into `agent-augur`
- local tests can accidentally rely on neighboring repo state rather than on a real installed Augur runtime

That makes local testing less production-faithful than it should be.

## Boundary

Charon should interact with Augur as a versioned release artifact, not as a source checkout.

The release unit is:

```text
augur-<version>.tar.gz
augur-release.json
```

The manifest contract is defined in:

- [`schemas/augur-release-schema.md`](../schemas/augur-release-schema.md)

## What a release contains

The release must contain the runtime-facing Augur surface:

- `IDENTITY.md`
- `README.md`
- `INDEX.yaml`
- `detectors/`
- `memory/`
- `schemas/`
- `skills/`
- `scripts/`
- `.generated/bundles/`

Benchmarks and research notes are intentionally excluded from the runtime artifact.

## Stable runtime entrypoints

Consumers should resolve these from `augur-release.json`:

- `scripts/run/prepare_analysis_dir.py`
- `scripts/run/prepare_deterministic_run.py`
- `scripts/run/build_analysis_context.py`
- `scripts/run/build_prompt_context.py`
- `scripts/run/build_validation_repair_prompt.py`
- `scripts/run/finalize_analysis.py`
- `skills/analyze/validator/validate.py`

## Charon responsibilities

Charon owns publication and channel management:

- build or receive a release artifact
- stage it into the shared artifact store
- publish channel pointers such as `stable` or `candidate`
- install or mount a selected version for runtime consumers

Charon should not rely on `agents/augur/...` source paths once the release path is active.

## Local testing target

The production-faithful local test path should become:

1. build a release artifact from Augur source
2. publish it through the Charon-owned publisher
3. resolve that published version locally
4. run Augur from the published release root, not from the monorepo checkout

That is the test methodology we should prefer before treating local results as production-like.

