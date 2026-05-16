# Platform Current State

Last manually observed: 2026-05-12.

Use `lib/scripts/inventory-platform.sh ottawa-server` to refresh the raw
read-only inventory.

## Host

- SSH target: `ottawa-server`
- Hostname: `kkord-OptiPlex-7090`
- OS: Ubuntu 24.04
- Kubernetes: k3s
- Container tools present: `docker`, `ctr`, `crictl`
- Tailscale host IP: `100.71.90.43`
- Tailscale DNS: `ottawa-server.tailc85f0f.ts.net`

Observed disks:

| Mount | Size | Used | Notes |
| --- | ---: | ---: | --- |
| `/` | 915Gi | 635Gi | Root disk, also backs current local-path registry and MinIO data. |
| `/mnt/hdd` | 916Gi | near empty | Candidate cold/bulk storage location. |

## Cluster

Nodes:

| Node | State | Notes |
| --- | --- | --- |
| `homeserver` | Ready control-plane | Active node on `ottawa-server`. |
| `kkord-latitude-5420` | Ready, SchedulingDisabled | Legacy/disabled worker. |
| `colima` | NotReady, SchedulingDisabled | Legacy/offline worker. |

Namespaces of interest:

| Namespace | Purpose |
| --- | --- |
| `master` | Workstation, docs, monitoring backend, shared Kord PVCs. |
| `kord` | Agent platform. |
| `dev` | Kafka and development platform workloads. |
| `augur` | Augur snapshot platform. |
| `gateway` | MinIO. |
| `registry` | Local image registry. |
| `longhorn-system` | Longhorn storage control plane. |

## Storage

Storage classes:

| StorageClass | Provisioner | Notes |
| --- | --- | --- |
| `longhorn` | `driver.longhorn.io` | Default, expandable, supports RWX through share-manager. |
| `local-path` | `rancher.io/local-path` | Default, node-local storage. |

Important PVCs:

| Namespace | PVC | Access | Size | Purpose |
| --- | --- | --- | ---: | --- |
| `master` | `kord` | RWX | 100Gi | Workstation `/kord`, shared Kordinate data. |
| `master` | `kord-repos` | RWX | 20Gi | Workstation `/repos`. |
| `master` | `workstation-home` | RWO | 20Gi | Workstation home. Currently not mounted by the live workstation manifest observed on 2026-05-12. |
| `kord` | `agent-runtime` | RWX | 20Gi | Agent platform runtime. |
| `dev` | `agent-runtime` | RWX | 20Gi | Dev agent runtime. |
| `augur` | `augur-state` | RWO | 20Gi | Augur queues, work dirs, outputs, semantic sessions. |
| `registry` | `registry-data` | RWO | 20Gi | Registry data, currently `local-path`. |
| `gateway` | `minio-data` | RWO | 10Gi | MinIO data, currently `local-path`. |

Observed Longhorn risk:

- Several volumes were `degraded` in the 2026-05-12 inventory.
- `master/kord` was observed `healthy`.
- Disabled/offline nodes likely affect replica health and scheduling.

## Workstation

Live `master/workstation` deployment:

- Containers: `cloudflared`, `caddy`, `workstation`
- Workstation image: `registry.kord:5000/workstation:latest`
- Mounts:
  - `master/kord` at `/kord`
  - `master/kord-repos` at `/repos`
  - host `/dev/net/tun` for Tailscale
- Does not currently mount `master/workstation-home` in the live manifest
  observed on 2026-05-12.

Charon rules mark workstation changes as sensitive and blocked unless
explicitly authorized.

## Registry

Live registry:

- Namespace: `registry`
- Deployment: `registry`
- Image: `registry:2`
- Service: NodePort `30500`
- PVC: `registry/registry-data`
- Storage class: `local-path`

Observed concerns:

- Registry storage is tied to the active node/root disk through `local-path`.
- Some live workloads still reference unresolved `REGISTRY/...` image names.
- Some workloads reference `localhost:30500/...`, which Charon docs say should
  not be hardcoded in platform manifests.

## MinIO

Live MinIO:

- Namespace: `gateway`
- Deployment: `minio`
- Image: `minio/minio:latest`
- PVC: `gateway/minio-data`
- Storage class: `local-path`

Observed concerns:

- Credentials were visible in the deployment environment in the observed live
  manifest. Charon docs expect MinIO credentials to be managed through secrets.
- MinIO storage is tied to the active node/root disk through `local-path`.

## Augur

Live Augur namespace:

- `augur-server`
- `augur-gateway`
- `augur-webhook`
- `augur-deterministic-worker`
- `augur-semantic-worker`

All observed Augur deployments mount `augur/augur-state` at `/kord/augur`.

Observed Augur paths:

- queue: `/kord/augur/queue`
- outputs: `/kord/augur/outputs`
- work dirs: `/kord/augur/work`
- semantic queue: `/kord/augur/semantic-queue`
- semantic sessions: `/kord/augur/semantic/sessions`

## Tailscale

Observed on `ottawa-server`:

- TUN enabled.
- Tailnet DNS suffix: `tailc85f0f.ts.net`
- Host IP: `100.71.90.43`
- Host advertises `172.20.0.0/16`.
- Actual k3s pod/service networks observed from routing and services are
  `10.42.0.0/16` and `10.43.0.0/16`.
- No `tailscale serve` config was active.

## Cleanup Candidates

- Confirm whether released PVs with `Retain` are still needed.
- Repair or document Longhorn degraded volume status.
- Decide whether registry and MinIO should move off `local-path`.
- Resolve `REGISTRY/...` placeholders in live platform workloads.
- Resolve pods failing due to missing namespace-local `kord` PVC.
- Decide whether `/mnt/hdd` should host cold storage, registry, MinIO, corpus,
  rclone cache, or all of these.
- Decide whether `master/workstation-home` remains useful if the workstation
  continues to use `/kord` as its primary writable home/workspace surface.

