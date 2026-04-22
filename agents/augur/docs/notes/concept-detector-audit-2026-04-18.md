# Concept Detector Audit 2026-04-18

Focused audit of the current Augur concept layer after strengthening `atlas.json.concepts`.

Scope:
- concept catalog and policy notes
- concept-evidence detectors
- fact-inference logic in `infer_concepts_from_facts.py`
- recent concept output from `matrixone`, `rustpbx`, `jPOS`, and `cnspec`

## Main Judgment

The concept section is worth keeping, but several atlas concepts are currently stronger as semantic annotations than as detector-backed facts.

Current problem:
- some concepts are backed by dedicated concept-evidence detectors and semantic questions
- others are mostly produced by broad fact inference from routes, jobs, handlers, or boundaries
- those broad inferences are good as *candidates* but too weak to be treated as high-confidence architectural concepts without stronger review discipline

So the concept layer is directionally correct, but still mixes:
- strong detector-backed concepts
- broad fact-inference candidates
- semantic interpretations that look more precise than the evidence really is

## What Looks Strong

### `repository`
Status: keep, but semantic-review only.

Why:
- dedicated detector assets exist:
  - `detectors/facts/concept-evidence/repository/meta.yaml`
  - `detectors/facts/concept-evidence/repository/ast-grep.yaml`
  - `detectors/facts/concept-evidence/repository/signatures.yaml`
- policy already says:
  - `auto_confirm.allowed: false`
  - `broad_match_requires_questions: true`
- semantic questions are good:
  - `repository-domain-facing-interface`
  - `repository-storage-separation`
- the catalog entry is strong and explicitly warns against treating any DB wrapper as a repository pattern.

Judgment:
- this is one of the better-designed concepts in the system
- keep it as a semantic-review concept
- do not auto-confirm from boundary naming or ORM usage alone

### `rest`
Status: keep, but semantic-review only.

Why:
- dedicated detector assets exist:
  - `detectors/facts/concept-evidence/rest/meta.yaml`
  - `detectors/facts/concept-evidence/rest/ast-grep.yaml`
  - `detectors/facts/concept-evidence/rest/signatures.yaml`
- the meta already encodes the right caution:
  - resource-oriented surface
  - method/status semantics
  - broad match requires questions
- the catalog distinction is useful because many repos are really RPC-over-HTTP, not REST.

Judgment:
- good concept to keep
- current deterministic inference from route style alone is too eager
- final atlas use should stay candidate-only until semantic questions are answered

### `workflow-engine`
Status: promising, but currently over-broad in inference.

Why:
- dedicated concept-evidence AST rules exist for concrete workflow frameworks:
  - Airflow
  - Temporal
  - Step Functions
- catalog entry is useful and clearly disambiguates from `state-machine`

Problem:
- `infer_concepts_from_facts.py` also infers `workflow-engine` from a broad mix of:
  - workflow registration
  - workflow handlers
  - queue/topic bindings
- on `cnspec`, that produced a high-confidence candidate from a very broad set of handlers.

Judgment:
- keep it
- but do not let broad handler/binding accumulation produce a strong architectural claim by itself
- prefer framework-backed or explicit orchestration evidence first
- otherwise keep as semantic-review candidate with lower confidence

## What Looks Weak Or Too Broad

### `event-driven`
Status: keep as a broad candidate, but do not treat as a strong differentiator yet.

Why weak:
- no dedicated concept-evidence directory for `event-driven`
- current inference is simply:
  - if `event` facts exist, emit `event-driven`
- that is too broad; many systems emit events without event-driven architecture being a defining architectural concern.

Judgment:
- useful as a hint
- weak as a final architectural concept unless paired with stronger evidence such as queue/topic boundaries, event contracts, or pub-sub topology

Recommendation:
- add a dedicated `concept-evidence/event-driven/` package or keep it explicitly low-confidence candidate-only

### `scheduler`
Status: too broad in current form.

Evidence state:
- there is a small AST detector package for concrete scheduler libraries
- but the common inference path is just:
  - if job facts exist, emit `scheduler`

Problem:
- many repos have timers, loops, or background jobs
- that does not always mean scheduling is an architectural concept worth surfacing in the atlas

Judgment:
- currently over-emitted
- should usually remain low or medium confidence unless there is an explicit scheduling subsystem, cadence policy, or leader-elected scheduled execution

