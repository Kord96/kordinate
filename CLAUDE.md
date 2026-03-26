This is the kordinate development repo. All agent, skill, kord, and infrastructure changes MUST be made here first.

To apply changes to the runtime (`~/.kord/` and `~/.claude/`), run `/install --local` after editing. Do NOT edit `~/.kord/` directly — it will be overwritten on next install.

The installable kordinate package lives at `kordinate/` (i.e., `kordinate/kordinate/` from repo root). Infrastructure manifests and images are under `kordinate/agents/deployer/skills/infra/`.
