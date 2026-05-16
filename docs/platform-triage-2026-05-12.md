# Platform Triage 2026-05-12

Raw inventory: `docs/inventory/2026-05-12-ottawa-server-platform.txt`.

This triage separates observed facts from proposed cleanup. Do not execute the
cleanup actions until the owner confirms data-retention expectations.

## Strategic Pivot

The target direction is no longer a broad multi-agent platform where simple
agents run continuously in Kubernetes. Kordinate should become a simpler
skills-first operational repo:

- simple agent responsibilities become Codex skills, scripts, and runbooks
- complex systems such as Augur remain their own repos/projects
- useful Augur architecture can be preserved: deterministic containerized work
  separated from semantic agent reasoning
- `/kord/shared` should be treated as a legacy compatibility mount unless a
  surviving workload proves it still needs shared repo state

This changes cleanup priorities. Repairing every broken platform agent is less
important than deciding which workloads survive the simplification.

## High-Confidence Observations

### Root Disk Is Carrying Too Much

`ottawa-server` has a 915Gi root filesystem at 74% usage and a 916Gi HDD mounted
at `/mnt/hdd` with almost all space free.

Current bulky services on root-backed storage:

- `registry/registry-data` uses `local-path`.
- `gateway/minio-data` uses `local-path`.
- Docker's root is `/var/snap/docker/common/var-lib-docker`.
- k3s local-path and Longhorn engine data also live under root-managed paths.

### Registry Exists But Platform Image Resolution Is Inconsistent

The cluster has a registry service:

- Namespace: `registry`
- Service: NodePort `30500`
- PVC: `registry-data`

Live workloads use a mix of image forms:

- `localhost:30500/...`
- `registry.kord:5000/...`
- unresolved `REGISTRY/...`
- bare local images such as `barren:latest`

Charon docs say platform manifests should resolve `REGISTRY` through overlays
and should not hardcode localhost-based registry addresses in platform
manifests.

### MinIO Exists But Is Not Yet On The Desired Secret/Storage Path

MinIO is running in `gateway` and uses `gateway/minio-data` on `local-path`.
The observed deployment has root credentials in environment values rather than
secret references.

### Longhorn Has Degraded Volumes

Several attached Longhorn volumes report `degraded`. `master/kord` reports
`healthy`. Disabled/offline nodes likely affect replica health and scheduling.

Do not infer data loss from `degraded` alone; inspect Longhorn replicas and
scheduling settings before repair.

### Several Retained PVs Are Released

The inventory shows many `Released` PVs with `Retain`, especially older
monitoring, workstation, and admin volumes. These are cleanup candidates only
after data retention is confirmed.

### Some Kord Namespace Pods Expect A Namespace-Local `kord` PVC

Recent events show pods in namespace `kord` failing scheduling because
`persistentvolumeclaim "kord" not found`. The existing `kord` PVC is in
namespace `master`, not `kord`. There is also a `kord/agent-runtime` PVC.

This is probably a manifest/runtime projection mismatch and should be fixed in
the Charon/Alfred overlay path, not by manually creating ad hoc PVCs.

Current source manifests show why the missing PVC matters:

- `agent-runtime` is mounted at `/kord`.
- `kord` is mounted at `/kord/shared`.
- agents set `PROJECTS_ROOT=/kord/shared/repos`.

So `kord` is the shared project/repo/artifact surface for agent pods, not a
throwaway mount. The scheduling failures are expected until the namespace-local
shared PVC story is fixed.

Under the skills-first direction, this is probably not a strategic mount to
preserve. It should be fixed only as a temporary compatibility step if a
surviving workload still needs it.

### Dev Namespace Is Missing Provider Secrets

Many `dev` namespace pods fail with missing provider secrets such as:

- `codex-api`
- `deepseek-api`
- `gemini-api`
- `anthropic-api`

This may be intentional if `dev` is dormant. Treat it as noise until the desired
state for `dev` is confirmed.

## Proposed Cleanup Order

### 1. Document Ownership And Desired State

