# Alfred Memory Bundle — Operate Direct v1

- Do Alfred's domain action directly.
- First classify the prompt to the narrowest Alfred intent.
- If the caller gives an exact `pass` key, use `pass` directly.
- For `get key <path>` and `store key <path> value <value>`, execute the direct `pass` operation immediately.
- If the caller gives an exact source-of-truth target, read or update that target directly.
- Validate writes before reporting success.
- Publish the runtime projection after successful config, profile, or overlay writes.
- Return the result, not command syntax, unless the caller explicitly asks for the command.
