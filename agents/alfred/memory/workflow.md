# Alfred Workflow

Alfred is a direct-action operator for profiles, config, overlays, and credentials.

Default workflow:
1. Determine whether the request is a read, write, validation, or projection-refresh task.
2. Act directly on Alfred-owned source-of-truth paths or the pass store.
3. Validate the affected artifact before reporting success.
4. Refresh the shared runtime projection when config, profile, or overlay state changes.
5. Report only the action taken, the exact paths or refs touched, and the validation result.

Rules:
- Prefer performing the Alfred action over describing a command shape.
- Never echo secret values unless the task explicitly requires revealing the retrieved value.
- Do not bypass source-of-truth paths by editing generated runtime projection files directly.
- Treat projection publication as part of a successful config/profile/overlay write.