### `service-manager`
Status: useful concept, weak detector coverage.

Evidence state:
- concept catalog entry exists and is reasonable
- detector side is only a few AST patterns around signal handling and graceful shutdown in Python/TypeScript
- no richer signatures or semantic questions were found

Problem:
- current real usage, such as `matrixone`, comes from semantic judgment, not strong detector support
- signal handling alone is not enough to establish a real service-manager architecture pattern

Judgment:
- keep in catalog
- but do not pretend it is detector-backed yet
- needs stronger concept-evidence support or should remain mainly semantic/manual

### `state-machine`
Status: concept is good, detector coverage is too weak.

Evidence state:
- catalog entry is strong and disambiguates from `workflow-engine`
- current AST evidence is very weak:
  - Python enum class
  - `transitions = { ... }`
- that is not enough for a cross-language architectural concept

Judgment:
- keep the concept
- detector coverage is currently far below what the atlas presentation implies
- should remain semantic-review only until stronger transition/guard detection exists

### `command-dispatch`
Status: probably useful, but not a first-class concept-evidence concept yet.

Evidence state:
- appears in structural fact extraction rules
- does not currently have a concept-evidence detector package like `repository` or `rest`
- `rustpbx` concept usage looked reasonable, but the system support is asymmetric

Judgment:
- this is better treated as a structural or control-flow pattern for now
- if we want it as a first-class atlas concept, give it the same treatment as `repository`:
  - catalog semantics
  - concept-evidence rules
  - review questions

## Repo Observations

### `matrixone`
- `service-manager` and `state-machine` were plausible semantic readings.
- But both concepts currently rely more on semantic interpretation than strong detector evidence.
- That makes the final atlas concepts believable but not strongly auditable.

### `rustpbx`
- `plugin-system` and `command-dispatch` were among the most useful concept annotations.
- `rest` was much weaker and more generic.
- `split-command-path` looked useful as an anti-pattern, but now needs repo-specific explanation fields.

### `jPOS`
- `message-queue` was strong and repo-shaping.
- `repository` looked weak and correctly ambiguous; the atlas note already admits it is not a classic repository-heavy system.
- `scheduler` looked broad rather than central.

### `cnspec`
- `repository` was plausible because of the datalake and scandb abstraction layer.
- `workflow-engine` and `event-driven` were much more debatable because they were largely inferred from handlers, execution graph pieces, and queue-like structures.
- This repo shows why broad fact inference must not look like final confirmation.

## Recommended Classification

### Keep And Strengthen
- `repository`
- `rest`
- `workflow-engine`
- `plugin`

### Keep But Candidate-Only Unless Stronger Evidence
- `event-driven`
- `scheduler`
- `service-manager`
- `state-machine`

### Do Not Promote To First-Class Concept Yet
- `command-dispatch`
  - keep as structural/control-flow signal until it gets full concept treatment

## Recommended Changes

1. Tighten atlas concept presentation policy.
- detector-backed concepts and semantic-review concepts should look different in the underlying evidence
- do not let broad fact inference masquerade as a strong architectural concept

2. Reduce confidence inflation in `infer_concepts_from_facts.py`.
- `event-driven`, `scheduler`, and broad `workflow-engine` inference should probably default lower
- require stronger paired evidence before raising confidence

3. Add explicit concept provenance fields later.
- at minimum distinguish:
  - `detector_backing: strong | partial | weak`
  - `decision_mode: fact-inference | semantic-review | auto-confirm`
- this is more honest than a single confidence label

4. Add richer detector packages only for high-value concepts.
Priority order:
- `event-driven`
- `service-manager`
- `state-machine`
- maybe `command-dispatch` if it remains useful across repos

5. Keep semantic review mandatory for architecture-level concepts.
- the external audit direction remains correct
- detector evidence should nominate
- facts should constrain
- semantic review should decide the architecture-level call

## Bottom Line

The concept section is promising, but right now its strongest concepts are:
- the ones with dedicated detector semantics and review questions
- plus a few good semantic/manual judgments

Its weakest concepts are the ones currently inferred from broad structural facts and then presented as if they were equally strong.

So the next improvement should not be "more concepts".
It should be:
- fewer but better concepts
- clearer separation between candidate inference and strong confirmation
- stronger detector support only for concepts that repeatedly prove architectural value
