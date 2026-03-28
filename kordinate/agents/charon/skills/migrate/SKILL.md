---
name: migrate
description: >
  Move a resource to a new location — workstation, PVC, or data.
  Specific procedures in resource docs.
argument-hint: "workstation | pvc <name> <namespace>"
curated: true
scope: global
---

Move a resource to a new location. The migration verb is generic — specific procedures live in resource docs.

## Usage

- `/migrate workstation` — move the workstation pod to a new node/image
- `/migrate pvc <name> <namespace>` — move a PVC to new storage class

## Workstation Migration

`/migrate workstation`

Full workstation migration lifecycle per [workstation.md](workstation.md): build new image, create new PVC, copy data, deploy new pod, verify, clean up old resources.

## PVC Migration

`/migrate pvc <name> <namespace>`

Upgrade a PVC to a new storage class (e.g., Longhorn RWX). Uses the upgrade-storage procedure from bootstrap: [../bootstrap/upgrade-storage.md](../bootstrap/upgrade-storage.md).

## Rules

- Authenticate before any operation: use `/authenticate`.
- Migration includes cleanup of old resources per [../shared/clean/clean.md](../shared/clean/clean.md).
- Always verify the new resource is healthy before cleaning up the old one.
