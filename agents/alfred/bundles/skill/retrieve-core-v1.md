# Alfred Skill Bundle — Retrieve Core v1

This bundle is for retrieval-heavy Alfred work.

Procedure:
1. Identify the requested artifact class:
   - path
   - profile field
   - config field
   - platform scaling field
   - secret value
2. Read the narrowest authoritative source needed to answer it.
3. Return only the requested result.

Source selection:
- profile definitions -> `agents/alfred/profile/model-profiles.yaml`
- backend aliases -> `agents/alfred/profile/backend-aliases.yaml`
- config -> `agents/alfred/profile/config.yaml`
- platform scaling -> `agents/alfred/profile/overlays/platform/<env>/scaling.yaml`
- secrets -> `pass show <path>`

Output rules:
- if the caller asked for an exact path, return only the path
- if the caller asked for a single model or field value, return only that value
- if the caller asked for min/max/cooldown, return only those values
- do not include command syntax
- do not include narrative explanation unless the caller asks for it
- do not mix result and instructions in the same answer
