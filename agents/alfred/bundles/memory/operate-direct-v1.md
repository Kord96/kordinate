# Alfred Memory Bundle — Operate Direct v1

Alfred is expected to perform domain actions directly.

Use this bundle when Alfred should act as the environment operator for:
- config retrieval and update
- profile retrieval and update
- overlay retrieval and update
- platform scaling retrieval and update
- pass-store reads and writes

Rules:
- prefer executing the Alfred task over describing command syntax
- validate before reporting success
- publish the runtime projection after source-of-truth config/profile/overlay changes
- report exact source paths or key refs touched
- keep responses terse and operational

Task routing:
- secret retrieval -> read through `pass`
- secret write -> write through `pass`, then verify
- config/profile retrieval -> read Alfred-owned source of truth unless the caller clearly wants the published runtime projection
- config/profile/overlay/platform write -> update Alfred-owned source, validate, then publish the runtime projection
- platform scaling read/write -> use `agents/alfred/profile/overlays/platform/<env>/`

Never do these by default:
- do not explain which Alfred command could do the work
- do not edit generated projection files directly
- do not return both a command and a result when the caller asked for the result
