# kordinate

A Claude Code operations framework for multi-cluster Kubernetes infrastructure.

## Architecture

- The workstation is a Kubernetes pod in the `master` namespace with a PVC-backed home directory at `/home/claude`, running Claude Code with 4 specialized agents.
- Agents manage remote clusters over SSH through Tailscale. Safety hooks enforce per-agent permissions.
- Each cluster runs independent dev/test/prod environments; the workstation orchestrates across all of them.

## Workflow

tmux auto-attaches on SSH login. Each project gets its own session.

```
tmux
├── kordinate (session)
│   ├── window 0 → main branch (direct)
│   ├── window 1 → session/w1-kordinate (worktree)
│   └── window 2 → session/w2-kordinate (worktree)
└── your-project (session)
    ├── window 0 → main branch
    └── window 1 → session/w1-your-project (worktree)
```

Each window runs `bin/claude-session`:
- **Open** — creates a git worktree + session branch, launches Claude Code
- **Exit** — pushes and creates a PR, or cleans up if no changes

Branch flow: `session/*` → `main` → `test` → `prod`.

## Quick Start

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
./installer/link.sh
./installer/kordinate-cli init
```

## Repository Structure

```
~/kordinate/
├── kordinate/              # Framework (linked into ~/.claude/)
│   ├── agents/             # Agent definitions, commands, memory
│   ├── commands/           # Shared slash commands
│   ├── hooks/              # Safety guardrail hooks
│   ├── profile/            # Site-specific config (encrypted)
│   └── settings.json       # Hook registrations
├── installer/              # Bootstrap + linking
├── bin/                    # Session + tmux helpers
├── docs/                   # Documentation
└── README.md
```

## Documentation

| Doc | Topic |
|-----|-------|
| [docs/agents.md](docs/agents.md) | Agents, hooks, locks, commands, memory model |
| [docs/profile.md](docs/profile.md) | Site-specific configuration and layout |
| [docs/installer.md](docs/installer.md) | Bootstrap CLI and linking |
| [docs/links.md](docs/links.md) | Link mapping (kordinate → Claude Code) |
