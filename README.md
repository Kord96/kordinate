# kordinate

A framework for kording specialized agents into a team.

```
kordinate/
├── core/           # framework — root agent, scribe, hooks, commands, lib
├── team/           # your agents — deployer, sauron, designer
│   └── config.yaml # site-specific configuration
├── installer/      # link-claude.sh, setup-shell.sh
├── bin/            # claude-session
└── docs/           # documentation site
```

## Quick Start

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
./installer/link-claude.sh
```

## Documentation

**[kord96.github.io/kordinate](https://kord96.github.io/kordinate/)**
