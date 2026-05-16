# Platform Build And Storage Design

This document records the recommended near-term design for image builds,
registry storage, MinIO storage, corpus storage, and Google Drive mounts.

## Constraints

- Builds are a recurring operator task and must be fast enough for normal
  platform iteration.
- Workstation lifecycle should not own durable platform state.
- Root disk pressure is real; `/mnt/hdd` has enough space for cold/bulk data.
- Existing Charon docs define useful registry-backed build/deploy mechanics, but
  Charon should no longer be assumed to remain a required long-running platform
  agent.
- Existing scripts already build agent images with host Docker.
- Current cluster registry and MinIO use `local-path` and are tied to the active
  node/root disk.
- The target Kordinate shape is skills-first: simple agent responsibilities move
  into skills/scripts, while complex systems like Augur keep their own repo
  boundary.

## Recommended Build Path

Use host Docker as the near-term build engine, but only through standardized
Kordinate scripts or Codex skills.

Rationale:

- It is already installed and working on `ottawa-server`.
- It is likely faster than introducing Kaniko as the default build path.
- Existing `lib/scripts/build-agent-images.sh` uses Docker and knows the current
  platform image set.
- Platform manifests already expose `/var/run/docker.sock` to some Charon-owned
  pods, so the platform has implicitly accepted host Docker as an operator
  boundary.

Rules:

- Do not run random Docker builds from workstation state.
- Build through `lib/scripts/build-agent-images.sh` or a future
  `platform-build-deploy` wrapper/skill.
- Push every build to the cluster registry.
- Use immutable timestamp tags for rollouts.
- Keep `latest` for bootstrap compatibility, but do not rely on `latest` alone
  for production rollouts.
- Use registry cache-from behavior where possible.
- Build/deploy wrappers should remain useful even if most simple platform agents
  are retired, because Augur and future containerized deterministic workers
  still need a standard image path.

Future option:

- Add BuildKit after the registry/storage path is clean if Docker build speed,
  isolation, or cache behavior becomes a bottleneck.
- Defer Kaniko as the default until measured. It is useful for fully in-cluster
  builds, but may be slower and adds another moving part.

## Recommended Image Flow

```text
source repo
  -> host Docker build
  -> local cluster registry
  -> rollout helper sets deployment image to immutable tag
  -> rollout status verification
```

For platform agent images:

```bash
lib/scripts/build-agent-images.sh <registry> --image <image> --tag <timestamp> --verify-local
python3 lib/scripts/roll-platform-image.py <image> <registry> <timestamp> --env <env>
```

The future `platform-build-deploy` skill/command should wrap this and add:

- registry resolution from Alfred/runtime profile
- timestamp generation
- preflight checks
- build log capture
- rollout verification
- clear failure classification: build, push, pull, rollout, health

If the multi-agent platform is retired, the same command should narrow its scope
to the remaining containerized projects rather than preserving all old platform
agent targets.

## Recommended Storage Path

Use `/mnt/hdd/kord-storage` for cold and bulky host-level data.

Proposed host layout:

```text
/mnt/hdd/kord-storage/
  registry/
  minio/
  corpus/
  rclone/
  build-cache/
```

Use fast/root/Longhorn storage for:

- active databases
- active queue/runtime state
- hot agent runtime state
- small files where latency matters more than size

Use HDD storage for:

- corpus repository cache
- materialized testing worktrees
- registry blobs
- MinIO archive/object data
- rclone cache/config/logs
- Docker/BuildKit cache if later moved deliberately

## Registry Recommendation

Move registry backing data to `/mnt/hdd/kord-storage/registry` after a migration
plan is written.

Reasoning:

- Registry blobs are bulky and root disk pressure matters.
- Build and pull speed matters, but a local HDD should be acceptable for normal
  operator iteration.
- The bigger current problem is inconsistent registry references
  (`REGISTRY/...`, `localhost:30500/...`, `registry.kord:5000/...`), not raw
  disk speed.

Do first:

- Repair registry resolution in overlays.
- Decide one canonical internal registry address.
- Add build/deploy wrapper.
- Back up or validate registry contents before moving storage.

## MinIO Recommendation

Move MinIO data to `/mnt/hdd/kord-storage/minio` if it is used for archive or
object data rather than latency-sensitive service state.

Do first:

- Move credentials into Kubernetes Secrets.
- Decide whether MinIO is still needed as platform object storage.
- Check bucket contents and size.
- Plan migration with downtime or a second MinIO instance.

## Corpus Recommendation

Create a corpus storage contract before moving current corpus data.

Desired behavior:

- source repo cache is read-only to consumers
- callers request materialized worktrees for a specific SHA
- project selectors return manifests/paths, not mutable repo directories
- dev work never happens in corpus source cache

Likely layout:

```text
/mnt/hdd/kord-storage/corpus/
  cache/
    github.com/
      owner/
        repo.git/
  materialized/
    <project>/
      <selection-id>/
  manifests/
```

This should become a `corpus` CLI plus a skill/runbook.

## Shared Runtime Recommendation

Do not treat `/kord/shared` as a long-term requirement unless a surviving
workload needs it.

Current agent manifests mount:

- `agent-runtime` at `/kord`
- a PVC named `kord` at `/kord/shared`
- repos under `/kord/shared/repos`

That design made sense for a live multi-agent platform. If simple agents become
skills used by one main agent, shared repos can move to explicit local paths,
corpus-managed paths, or project-specific checkouts instead of a Kubernetes-wide
shared PVC.

Near-term rule:

- If a workload will be retired, do not fix its `/kord/shared` scheduling
  failure.
- If a workload survives temporarily, either create the namespace-local `kord`
  PVC as a compatibility repair or patch the manifest to use a clearer
  `kord-shared` contract.
- Long-term, prefer no implicit shared mount. Skills should accept explicit
  paths and corpus selectors.

## Google Drive Recommendation

Use `rclone mount` for the initial desired user experience:

```text
mount -> edit files -> rclone writes to Google Drive
```

Prefer host-level rclone mount if multiple containers or future services need
the same path. Store rclone cache/logs/config under:

```text
/mnt/hdd/kord-storage/rclone/
```

Do not introduce PVC sync or bidirectional copy until there is a concrete need.

## Open Decisions

- Exact canonical registry address.
- Whether `registry.kord:5000` should resolve cluster-wide, host-wide, or both.
- Which current platform agents survive the skills-first simplification.
- Whether any surviving workload still needs `/kord/shared`.
- Whether MinIO remains platform-critical.
- Whether the HDD should be bind-mounted into Kubernetes through hostPath PVs or
  managed by host-level services directly.
