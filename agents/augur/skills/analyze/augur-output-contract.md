# Augur Output Contract

What augur produces and what downstream consumers (scribe, improve loop) can depend on.

This document is the stable interface. Internal methodology may change; these outputs won't break without a version bump. For full schema details, see [schema.md](schema.md) (atlas), [story-schema.md](story-schema.md) (stories + journeys), and the new facts-first synthesis path described below.

## Output Layout

```
$MEM/
  facts/
    index.json        # normalized extraction manifest
    <domain>.json     # concrete extracted observations (routes, models, deps, ...)
  atlas.json            # structural inventory — complete, scoreable
  stories/
    <id>.yaml           # 8-15 stories, each a scoped architectural concern
  journeys/
    <id>.yaml           # at least one — teaching-order path through stories
```

`--detect-only` produces `facts/` and `atlas.json` (no stories or journeys).

To synthesize atlas scaffolding directly from facts, use:

```bash
python3 scripts/synthesize_atlas_from_facts.py <facts-dir> --project <name> --output <atlas.json>
```

That CLI is intentionally conservative. It derives `stack`, `api_surface`, `state`, `external_dependencies`, `module_graph`, and `domain_model` hints from extracted facts, but it does not replace concept detection or debt analysis.

---

## facts/

Normalized extraction output. JSON, version `"1"`. See [schemas/facts-schema.md](../../schemas/facts-schema.md).

Facts are the stable contract between deterministic extraction and semantic concept inference.

### Stable v1 domains

- `frameworks`
- `routes`
- `models`
- `external-clients`
- `import-graph`

### Optional v1 domains

- `middleware`
- `config`
- `hot-files`
- `jobs`
- `events`
- `auth-surface`

---

## atlas.json

Full structural inventory. JSON, version `"4"`. See [schema.md](schema.md) for the complete field-by-field schema.

**Top-level sections:** `version`, `generated`, `project`, `purpose`, `domain_model`, `stack`, `groups`, `actors`, `components`, `flows`, `state`, `events`, `external_dependencies`, `failure_modes`, `concepts`, `module_graph`, `api_surface`, `debt`, `metadata`.

### Constraints scribe can depend on

| Constraint | Value | Hard? |
|-----------|-------|-------|
| Top-level groups | 3-5 | Yes |
| Components | 5-10 (4-12 acceptable) | Guideline |
| Critical data flows | 2-4 | Guideline |
| Failure modes | covers every external dep + stateful component | Yes |
| Component IDs | kebab-case, unique | Yes |
| All cross-references | resolve to existing IDs | Yes |
| Omit empty sections | events, reverse_deps, api_surface when N/A | Yes |

### What changed from architecture.yaml v2

| Change | Old | New |
|--------|-----|-----|
| Format | YAML | JSON |
| Version | `"2"` | `"4"` |
| Grouping | `capabilities` | `groups` (structural-only) |
| Component group | via capabilities | `group` field on each component |
| Story link | N/A | `metadata.story_ids` |

---

## Story Tree

Stories form a tree mirroring the atlas group hierarchy. See [story-schema.md](story-schema.md) for the full schema.

### Tree structure

- **Root stories** (3-5, one per atlas group) — high-level view, `parent: null`
- **Child stories** (2-5 per root) — zoom into specific concerns, `parent: "<root-id>"`
- Max depth: 2. The root stories ARE the architecture overview.

### Building blocks

| Block | Purpose | Multiple? |
|-------|---------|----------|
| **summary** | Short paragraphs (depth-dependent length) | No (required) |
| **structures** | Nested components + typed edges | Yes |
| **flows** | Ordered steps, typed | Yes |
| **observations** | Evidence-backed findings | One list, multi-attached |
| **rationale** | Decisions, trade-offs, alternatives | Yes |

### Key properties

- **Stories nest** — `parent`/`children` fields form a tree. Primary navigation.
- **Types are freeform** — structures and flows have a `type` string
- **Multiple structures and flows per story**
- **Observations attach at three levels** — story-wide, on nodes, on flow steps
- **Cross-group references allowed** — child stories can reference nodes outside parent's group
- **Verbosity scales with depth** — root: 2 paragraphs max (~50-80 words), child: 3 paragraphs max (~80-120 words)

---

## Journeys

Thin cross-cutting paths through the story tree. Only created when a concern spans multiple root groups. See [story-schema.md](story-schema.md).

**Properties:**
- Just ordered lists of story IDs — no content of their own
- Pull from any level of the tree (root or child, any group)
- At least one journey required: `getting-started.yaml` — teaching-order path covering all groups, for someone new to the codebase
- Additional journeys for cross-cutting concerns (resilience review, security audit, etc.) as the codebase warrants
- Every story ID in a journey exists in `stories/`
- 3-8 stories per journey

---

## Evaluation Scores

Each story carries:
- **Groundedness** — % of claims traced to atlas findings + node IDs. Target: >= 0.85
- **Coverage** — % of critical atlas nodes in at least one story. Target: >= 0.80

---

## What Scribe Can Depend On

1. **facts/index.json always exists** after `/analyze`
2. **atlas.json always exists** after `/analyze`
3. **stories/ directory exists** (may be empty if `--detect-only`)
4. **journeys/ directory exists** with at least `getting-started.yaml` (empty if `--detect-only`)
5. **All IDs are kebab-case and unique** within their section
6. **All cross-references resolve** — node IDs in stories exist in atlas, story IDs in journeys exist in stories/
7. **3-5 groups** — hard constraint
8. **Bold refs in summaries match atlas node IDs**
9. **Observation evidence includes file paths** relative to project root
10. **Journeys are ordered** — render stories in the sequence given

## What May Change (Not Stable)

- Number of stories (depends on project)
- Number and types of journeys
- Structure/flow type strings (freeform, new types may appear)
- Observation fields (may add new ones)
- Detection methodology internals
- Exact fact domain count beyond the stable v1 set
- Evaluation score thresholds
- Additional atlas metadata fields
