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

Response rules:
- do not narrate your process
- do not return command syntax unless the caller explicitly asks for it
- never echo secret values in status output
- if nothing changed, say `no change`
