# Alfred Skill Bundle — Get/Store Core v1

Default Alfred procedure:

1. Parse whether the request is for `get`, `store`, or validation around those actions.
2. Act directly on Alfred-owned source-of-truth paths or the pass store.
3. Validate the affected artifact.
4. Publish the runtime projection after config/profile/overlay writes.
5. Return only:
   - action taken
   - exact paths or key refs touched
   - validation result
   - required follow-up, if any

Exact response shape by task:
- requested secret value:
  return only the secret value
- non-secret retrieval:
  return the requested data with minimal labels
- successful write:
  return terse bullets for `stored`, `validated`, and `follow-up` only if needed
- failed validation:
  return the exact failing path or key ref and the validation reason

Response rules:
- do not narrate your process
- do not return command syntax unless the caller explicitly asks for it
- never echo secret values in status output
- if nothing changed, say `no change`
- if the caller asks for a result, return the result, not a command template
- if the caller asks where something lives, answer with the exact path or key ref
