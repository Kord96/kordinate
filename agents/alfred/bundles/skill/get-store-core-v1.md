# Alfred Skill Bundle — Get/Store Core v1

- Classify the prompt first:
  - `get_secret`
  - `store_secret`
  - `get_source_value`
  - `set_source_value`
  - `get_overlay`
  - `set_overlay`
  - `get_platform_scaling`
  - `set_platform_scaling`
- `get key <path>`: run `pass show <path>` and return the value only.
- `store key <path> <value>`: write through `pass`, verify with `pass show <path>`, and never echo the secret in confirmation output.
- For those exact secret operations, success requires the direct `pass` action to happen. Empty or generic assistant output is a failure.
- For config, profile, overlay, and platform changes, update the Alfred source of truth, validate, then publish the runtime projection.
- Keep simple tasks narrow: direct action first, direct verification second, then answer.
- If the direct action fails, report the concrete failure instead of broad exploration.
