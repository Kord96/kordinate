Invalidate consultation caches where a given agent is the consultant.

Call this after making changes that affect your knowledge (e.g., updating memory, deploying new versions, modifying dashboards).

**Input**: $ARGUMENTS (required: `<agent>`, e.g., `deployer`)

## Usage

```
/invalidate deployer
/invalidate designer
```

## Procedure

1. Parse the agent name from arguments. This is the agent whose knowledge has changed.

2. Resolve the cache directory:
   - Find `KORDINATE_HOME` from the kordinate repo root
   - Cache dir: `agents/shared/memory/dynamic/`

3. Find and remove all hash files where this agent is the consultant:
   ```bash
   KORDINATE_HOME="${KORDINATE_HOME:-$(git rev-parse --show-toplevel)/kordinate}"
   count=0
   for hash_file in "$KORDINATE_HOME/agents/shared/memory/dynamic"/.*-<agent>.hash; do
     [ -f "$hash_file" ] || continue
     rm -f "$hash_file"
     count=$((count + 1))
   done
   ```

4. Report: "Invalidated $count consultation cache(s) for <agent>."
   Cache content files are preserved as fallback — they'll be refreshed on next `/consult`.
