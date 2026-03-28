# Create Route

Level 3 resource for the register skill. Define a new route — a capability exposed by an agent via Beorn.

## Usage

```
/register route deployer cluster-health "pre-deployment health checks" --skill infra --cache inputs=agents/charon/memory/infra.md
/register route scribe write-memory "persist agent memories" --skill remember
```

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Route name (required, kebab-case, must be unique across all agents)
    - Method — the tool name exposed to callers (required, snake_case)
    - Description — one-line summary of what this route does (required)
    - Provider agent — which agent owns this route (required, determines which `routes.yaml` to edit)
    - Skill — which skill directory handles this route (required, must exist under the agent's `skills/` or global `skills/`)
    - Cache config (optional):
      - `inputs` — list of file/directory paths whose changes invalidate the cache
      - `max_age` — maximum cache age in seconds (default: none)

2. **Validate** before writing:
    - The provider agent directory must exist at `$KORDINATE_HOME/agents/<provider>/`
    - The skill must exist at `$KORDINATE_HOME/agents/<provider>/skills/<skill>/` or `$KORDINATE_HOME/skills/<skill>/`
    - The route name must not already exist in any agent's `routes.yaml`

3. **Add route entry** to `$KORDINATE_HOME/agents/<provider>/routes.yaml`:

    If the file does not exist, create it with the YAML structure:
    ```yaml
    routes: []
    ```

    Append the new route to the `routes` array:
    ```yaml
    routes:
      - name: <route-name>
        method: <method>
        description: <description>
        skill: <skill>
        cache:
          inputs:
            - <path>
          max_age: <seconds>
    ```

    Omit the `cache` section entirely if no cache config is provided.

4. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

5. **Report** what was created:
    - "Route `<name>` added to `agents/<provider>/routes.yaml`."

## Notes

- Routes are pure YAML entries — no directory creation needed.
- Cache invalidation is handled by Beorn at runtime using the `inputs` paths and `max_age`.
- One agent can have many routes, all in a single `routes.yaml`.
