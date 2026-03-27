---
description: Scan specified files for hardcoded secrets before commit
requester: any
mode: stateless
skill: scan-breaches
curated: true
scope: global
---

## Provider Guidelines

Scan the specified files/paths for hardcoded secrets, PII, and credentials.
Return clean/dirty with specific findings.
This is lighter than a full repo scan — targeted at files about to be committed.
