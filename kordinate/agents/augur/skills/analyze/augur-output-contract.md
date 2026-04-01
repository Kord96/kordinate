# Augur Output Contract

What augur produces and what downstream consumers (scribe, improve loop) can depend on.

This document is the stable interface. Internal methodology may change; these outputs won't break without a version bump. For full schema details, see [atlas-schema.md](atlas-schema.md) (atlas) and [story-schema.md](story-schema.md) (stories + journeys).

## Output Layout

```
<project>/.kord/agents/augur/memory/
  atlas.json            # structural inventory — complete, scoreable
  stories/
    <id>.yaml           # 8-15 stories, each a scoped architectural concern
  journeys/
    <id>.yaml           # at least one — teaching-order path through stories
```

`--detect-only` produces only `atlas.json` (no stories or journeys).

---

## atlas.json

Full structural inventory. JSON, version `"4"`. See [atlas-schema.md](atlas-schema.md) for the complete field-by-field schema.

**Top-level sections:** `version`, `generated`, `project`, `purpose`, `domain_model`, `stack`, `groups`, `actors`, `components`, `flows`, `state`, `events`, `external_dependencies`, `failure_modes`, `concepts`, `module_graph`, `observability`, `security`, `developer_experience`, `api_surface`, `debt`, `metadata`.

### Constraints scribe can depend on

| Constraint | Value | Hard? |
|-----------|-------|-------|
| Top-level groups | 3-5 | Yes |
| Components | 5-10 (4-12 acceptable) | Guideline |
| Flows (all types combined) | 2-6 | Guideline |
| Flow types | data, control, event, state, resource | Yes (enum) |
| Failure modes | covers every external dep + stateful component | Yes |
| Component IDs | kebab-case, unique | Yes |
| All cross-references | resolve to existing IDs | Yes |
| Omit empty sections | events, reverse_deps, api_surface, observability, security, developer_experience when N/A | Yes |

### What changed from v3

| Change | v3 | v4 |
|--------|-----|-----|
| Version | `"3"` | `"4"` |
| Flows | `data_flows` (single type) | `flows` with type discriminator |
| Flow step schema | data-only fields | Common base + type-specific fields |
| Domain model | entities + relationships | + `bounded_contexts` with ubiquitous language |
| State | inventory only | + `schema_evolution`, `concurrency` |
| Observability | detected as concepts | Dedicated section: logging, metrics, tracing, gaps |
| Security | auth field on endpoints | Dedicated section: authn, authz, secrets, threat surface |
| Developer experience | N/A | Testing, linting, documentation |
| Module graph | modules, deps, infra | + `ci_cd`, `iac` |

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
| **flows** | Ordered steps, typed by flow category | Yes |
| **observations** | Evidence-backed findings | One list, multi-attached |
| **rationale** | Decisions, trade-offs, alternatives | Yes |

### Key properties

- **Stories nest** — `parent`/`children` fields form a tree. Primary navigation.
- **Flow categories** — flows typed as data, control, event, state, or resource (matching atlas flow types)
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
- Additional journeys for cross-cutting concerns that emerged from the analysis — no default set
- Every story ID in a journey exists in `stories/`
- 3-8 stories per journey

---

## Evaluation Scores

Each story carries:
- **Groundedness** — % of claims traced to atlas findings + node IDs. Target: >= 0.85
- **Coverage** — % of critical atlas nodes in at least one story. Target: >= 0.80

---

## What Scribe Can Depend On

1. **atlas.json always exists** after `/analyze`
2. **stories/ directory exists** (may be empty if `--detect-only`)
3. **journeys/ directory exists** with at least `getting-started.yaml` (empty if `--detect-only`)
4. **All IDs are kebab-case and unique** within their section
5. **All cross-references resolve** — node IDs in stories exist in atlas, story IDs in journeys exist in stories/
6. **3-5 groups** — hard constraint
7. **Bold refs in summaries match atlas node IDs**
8. **Observation evidence includes file paths** relative to project root
9. **Journeys are ordered** — render stories in the sequence given
10. **Flow type is one of** data, control, event, state, resource
11. **Flow steps use type-appropriate fields** — data flows use `data`/`transform`, control flows use `condition`/`gate`, etc.
12. **`observability`, `security`, `developer_experience` sections** are present when the project has the relevant concerns (omitted only when truly N/A)

## What May Change (Not Stable)

- Number of stories (depends on project)
- Number and types of journeys
- Structure type strings (freeform, new types may appear)
- Observation fields (may add new ones)
- Detection methodology internals
- Evaluation score thresholds
- Additional atlas metadata fields
- New optional fields within `observability`, `security`, `developer_experience`
