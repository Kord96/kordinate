---
name: audit
description: Audit a skill, agent, or shared system using a target-local audit.md contract. Use for structural checks, semantic review, E2E verification, benchmark analysis, or audit loops with optional safe fixes.
argument-hint: "<target> [--mode structural|semantic|runtime|benchmark|loop] [--fix]"
---

Audit a target using one shared process and one local audit contract.

The shared skill owns the mode contracts. The target owns its specific audit scope in `audit.md` or `audit/index.md`.

## Target Contract

Resolve the audit target first.

- skill target:
  - `agents/<agent>/skills/<skill>/audit/index.md`
  - `agents/<agent>/skills/<skill>/audit.md`
  - `shared/skills/<skill>/audit/index.md`
  - `shared/skills/<skill>/audit.md`
- agent target:
  - `agents/<agent>/audit/index.md`
  - `agents/<agent>/audit.md`
- shared system target:
  - `shared/<system>/audit/index.md`
  - `shared/<system>/audit.md`

If no local audit contract exists for the target, fail clearly instead of guessing.

## Modes

| Mode | Purpose | Mutability | Typical Output |
|------|---------|------------|----------------|
| `structural` | deterministic checks, inventory, schema, path, generated artifacts, cacheability, drift | read-only by default, `--fix` allowed for safe mechanical fixes | findings report, fix list |
| `semantic` | meaning quality, metadata quality, interpretation mismatch, reflection-informed review | read-only | semantic findings, recommended changes by layer |
| `runtime` | verify live execution contract, output artifacts, telemetry, caching, reflections | read-only by default | pass/fail checklist, operational blockers |
| `benchmark` | compare runs across repos, models, bundles, or time | read-only on product code | benchmark summary, deltas, trend findings |
| `loop` | orchestrate structural + semantic + runtime/benchmark + edits + reruns | mutating | changed files, rerun summary, improvement report |

Default mode is `structural`.

## Procedure

1. Resolve the target and load its `audit.md`.
2. Read only the references named by that `audit.md`.
3. Apply the requested mode contract:
   - `structural`: deterministic checks first
   - `semantic`: review meaning and interpretation quality
   - `runtime`: verify live system behavior against the checklist
   - `benchmark`: compare recorded runs or execute the benchmark slice
   - `loop`: run structural first, semantic second, then decide and apply the smallest useful changes
4. Report findings grouped by layer and severity.
5. If `--fix` is set in `structural`, only apply safe mechanical fixes.

## Rules

- Do not confuse audit with target ownership. `audit.md` defines what to inspect, not who owns implementation.
- Keep structural findings separate from semantic findings.
- `--fix` is only for narrow mechanical repairs in `structural`.
- `loop` must say what changed, what was rerun, and what improved or regressed.
- Prefer target-local scripts and checklists over ad hoc process invention.
- Keep target-specific domain references out of the shared skill where possible. Put them in the target's own `audit.md` and supporting files.
