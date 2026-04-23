# Augur Detector Audit Notes

Current findings from inspecting the analyze bundles, bundle generators, detector source, and detector runners.

## High-Value Findings

### 1. Holistic bundle size is intentional, but selective still needs discipline

`build_memory_bundles.py` inlines the same large shared sections into both selective and holistic memory bundles:

- workflow
- app contract
- abstractions
- anti-pattern index
- concept index

Then `build_runtime_bundles.py` embeds the entire generated memory bundle again inside the runtime bundle.

This is not automatically a bug. Holistic is meant to be enormous so large-context models can preload broad semantics before analysis.

The real question is whether:

- holistic materially helps large-context models
- selective stays lean enough for constrained models
- shared sections inside selective are still carrying more prompt mass than necessary

### 2. Fact detectors are mostly policy plus prose signatures

The fact detector layer under `detectors/facts/` has useful domain segmentation, but the current source is still thin:

- `policy.yaml` exists for all main fact domains
- `signatures.yaml` exists for all main fact domains
- there are currently no checked-in `ast-grep.yaml` or `semgrep.yaml` files for the fact domains

That means the system is still relying heavily on broad textual heuristics and downstream interpretation.

### 3. Concept detector rules now live in the detector tree

Executable concept rules have been moved from `memory/concepts/` into `detectors/concepts/`.

Current detector-side coverage after migration:

- `175` concepts with `ast-grep.yaml`
- `8` concepts with `semgrep.yaml`
- only a small subset still has concept-side `meta.yaml` and `signatures.yaml`

This is a much better source layout for runtime execution, but it also means the next detector task is policy quality, not just file placement.

### 4. The concept runner was partially broken

The AST runner had three practical issues:

- it imported `concept_decision` from a non-existent file
- it defaulted to detector source under `~/.kord/...` rather than the workspace repo
- it assumed the binary name `ast-grep`, but this machine exposes `sg`

Those issues are now fixed locally so the runner can load detector-side concept rules from the workspace repo.

### 5. Concept inference is still a heuristic bridge

`infer_concepts_from_facts.py` is pragmatic and useful, but it is still a lightweight bridge rather than a mature concept decision system. It infers concepts from facts using simple mappings and a small number of heuristics.

That is enough to bootstrap evaluation, but not enough to treat detector performance as mature.

## Immediate Priorities

### Priority 1: improve fact extraction before adding many more semantic concepts

The highest-leverage work is still likely in fact quality, not concept taxonomy.

The concept AST rule migration means runtime concept coverage is no longer the main structural blocker. The remaining gaps are:

- fact-domain AST coverage
- policy/signature quality for detector-side concepts
- better concept decision logic than simple default strengths

Recommended first AST targets:

- `routes`
  - route decorators
  - route registration calls
  - file-based handlers
  - RPC or websocket bindings
- `models`
  - ORM models
  - schema declarations
  - migrations
  - repository-backed entities
- `external-clients`
  - outbound HTTP client construction
  - SDK client initialization
  - timeout and retry configuration
- `middleware`
  - request/response hooks
  - guard or interceptor registration
  - auth and validation wrappers
- `auth-surface`
  - route guards
  - auth dependencies
  - token or session validation boundaries

### Priority 2: add stronger negative signals

Several fact and concept domains need stronger negative evidence, especially:

- `routes`
  - unrelated path literals
- `events`
  - local callbacks that never cross a boundary
- `models`
  - DTOs and transient structs
- `external-clients`
  - local helpers with no remote target
- `hexagonal`
  - domain code importing infrastructure directly
- `outbox`
  - direct publish inside request handlers with no durable staging

### Priority 3: preserve holistic breadth while keeping selective lean

The selective and holistic bundle split should stay. Holistic should remain large. The main design pressure is on selective and on the operating policy that chooses which bundle to preload for which model tier.

Likely improvements:

- keep selective focused on summaries plus targeted read rules
- make sure selective does not carry unnecessary semantic bulk
- keep holistic focused on full semantics for large-context models
- benchmark bundle choice as model-tier policy rather than forcing every model through every preload mode

### Priority 4: connect evaluation failures directly to detector edits

Benchmark failures should produce concrete detector follow-up:

- missing route family -> route AST rule or grep signal
- invented component -> stronger negative signal or component synthesis guard
- missed external dependency -> client construction rule
- invented concept -> absent-label false positive review plus negative signal

### Priority 5: treat facts as strong evidence, not the sole concept decider

Concepts should be finalized by combining:

- detector evidence
- normalized facts
- LLM semantic repo understanding

The concept decision model is documented in:

- `agents/augur/docs/notes/concept-decision-design.md`

That document defines:

- which concepts can auto-confirm
- which concepts require semantic review
- the final concept verdict schema
- the role of fact-derived concept suggestions

## Recommended Next Step

Use `agents/augur/docs/notes/detector-audit-prompt.md` with Gemini and DeepSeek, giving them the bundle generators, generated bundles, detector source, and analyze scripts.

The goal should be:

- identify which bundle content should shrink
- identify which fact domains deserve AST rules first
- identify which signatures are too weak or too broad
- identify pipeline issues that should be fixed before detector expansion
