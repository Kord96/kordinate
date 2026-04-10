# Alfred Paths

| Domain | Path | Notes |
| --- | --- | --- |
| config | `$KORDINATE_HOME/agents/alfred/profile/config.yaml` | Alfred-owned source of truth |
| profiles | `$KORDINATE_HOME/agents/alfred/profile/model-profiles.yaml` | Reusable backend profile definitions |
| backend aliases | `$KORDINATE_HOME/agents/alfred/profile/backend-aliases.yaml` | Stable backend alias mapping |
| overlays | `$KORDINATE_HOME/agents/alfred/profile/overlays/<cluster>/<namespace>/` | Kustomize overlay source tree |
| platform overlays | `$KORDINATE_HOME/agents/alfred/profile/overlays/platform/<env>/` | Per-environment agent scaling and resources |
| runtime projection | `$KORDINATE_HOME/shared/runtime/profile/` | Read-only published projection for runtime/bootstrap consumers |
| runtime home | `$AGENT_HOME_DIR` | Seeded runtime files for the current Alfred instance |
| shared memory | `/kord/shared/memory/` | Shared memory and cross-agent artifacts |

Use source-of-truth paths for writes. Use the runtime projection only for consumers that need a published read-only view.
