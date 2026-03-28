---
description: Cache review prompt — sent to provider when expiry is uncertain
curated: true
scope: global
---

You are reviewing whether your cached response is still valid.

## Changed Inputs

{{DIFF}}

## Cached Response

{{CACHED_DATA}}

## Decision

Based on the changes above, is your cached response still accurate and complete?

- If the changes are irrelevant to your cached response (e.g., comments, formatting, unrelated files), respond: `VALID`
- If the changes affect the accuracy of your cached response, respond: `STALE`

Respond with ONLY `VALID` or `STALE` on the first line, followed by a brief reason.
