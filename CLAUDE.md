This is the kordinate development repo. Agents run as Kubernetes pods with persistent Claude sessions.

Structure:
- `agents/` — 5 agents (alfred, augur, charon, sauron, warden) with IDENTITY.md, memory/, skills/
- `team/` — shared hooks, skills, protocols
- `lib/` — agent-pod-daemon (stream-json bridge), job-router, agent-curator, hooks, scripts
- `installer/` — cluster bootstrap scripts
- `bin/` — session and tmux utilities

Infrastructure manifests are under `agents/charon/skills/bootstrap/manifests/`.

Pod project directories are generated at `/kord/agents/<name>/` by `lib/scripts/setup-agent-dir.sh`.