- Confirm whether `kordinate` is the canonical private platform repo.
- Reclassify Charon responsibilities into scripts/skills/runbooks where
  practical.
- Reclassify Alfred responsibilities into configuration/profile documentation
  where practical.
- Confirm where operator notes should live before Google Drive is mounted.

### 2. Classify Platform Agents Before Repairing Them

- Mark each simple agent responsibility as `absorb into skill` or `retire`.
- Keep Augur separate because it is complex and already has a repo boundary.
- Preserve only the auto-containerization and deterministic/semantic split as a
  possible future reusable pattern.
- Do not spend time repairing missing PVCs, image references, or provider
  secrets for agents that are likely to be retired.

### 3. Repair Registry Resolution For Surviving Workloads

- Inspect `agents/alfred/profile/config.yaml` and generated runtime projection.
- Regenerate platform overlays if `REGISTRY` placeholders are leaking into live
  workloads that still matter.
- Decide whether the registry service should move to HDD-backed storage.
- Only then define `platform-build-deploy`.

Recommended direction:

- Keep `kordinate` as the platform/ops source of truth.
- Keep the cluster registry as the image distribution point.
- Keep host Docker as the near-term build engine for speed and because the
  existing `lib/scripts/build-agent-images.sh` already expects Docker.
- Standardize builds through one script/skill rather than ad hoc Docker use.
- Add timestamped immutable tags and roll deployments to tags, while still
  pushing `latest` for bootstrap compatibility.
- Defer BuildKit/Kaniko until the registry path and storage location are clean.
  BuildKit is a likely future improvement; Kaniko may be slower and should not
  be introduced as the default until measured.

### 4. Stabilize Shared Storage

- Inspect Longhorn replica count, degraded volume causes, and node scheduling.
- Decide whether disabled/offline nodes should be removed from Longhorn
  scheduling or repaired.
- Decide which data should move to `/mnt/hdd`.
- Create a migration plan for registry and MinIO before moving data.

Recommended direction:

- Use `/mnt/hdd` for cold/bulky host-level data first: corpus repo cache,
  rclone cache/logs, registry backing data, MinIO bulk data, and build caches
  where latency is acceptable.
- Keep latency-sensitive active database/runtime volumes on Longhorn/root-backed
  storage unless a specific workload proves it can tolerate HDD latency.
- Treat registry and MinIO differently:
  - Registry: moving to HDD is likely acceptable because image pulls/build pushes
    are recurring but not latency-critical. The cost is slower pushes/pulls.
  - MinIO: moving to HDD is acceptable for archive/object data, but not for
    latency-sensitive app state.
- Avoid moving Longhorn's whole data path to HDD as a first step. That would
  affect all PVCs and make performance/failure behavior harder to reason about.

Initial target layout on the host, if approved:

```text
/mnt/hdd/kord-storage/
  registry/
  minio/
  corpus/
  rclone/
  build-cache/
```

### 5. Make Corpus Read-Only By Design

- Define a corpus root, likely on HDD or a dedicated RWX PVC.
- Separate source repo cache from materialized test worktrees.
- Add a CLI that returns manifests/paths instead of encouraging direct edits.
- Enforce read-only mounts for consumers where possible.

### 6. Add Knowledge Landing Zone

- Do not finalize the Obsidian layout yet.
- After Google Drive is mounted, create only a minimal `Knowledge/` landing
  structure.
- Review Notion content before choosing permanent folders.

## Feedback Needed Before Mutating Live State

- Confirm the platform source of truth remains `kordinate`.
- Confirm `dev` should be treated as dormant/noise for now.
- Decide which platform agents survive as live workloads after the skills-first
  pivot.
- Decide whether any surviving workload still needs `/kord/shared`; if not, stop
  designing around a namespace-local `kord` PVC.
- Approve or reject `/mnt/hdd/kord-storage/` as the host root for cold/bulky
  services.
- Approve host Docker as the near-term build engine while we standardize the
  build/deploy process around Kordinate scripts/skills.
