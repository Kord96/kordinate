# Scribe

Documentation gate — present in every team. Only agent authorized to edit `.md` files. All other agents delegate markdown edits to scribe.

Enforced by `guard-md.sh`: the hook blocks Edit/Write on `.md` files unless scribe's auth token is present.

**Commands**

| Command | Description |
|---------|-------------|
| `/scribe:onboard` | Add a new agent to the team |
| `/scribe:kord` | Define a kord between two agents |
| `/scribe:update-agent-docs` | Update an agent's documentation |
| `/scribe:update-project-docs` | Update project-level docs |
