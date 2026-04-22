# Augur Base API Contract

This document defines the read-only interface Augur should expose for canonical
analysis artifacts.

It exists to separate:

- **Augur-owned data**
  - immutable base analyses
  - reflections
  - validation and canonical analysis metadata
- **Docs-owned data**
  - overlays
  - published/current view selection
  - website-facing merged projection

The intent is to avoid coupling downstream consumers directly to Augur's
filesystem layout while still letting Augur remain the source of truth for the
base analysis.

## Ownership Split

### Augur owns

- `atlas.json`
- `stories/*.yaml`
- `narratives.yaml`
- `meta.json`
- `log.json`
- `reflections/`
- immutable analysis snapshots
- convenience pointers such as `analysis/latest.json`

### Docs owns

- `overlays/`
- overlay metadata and user edits
- published/current pointers for docs presentation
- merged website-facing views

## Deployment Model

The shared daemon runtime should be generic at the platform level, but each
agent may expose its own namespace and contract.

For Augur, the recommended shape is:

- shared daemon or gateway core
  - auth
  - routing
  - health
  - capability discovery
  - common error envelope
- Augur namespace
  - read-only analysis retrieval API

This implies:

- **do not** make docs read Augur memory paths directly
- **do not** make Augur own docs overlays
- **do** let docs fetch Augur base snapshots through an API

## Namespace

Recommended namespace:

```text
/augur
```

All routes below are read-only.

## Endpoint Set

### `GET /augur/projects`

Lists projects that have canonical accepted analyses available.

Response:

```json
{
  "projects": [
    {
      "project": "Kord96--logbd",
      "title": "Kord96--logbd",
      "latest_analysis_id": "2026-04-18T16-24-54Z",
      "latest_commit_sha": "d6a89b5e2b69be6fe66daf7aae1ec4ea44857683",
      "purpose": "Analyze message traffic into graph snapshots, serve queries, and classify spam risk."
    }
  ]
}
```

### `GET /augur/projects/:project/analyses`

Lists accepted analyses for one project.

Response:

```json
{
  "project": "Kord96--logbd",
  "analyses": [
    {
      "analysis_id": "2026-04-18T16-24-54Z",
      "commit_sha": "d6a89b5e2b69be6fe66daf7aae1ec4ea44857683",
      "analyzed_at": "2026-04-18T16:24:54Z",
      "validation_passed": true,
      "status": "accepted"
    }
  ]
}
```

### `GET /augur/projects/:project/analyses/:analysisId`

Returns summary metadata for one accepted analysis.

Response:

```json
{
  "project": "Kord96--logbd",
  "analysis_id": "2026-04-18T16-24-54Z",
  "meta": {},
  "artifacts": {
    "atlas": true,
    "stories": true,
    "narratives": true,
    "log": true,
    "reflections": true
  }
}
```

### `GET /augur/projects/:project/analyses/:analysisId/base`

Returns the canonical semantic artifact set for one analysis snapshot.

Response:

```json
{
  "project": "Kord96--logbd",
  "analysis_id": "2026-04-18T16-24-54Z",
  "atlas": {},
  "stories": [],
  "narratives": [],
  "meta": {},
  "log": {}
}
```

Notes:

- `stories` should be returned as a list of parsed story documents, not as raw
  YAML blobs.
- `narratives` should be normalized to the list form expected by downstream
  consumers.
- `log` is optional for consumers, but useful for provenance and debug.

### `GET /augur/projects/:project/analyses/:analysisId/reflections`

Returns any reflections attached to the analysis.

Response:

```json
{
  "project": "Kord96--logbd",
  "analysis_id": "2026-04-18T16-24-54Z",
  "reflections": []
}
```

## Canonical Inclusion Rules

Only expose an analysis snapshot when all are true:

- the snapshot is inside the canonical project analysis root
- `meta.json` exists
- `atlas.json` exists
- `stories/` exists
- `narratives.yaml` exists
- `meta.validation.passed === true`
- the project pointer or listing logic treats it as accepted/currently valid

## Error Model

Use the daemon's common error envelope. At minimum:

```json
{
  "error": {
    "code": "not_found",
    "message": "analysis not found"
  }
}
```

Recommended codes:

- `unauthorized`
- `not_found`
- `invalid_request`
- `analysis_not_ready`
- `internal_error`

## Relationship To Docs

The docs backend should consume Augur base artifacts through this API and merge
its own overlays at read time.

Recommended docs flow:

1. fetch base from Augur:
   - `GET /augur/projects/:project/analyses/:analysisId/base`
2. load overlay from docs-owned store
3. merge into website-facing current or analysis view
4. serve via docs API

This keeps:

- Augur responsible for canonical analysis generation
- docs responsible for editorial customization and presentation

## Non-Goals

This API should **not**:

- serve docs overlays
- expose docs `current.json` or published pointers
- return website-specific merged views
- require consumers to know Augur filesystem paths

## Future Extensions

Possible later additions:

- `GET /augur/projects/:project/current-base`
- `GET /augur/projects/:project/analyses/:analysisId/files/:artifact`
- `GET /augur/projects/:project/analyses/:analysisId/provenance`
- `GET /augur/projects/:project/analyses/:analysisId/health`

These should remain analysis-oriented, not docs-oriented.
