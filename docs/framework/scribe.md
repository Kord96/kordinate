# Scribe

Documentation gate — present in every team. Only agent authorized to edit `.md` files. All other agents delegate markdown edits to scribe.

Enforced by `guard-md.sh`: the hook blocks Edit/Write on `.md` files unless scribe's auth token is present.

**Triggers:** `update docs`, `update project docs`, `add api key`, `add mcp`, `update agent docs`, `write readme`

**Commands**

| Command | Description |
|---------|-------------|
| `/scribe:onboard` | Add a new agent to the team |
| `/scribe:kord` | Define a kord between two agents |
| `/scribe:add-mcp` | Add a new MCP server entry |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
| `/scribe:update-subagent-memory` | Update agent memory files |

## Onboarding an Agent

Use `/scribe:onboard` to add a new agent interactively. Example — adding the **designer** agent:

```bash
/scribe:onboard designer "reviews architecture and owns design patterns"
```

Scribe asks for anything missing:

- **Triggers?** → `review architecture`, `design review`, `check design consistency`
- **Exclusive tools?** → Gemini (design validation)
- **Consultation expertise?** → Component topology, design patterns, data flow, failure modes, dependencies

### What gets created

```
agents/designer/
├── IDENTITY.md                    # identity — role, triggers, commands, rules
├── memory/
│   └── static/
│       └── instructions/      # consultation behavior, cache sources
├── commands/
│   └── detect-patterns.md     # /designer:detect-patterns skill
```

### What gets updated

- **Root IDENTITY.md** — designer added to the routing table and consultation directory
- **settings.json** — guard hook registered (if exclusive tools specified)
- **link-claude.sh** — run to register the new agent with the runtime

### Customize

The generated files are starting points. For designer, we added:

- `memory/static/patterns/*.md` — 16 pattern definitions
- `memory/static/libraries/*.md` — shared library docs
- `commands/detect-patterns.md` — scans a project for recognized patterns
