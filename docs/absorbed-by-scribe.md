# Content Absorbed By Scribe

Kordinate no longer owns canonical copies of deployment/runtime manifests that
are maintained in the Scribe vault.

Canonical location:

- `/kord/personal-cloud/scribe-vault/References/manifests/kordinate/`

Absorbed content:

- bootstrap Kubernetes manifests formerly under
  `agents/charon/skills/bootstrap/manifests/`
- platform base manifests formerly under
  `agents/charon/skills/platform/manifests/base/`
- runtime/backend config formerly stored in:
  - `BACKENDS.yaml`
  - `shared/runtime/model-catalog.yaml`
  - `shared/runtime/profile/backend-aliases.yaml`
  - `shared/runtime/profile/config.example.yaml`
  - `shared/runtime/profile/model-profiles.yaml`

This repository may still contain scripts, skills, and docs that reference the
old paths. Treat those references as the next cleanup surface, not as active
manifest ownership.
