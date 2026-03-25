# kordinate

A framework for kording specialized agents into a team.

```
kordinate/
├── core/           # framework — root agent, scribe, hooks, commands, lib
├── team/           # your agents — deployer, sauron, designer
│   └── config.yaml # site-specific configuration
├── installer/      # setup-shell.sh, kordinate-cli
├── bin/            # claude-session
└── docs/           # documentation site
```

## Quick Start

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
# Linking is handled by scribe via /onboard sync
```

## Documentation

**[kord96.github.io/kordinate](https://kord96.github.io/kordinate/)**
