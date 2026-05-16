# Platform Cleanup Plan

This plan tracks the cleanup needed before adding more shared storage, Google
Drive mounts, corpus automation, and note-capture tooling.

## Goals

- Make the platform's operational state discoverable from this repository.
- Simplify Kordinate into a skills-first operational repo instead of a
  long-running multi-agent platform.
- Separate workstation lifecycle from durable storage and build services.
- Use the HDD for cold or bulky data where latency is not critical.
- Keep corpus repositories read-only and separate from development checkouts.
- Standardize note capture before migrating Notion, Facebook, and web-clipped
  sources into a Drive-backed knowledge store.

## Non-Goals

- Do not move live PVC data without a migration plan and rollback path.
- Do not change workstation manifests casually; Charon marks workstation changes
  as blocked unless explicitly authorized.
- Do not replace the registry, MinIO, or Longhorn before inventory and backup
  expectations are documented.
- Do not lock in the final Obsidian/Drive layout before reviewing Notion.
- Do not invest in repairing simple platform agents if their responsibilities
  can be absorbed into Codex skills.

## Phase 1: Current-State Inventory

- [x] Document the initial observed Kubernetes, storage, and Tailscale state.
- [x] Add a read-only inventory script for repeatable snapshots.
- [ ] Run and commit a fresh inventory snapshot after deciding where generated
  reports should live.
- [ ] Compare live cluster state against Charon docs and generated overlays.
- [ ] Identify stale PVCs, released PVs, failed pods, broken image references,
  and obsolete manifests.
- [ ] Inventory host disk usage, Docker cache, registry size, MinIO size, Augur
  state size, workstation mounts, and repo caches.

## Phase 2: Storage Design

- [ ] Decide canonical host storage roots, including what belongs on `/mnt/hdd`.
- [ ] Decide whether registry data should remain `local-path`, move to
  Longhorn, or move to a host-path backed by `/mnt/hdd`.
- [ ] Decide whether MinIO data should remain `local-path`, move to Longhorn, or
  move to `/mnt/hdd`.
- [ ] Decide where rclone Google Drive mount/cache/config/logs should live.
- [ ] Decide whether corpus storage lives in a cluster PVC, a host path on
  `/mnt/hdd`, or both.
- [ ] Define backup/snapshot expectations for registry, MinIO, corpus, notes,
  and Google Drive config.

## Phase 3: Platform Simplification

- [ ] Classify each current platform agent as `absorb into skill`, `retire`, or
  `extract as project`.
- [ ] Preserve Augur as a separate complex repo/project.
- [ ] Preserve Augur's useful architectural pattern: deterministic containerized
  execution separated from semantic agent work.
- [ ] Treat `/kord/shared` as a legacy compatibility mount unless a remaining
  workload proves it still needs shared repo state.
- [ ] Decide which existing Kordinate manifests remain needed after agent
  responsibilities move into skills.

## Phase 4: Ops Commands And Skills

- [ ] Define a `platform-build-deploy` workflow for image build, tag, push,
  rollout, and verification.
- [ ] Define a corpus workflow for read-only source repo cache, SHA selection,
  materialized worktrees, project-defined selectors, and returned manifests.
- [ ] Define a minimal `knowledge-notes` workflow for markdown notes, temporary
  note TTL, long-term notes, archive rules, and an index.
- [ ] Add docs or skills for each workflow.
- [ ] Add validation commands for each workflow.

## Phase 5: Safe Cleanup

- [ ] Clean or archive released/stale PVs only after confirming they are unused.
- [ ] Fix unresolved `REGISTRY/...` image references through the platform
  overlay path only for workloads that survive the simplification.
- [ ] Fix pods that reference missing namespace-local PVCs only if those pods
  remain part of the target runtime.
- [ ] Scale down or remove retired platform agents through source-controlled
  manifests.
- [ ] Migrate registry data if needed.
- [ ] Migrate MinIO data if needed.
- [ ] Consolidate repo/corpus storage.
- [ ] Verify workloads after each change.

## Phase 6: Knowledge Import

- [ ] Mount or connect Google Drive.
- [ ] Create a minimal landing layout only:
  - `Knowledge/INDEX.md`
  - `Knowledge/inbox/`
  - `Knowledge/sources/notion-raw/`
  - `Knowledge/sources/facebook-raw/`
  - `Knowledge/working/`
  - `Knowledge/archive/`
- [ ] Read/export Notion current state.
- [ ] Categorize Notion content types.
- [ ] Import a small Notion sample.
- [ ] Draft permanent Drive/Obsidian-compatible layout from actual content.
- [ ] Migrate remaining Notion content.

## Phase 7: Capture Tools

- [ ] Define temporary vs long-term note schema.
- [ ] Build minimal note-writing CLI/API.
- [ ] Build Chrome extension capture flow.
- [ ] Build mobile capture flow.
- [ ] Add TTL/archive job for temporary notes.

## Immediate Design Biases

- Prefer the existing cluster registry path over ad hoc image movement.
- Prefer Kordinate-owned scripts and Codex skills over long-running simple
  platform agents.
- Prefer preserving Charon build/deploy knowledge as skills/runbooks rather than
  preserving Charon as a required platform actor.
- Prefer `rclone mount` for the initial Google Drive experience because the
  desired model is mount, edit, and push through Drive.
- Prefer a host-level rclone mount if multiple containers need the same mounted
  Drive path.
- Prefer read-only corpus cache plus separate materialized worktrees over
  editing cached source repositories.
- Prefer postponing final knowledge taxonomy until Notion is inventoried.
