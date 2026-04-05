This is the kordinate development repo. Agents run as Kubernetes pods with persistent Claude sessions.

Structure:
- `agents/` — 5 agents (alfred, augur, charon, sauron, warden) with IDENTITY.md, memory/, skills/
- `shared/` — shared memory, hooks, skills, protocols
- `lib/` — agent-pod-daemon (stream-json bridge), job-router, agent-scribe, hooks, scripts
- `installer/` — cluster bootstrap scripts
- `bin/` — session and tmux utilities

Infrastructure manifests are under `agents/charon/skills/bootstrap/manifests/`.

Built-in PVC directories are created by bootstrap under `/kord/<name>/`; new agent PVC paths should be provisioned by Charon skills.
