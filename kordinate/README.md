# kordinate framework

The Claude Code framework: agents, hooks, commands, and site-specific config. Linked into `~/.claude/` via [installer/link.sh](../installer/link.sh).

## Agents

| Agent    | Triggers                                           | Purpose                    |
|----------|---------------------------------------------------|----------------------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff`        | GitOps deployments         |
| sauron   | `add monitoring`, `add metrics`, `health check`, `dashboard`, `set up logging`, `run tests`, `code validation` | Observability & validation |
| designer | `review architecture`, `design review`            | Architecture review + pattern authority |
| scribe   | `update docs`, `add api key`, `add mcp`, `write readme`   | Documentation (sole `.md` editor) |

```
User message
 │
 ├── matches trigger ──► spawn agent
 │   ├── deployer ──► kubectl ops   (guard-kubectl, guard-git, guard-redis)
 │   ├── sauron ────► monitoring    (guard-grafana)
 │   ├── designer ──► architecture
 │   └── scribe ────► .md edits     (guard-md)
 │
 └── /consult <agent> "question"
     └── agent reads knowledge ──► returns answer
```

See [agents/README.md](agents/README.md) for lock-based authorization and consultation protocol.

## Hooks

| Hook                 | What It Guards                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| `guard-kubectl.sh`   | Blocks kubectl write operations via SSH unless deployer is authorized. Master namespace requires bootstrap auth. Workstation resources always blocked. |
| `guard-md.sh`        | Blocks `.md` file edits unless scribe is authorized.                          |
| `guard-grafana.sh`   | Blocks Grafana MCP calls unless sauron is authorized.                         |
| `guard-redis.sh`     | Blocks Redis MCP calls unless deployer is authorized.                         |
| `guard-git.sh`       | Blocks git push to test/prod branches unless deployer is authorized.          |
| `auto-merge-to-dev.sh` | Post-push hook that auto-merges session branches to main.                  |

## Commands

| Command           | Description                                          |
|-------------------|------------------------------------------------------|
| `/boot`           | Initialize the workstation environment               |
| `/consult`        | Query an agent without full handoff                  |
| `/merge`          | Merge current session branch                         |
| `/deployer:roll`  | Trigger a rolling deployment via the deployer agent  |

## Profile

Site-specific config at `profile/` — git-crypt encrypted. See [profile/README.md](profile/README.md) for the full layout.

| File | Purpose |
|------|---------|
| `config.yaml` | Cluster IPs, ports, services, registry |
| `topology.yaml` | App definitions, monitoring, health thresholds |
| `mcp.json` | MCP server config |
| `settings.json` | Claude Code hooks, permissions |
| `locks/` | Agent auth locks |
| `keystore/` | Symlink to `pass` store |
