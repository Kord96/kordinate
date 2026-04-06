# Bootstrap image policy

The agent platform uses layered images:

- `agent-base`
- `agent-<name>`

## Policy

All agent images must be available as prebuilt bootstrap artifacts before a fresh install or disaster recovery rollout.

At minimum, the bootstrap set includes:

- `agent-base`
- `agent-charon`
- `agent-augur`
- `agent-sauron`
- `agent-alfred`
- `agent-warden`

## Why

This avoids bootstrap paradoxes where the platform would need an already-working in-cluster agent to build or repair the image for that same agent.

A fresh install should be able to:

1. pull prebuilt images from the configured `REGISTRY`
2. deploy the platform stack
3. bring up Charon with all required platform tooling already present
4. let Charon manage future image changes and rollouts after the platform is healthy

## Runtime ownership after bootstrap

After the platform is healthy:

- Charon owns future image rollouts
- Charon may trigger kaniko-based rebuilds for agent images
- Charon may apply platform overlays and restart deployments as needed

Bootstrap never depends on those later self-management paths.

## Registry policy

Image references in manifests should use `REGISTRY/<image>:<tag>` placeholders or equivalent config-driven resolution. `REGISTRY` should resolve from Alfred-owned profile source (`agents/alfred/profile/config.yaml`) or the published runtime projection (`shared/runtime/profile/config.yaml`) using `clusters.<name>.services.registry.url` during overlay generation or manifest templating.

Do not hardcode localhost-based registry addresses in platform manifests.

## First layered-image rollout

The first rollout after introducing layered images must ensure the following images exist in `REGISTRY` before restart:

- `agent-base:latest`
- `agent-charon:latest`
- `agent-augur:latest`

The remaining agent-specific images should also be published as bootstrap artifacts even if some workloads still run directly from `agent-base` at first.
