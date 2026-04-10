# Alfred Skill Bundle — Validation Core v1

Validation expectations by artifact:

- `key`
  - verify the pass entry exists after write

- `config`
  - validate required fields
  - reject invalid structure or invalid ports/IPs

- `profile`
  - require profile and model fields
  - preserve backend/provider consistency

- `overlay`
  - ensure expected kustomize files are present
  - reject obviously broken base or patch references

- `platform scaling`
  - ensure integer min/max/cooldown values
  - require `min <= max`
  - require non-negative cooldown

Do not report success if validation fails.

Escalation rules:
- if the request is outside Alfred's domain, say so briefly and point to the owning agent
- if the correct path or key ref is ambiguous, resolve the ambiguity before writing
- when returning a failure, prefer the exact failing path, key ref, or field over generic explanation
