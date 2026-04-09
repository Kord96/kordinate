# klaude-daemon

Shared Kordinate runtime package for the Kafka-backed Klaude daemon.

This package was integrated from the former standalone `klaude-daemon` repo so
runtime behavior can live under `shared/` while remaining independently
buildable.

## What it does

- consumes per-agent Kafka request messages
- resumes or creates provider sessions
- executes prompts through Codex, Claude SDK, or the `openclaude` harness
- publishes responses and optional reflections
- optionally registers agent metadata to a discovery server
- persists provider session IDs to disk
- supports `AGENT_PROFILE` so deployed agent names can reuse specialist flavors

## Platform Contract

- agent pods should execute `klaude-daemon`
- Charon owns the pod manifests that run this package in-cluster
- this package may invoke `openclaude` internally for the `openclaude-harness` runtime, but pods should not be wired directly to `openclaude-daemon`

## Commands

Run these from this directory:

```bash
npm run build
npm test
npm run start
npm run start:discovery
```

## Ownership

- `shared/klaude-daemon/` owns daemon runtime implementation
- Alfred owns runtime profile/config inputs under `agents/alfred/profile/`
- Charon owns deployment/manifests for running the daemon in-cluster
