# Alfred Contracts

## Source of Truth

Alfred owns:
- `agents/alfred/profile/model-profiles.yaml`
- `agents/alfred/profile/backend-aliases.yaml`
- `agents/alfred/profile/config.yaml`
- `agents/alfred/profile/overlays/**`
- pass store entries under the `kordinate/` prefix

Runtime/bootstrap consumers should prefer the published projection under:
- `shared/runtime/profile/`

They should not mutate Alfred-owned source files directly.

## Update Contract

When Alfred changes:
- config
- profile definitions
- backend aliases
- overlays

it should:
1. validate the updated source files
2. publish the runtime projection
3. report the exact source path changed

When Alfred changes a secret, it should:
1. write through `pass`
2. verify the entry exists
3. report the key path only, not the secret value
