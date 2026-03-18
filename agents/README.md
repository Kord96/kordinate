# Agents

Kordinate ships four specialized agents, each scoped to a specific operational domain.

| Agent    | Triggers                                           | Purpose                    |
|----------|---------------------------------------------------|----------------------------|
| deployer | `roll`, `migrate`, `stop`, `clean`, `diff`        | GitOps deployments         |
| sauron   | `add monitoring`, `health check`, `dashboard`, `run tests` | Observability & validation |
| designer | `review architecture`, `design review`            | Architecture review + pattern authority |
| scribe   | `update docs`, `add api key`, `add mcp`, `write readme`   | Documentation (sole `.md` editor) |

## Consultation Protocol

Ask an agent a question without transferring full control:

```
/consult deployer "Is your-app healthy on cluster-a?"
```

## Async Messaging

Send a message to an agent via scribe relay:

```
/scribe:text sauron "Add a dashboard for your-app memory usage"
```

## Hooks (Safety Guardrails)

Hooks intercept tool calls and enforce authorization before execution.

| Hook                 | What It Guards                                                                 |
|----------------------|-------------------------------------------------------------------------------|
| `guard-kubectl.sh`   | Blocks kubectl write operations via SSH unless deployer is authorized. Master namespace requires bootstrap auth. Workstation resources always blocked. |
| `guard-md.sh`        | Blocks `.md` file edits unless scribe is authorized.                          |
| `guard-grafana.sh`   | Blocks Grafana MCP calls unless sauron is authorized.                         |
| `guard-redis.sh`     | Blocks Redis MCP calls unless deployer is authorized.                         |
| `guard-git.sh`       | Blocks git push to test/prod branches unless deployer is authorized.          |
| `auto-merge-to-dev.sh` | Post-push hook that auto-merges session branches to main.                  |

### Lock-Based Authorization

Agents authorize themselves by placing a lock file before operating:

1. Agent copies lock from `profile/locks/<agent>` to `/tmp/.<agent>-auth`
2. Hook compares lock file with `/tmp/` file
3. Agent removes lock file after completing work

## Commands

| Command           | Description                                          |
|-------------------|------------------------------------------------------|
| `/boot`           | Initialize the workstation environment               |
| `/consult`        | Query an agent without full handoff                  |
| `/merge`          | Merge current session branch                         |
| `/deployer:roll`  | Trigger a rolling deployment via the deployer agent  |
| `/scribe:text`    | Send an async message to an agent via scribe         |
