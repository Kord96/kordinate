# Alfred Memory Bundle — Secrets Heavy v1

Use this bundle when the task is primarily about credentials.

Rules:
- secrets live in `pass`, not plaintext files
- key-path correctness matters more than prose explanation
- verify writes with `pass show <path>`
- never echo secret values in normal confirmation output
- if a task explicitly requests the retrieved secret value, return only that value and no extra commentary

When in doubt:
- confirm the key path
- perform the read or write
- report the ref and validation result
