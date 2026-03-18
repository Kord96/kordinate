# kordinate

An agent operations framework for multi-cluster Kubernetes infrastructure.

Kordinate provides specialized agents, safety guardrails, and a GitOps pipeline — orchestrated through an AI coding assistant running inside a Kubernetes pod.

## How It Works

```
              ┌────────┐
              │  You   │
              └───┬────┘
                  │ Tailscale SSH
    ┌─────────────▼──────────────────┐
    │        Workstation Pod         │
    │                                │
    │  tmux ─► Claude Code           │
    │               │                │
    │        ┌──────┴──────┐         │
    │        │   Agents    │         │
    │        │  deployer   │────┐    │
    │        │  sauron     │    │    │
    │        │  designer   │  hooks  │
    │        │  scribe     │  check  │
    │        └─────────────┘  every  │
    │                         tool   │
    │                         call   │
    └─────────────────────────┼──────┘
                              │
                      SSH + kubectl
                 ┌────────┼────────┐
                 │        │        │
           ┌─────▼──┐ ┌──▼─────┐  │
           │cluster-a│ │cluster-b│ ...
           │ dev     │ │ dev     │
           │ test    │ │ test    │
           │ prod    │ │ prod    │
           └─────────┘ └────────┘
```

The framework is **agent-agnostic** — a linking layer maps kordinate's internal structure to whatever AI agent runtime you use:

```
┌──────────────┐     link.sh      ┌──────────────┐     ┌──────────────┐
│  kordinate/  │ ─── mapping ───► │  ~/.claude/   │ ◄── │  Claude Code  │
│  (repo)      │                  │  (symlinks)   │     │              │
└──────────────┘                  └──────────────┘     └──────────────┘
```

## Agents

| Agent | What it does |
|-------|-------------|
| **deployer** | Rolls deployments between environments, manages infrastructure |
| **sauron** | Adds monitoring, validates code quality, manages dashboards |
| **designer** | Reviews architecture, owns design patterns |
| **scribe** | Sole editor of documentation files |

Each agent has its own commands, memory, and safety hooks. See [docs/agents.md](docs/agents.md).

## Workflow

tmux auto-attaches on SSH login. Each project gets its own session.

```
tmux
├── kordinate (session)
│   ├── window 0 → main branch
│   ├── window 1 → session/w1 (worktree)
│   └── window 2 → session/w2 (worktree)
└── your-project (session)
    ├── window 0 → main branch
    └── window 1 → session/w1 (worktree)
```

Each window creates an isolated worktree + branch. On exit: push + PR, or cleanup if no changes.

Branch flow: `session/*` → `main` → `test` → `prod`

## Quick Start

Prerequisites: Linux, `git`, `gh`, `curl`, `python3`, Tailscale, GPG key.

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
./installer/link.sh              # link framework into ~/.claude/
./installer/kordinate-cli init   # bootstrap k8s + workstation
```

Joining an existing cluster:

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
git-crypt unlock                 # decrypt profile/
./installer/link.sh
./installer/kordinate-cli hydrate
```

## Repository Structure

```
~/kordinate/
├── kordinate/                   # Framework
│   ├── agents/                  #   agent definitions + memory
│   ├── commands/                #   shared slash commands
│   ├── hooks/                   #   safety guardrails
│   ├── profile/                 #   site config (encrypted)
│   └── settings.json            #   hook registrations
├── installer/                   # Bootstrap + linking
├── bin/                         # Session management
└── docs/                        # Documentation
```

## Documentation

| Doc | Level | Topic |
|-----|-------|-------|
| [docs/overview.md](docs/overview.md) | Start here | How the pieces fit together |
| [docs/agents.md](docs/agents.md) | Mid-level | Agents, hooks, commands, consultation |
| [docs/memory.md](docs/memory.md) | Mid-level | Memory model: static, dynamic, project |
| [docs/profile.md](docs/profile.md) | Reference | Site-specific config and YAML structure |
| [docs/claude-links.md](docs/claude-links.md) | Reference | Link mapping (kordinate → Claude Code) |
