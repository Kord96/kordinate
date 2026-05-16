# kordinate

A framework for kording specialized agents into a team.

```
kordinate/
├── core/           # framework — root agent, hooks, commands, lib
├── shared/         # shared memory, hooks, klaude-daemon, runtime projections, skills, scripts
├── installer/      # setup-shell.sh, kordinate-cli
├── bin/            # repo-global utilities (session/tmux helpers now live with the workstation image)
└── docs/           # documentation site
```

## Quick Start

```bash
git clone <repo-url> ~/kordinate
cd ~/kordinate
# Install: /install (or /install --local for no infra)
```

## Documentation

**[kord96.github.io/kordinate](https://kord96.github.io/kordinate/)**

## Current Status

Kordinate is being reduced to the parts that have not been absorbed by the
newer project boundaries. Scribe owns the canonical manifest reference vault;
Augur owns the Augur runtime/application boundary; Charon owns agent bundle and
deployment packaging.

See [docs/absorbed-by-scribe.md](docs/absorbed-by-scribe.md) for the first
removed manifest/config set.
