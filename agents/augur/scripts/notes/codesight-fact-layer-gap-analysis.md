# Augur Fact Layer vs Codesight

Thorough comparison between Augur's current fact pipeline and the locally cloned Codesight reference at:

- `/tmp/augur-reference/codesight`

This document is not a product comparison. It is an extraction-method comparison intended to improve Augur's fact layer without collapsing Augur into Codesight's output model.

## Scope

Compared:

- Codesight scanner and detector orchestration
- Codesight AST extractors
- Augur fact extraction, concept bridge, and atlas synthesis path

Important local references:

- [fact_extractor_support.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/fact_extractor_support.py)
- [infer_concepts_from_facts.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/infer_concepts_from_facts.py)
- [synthesize_atlas_from_facts.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/synthesize_atlas_from_facts.py)
- [facts-schema.md](/kord/workstation/home/project/kordinate/agents/augur/schemas/facts-schema.md)

Codesight references examined:

- `/tmp/augur-reference/codesight/src/index.ts`
- `/tmp/augur-reference/codesight/src/scanner.ts`
- `/tmp/augur-reference/codesight/src/detectors/routes.ts`
- `/tmp/augur-reference/codesight/src/detectors/schema.ts`
- `/tmp/augur-reference/codesight/src/detectors/events.ts`
- `/tmp/augur-reference/codesight/src/detectors/middleware.ts`
- `/tmp/augur-reference/codesight/src/detectors/config.ts`
- `/tmp/augur-reference/codesight/src/detectors/graph.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-go.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-csharp.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-python.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-routes.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-schema.ts`
- `/tmp/augur-reference/codesight/src/ast/extract-components.ts`

## Bottom Line

Codesight is ahead in extraction discipline.

Augur is ahead in downstream ambition.

Codesight already has a better answer to:

- how to collect files cheaply
- how to dispatch detectors by framework/language
- how to use language-specific structured parsing where it matters
- how to keep detector modules narrow and composable

Augur already has a better answer to:

- how to normalize evidence into durable facts
- how to keep concept inference separate from raw detection
- how to support semantic review, contradiction handling, atlas synthesis, reflections, and evaluation

So the right move is:

- borrow Codesight's extraction methodology
- keep Augur's fact contract and downstream architecture

## The Core Architectural Difference

Codesight pipeline:

```text
collect files
-> detect project/framework/orm
-> run detector modules in parallel
-> enrich results
-> compile markdown/wiki/report
```

Augur pipeline:

```text
detectors
-> normalized facts
-> concepts
-> atlas
-> stories
```

This difference matters.

Codesight extracts directly into user-facing structures:

- routes
- schemas
- components
- libs
- config
- middleware
- graph
- events

Augur extracts into a stable intermediate representation:

- facts

That means Augur should copy Codesight's detector and extractor patterns, not its final output format.

## Where Codesight Is Stronger

### 1. Detector orchestration is explicit and centralized

Codesight runs explicit detector modules from a single orchestration file.

Good properties:

- easy to see what runs
- easy to disable detectors
- detector boundaries are clear
- project framework context decides which detectors fire

Augur currently has more extraction logic concentrated inside one large support file.

Consequence:

- detector behavior is harder to inspect and evolve
- non-web languages fall through more easily
- adding a new fact family still feels like editing one monolithic extractor

### 2. Structured parsers exist for the non-TS stacks that matter

Codesight's strongest practical advantage is not only TypeScript AST. It has focused structured extractors for:

- Go routes and GORM models
- C# ASP.NET routes and Entity Framework models
- Python routes and SQLAlchemy models
- framework-specific route extraction across many stacks

This is exactly where Augur currently underperforms on unseen repos.

Evidence from our 8-repo local run:

- `temporal`: almost only `models`
- `loki`: nearly blind
- `newpipe`: nearly blind
- `keepassxc`: nearly blind

The problem is not just weak rules. The problem is that non-Python/JS/TS stacks still do not get enough structured extraction attention.

### 3. Detector families are concrete and narrow

Codesight detector modules tend to correspond to one extractable thing:

- routes
- schema
- middleware
- graph
- config
- events

This keeps each module legible and improves precision.

Augur's fact layer is conceptually similar, but the implementation is more blended:

- some domains are AST-backed
- some are regex-heavy
- some architecture-relevant signals are missing entirely
- fact extraction and detector execution still overlap too much

### 4. File collection and framework detection are already multi-stack aware

Codesight's `scanner.ts` does four useful things well:

- collects files with a clear extension list
- applies a stable ignore policy
- infers monorepo structure
- aggregates workspace-level frameworks and ORMs

Augur's current file iteration is acceptable, but Codesight's project-detection layer is stronger and more systematic.

This matters because better framework context narrows detector choices and lowers false positives.

## Where Augur Is Stronger

### 1. Facts are first-class normalized evidence

Codesight returns useful structures, but Augur's fact schema is stronger as an analysis substrate.

Facts carry:

- detector provenance
- normalized raw evidence
- grounded source files
- contradictions
- relationships

That is the right substrate for:

- semantic review
- concept confirmation
- benchmark grading
- traceability

Codesight does not need this depth because it is not primarily doing architecture inference.

### 2. Concept and atlas layers are deliberately separate

Augur's design keeps these distinct:

- observed facts
- inferred concepts
- synthesized atlas

That is the right architecture for an architecture-analysis system.

Codesight is mostly optimized to produce compact context quickly. That is useful, but it is a shallower end state.

### 3. Evaluation and reflection are already part of the design

Augur has the beginnings of:

- benchmarked runs
- run manifests
- bundle-aware evaluation
- reflection artifacts
- semantic-review packets

Codesight has evaluation fixtures, but Augur is already set up to be improved as a system, not just run as a scanner.

## Specific Gaps Augur Should Close

### Gap 1. Too much extraction logic still lives in one file

Current state:

- [fact_extractor_support.py](/kord/workstation/home/project/kordinate/agents/augur/scripts/fact_extractor_support.py) owns a very large share of the behavior

Consequence:

- hard to reason about domain boundaries
- easy to add broad heuristics that affect everything
- harder to benchmark domain-level improvements independently

Recommendation:

- move toward Codesight-style domain modules
- keep one orchestrator, but split extractor logic by fact family and language

Target shape:

```text
agents/augur/scripts/facts/
  frameworks.py
  routes.py
  models.py
  middleware.py
  external_clients.py
  config.py
  import_graph.py
  jobs.py
  events.py
  registrations.py
  handlers.py
  dispatch_bindings.py
  boundaries.py
  languages/
    python.py
    typescript.py
    go.py
    java.py
    csharp.py
    kotlin.py
```

### Gap 2. Non-web stacks are still severely undercovered

This is the biggest practical gap.

We saw:

- Go repos missing handler/binding/registration facts
- C# desktop/plugin repos reduced to config/auth noise
- Java/Kotlin repos only lightly understood unless framework signals are obvious

Recommendation:

- copy Codesight's approach of focused non-TS extractors
- add structured family-level extractors for:
  - Go
  - C#
  - Java
  - Kotlin

Priority order:

1. Go
2. C#
3. Java
4. Kotlin

### Gap 3. Missing architectural fact families

Codesight is not explicitly solving all of these, but its route/event/schema extractors show the right style of implementation.

Augur needs these generic families:

- `registrations`
- `handlers`
- `dispatch-bindings`
- `boundaries`

These are the right abstraction level for unseen repos.

They should stay generic and reusable across frameworks.

Examples:

- registrations:
  - plugin registration
  - service registration
  - workflow/activity registration
- handlers:
  - command handlers
  - request handlers
  - RPC handlers
  - event consumers
- dispatch-bindings:
  - queue/topic bindings
  - bus dispatch
  - worker subscriptions
- boundaries:
  - interface/implementation contracts
  - repository/store/provider boundaries
  - adapter/service boundary clues

### Gap 4. Auth/config noise dominates because structural families are absent

Our 8-repo run showed repeated overproduction of:

- `rbac`
- `api-key-auth`
- `route-guard`
- `session-auth`
- `token-auth`

This is partly a precision issue, but mostly a balance issue.

When the system lacks stronger structural families, the cheaper auth/config heuristics dominate the concept layer.

Recommendation:

- do not start by endlessly refining auth heuristics
- first add stronger structural fact families
- then downweight or tighten auth/config patterns once the fact layer has better alternatives

### Gap 5. Fact extraction still skips too many file types

Until recently, Augur only gave real attention to:

- Python
- JS/TS
- Prisma
- SQL

Everything else was mostly incidental.

Codesight does better by explicitly handling more stacks, even if the extractor is regex/structured rather than full AST.

Recommendation:

- every important language should have at least a minimal structured extraction path
- "regex only" is acceptable if the signals are narrow and useful
- the real mistake is to leave a language with no structural path at all

## What Augur Should Copy Directly

### 1. Framework-gated detector selection

Codesight only runs many detectors once it knows the framework family.

Augur should do more of this.

Specifically:

- make framework facts drive detector applicability more aggressively
- avoid broad route/model/auth scans in stacks where they are not appropriate

### 2. Language-specific structured extraction

Codesight's Go and C# extractors are a useful pattern:

- not necessarily full compiler AST
- but more structured than naive regex
- focused on real constructs that define behavior

Augur should adopt the same discipline for fact families that matter most.

### 3. Narrow detector modules

Codesight's domain modules are easier to inspect and test.

Augur should mirror that by splitting the extractor into:

- family modules
- language adapters
- one orchestrator

### 4. Cheap structured enrichment before final output

Codesight does:

- detect raw routes
- enrich contracts
- compute grouped summaries

Augur should apply the same pattern at the fact layer:

- emit narrow facts
- add cheap inferred relationships
- then hand off to concept inference

## What Augur Should Not Copy

### 1. Output coupling

Codesight is optimized to emit human-facing context directly.

Augur should keep:

- facts as a stable substrate
- concepts as a separate stage
- atlas as a separate synthesis stage

### 2. Single-pass architectural interpretation

Codesight does not need semantic review or contradiction-heavy concept adjudication.

Augur does.

So we should not collapse back to:

- detector output -> final architecture summary

### 3. Over-indexing on markdown/wiki generation

That is a great product feature for Codesight.

For Augur, it is downstream. The bottleneck is still evidence quality.

## Direct Mapping

### Codesight detector/extractor -> Augur fact family

- `routes.ts` + `extract-routes.ts` + language route extractors
  - Augur:
    - `routes`
    - `handlers`
    - `registrations`

- `schema.ts` + language schema extractors
  - Augur:
    - `models`
    - `boundaries`

- `events.ts`
  - Augur:
    - `events`
    - `dispatch-bindings`
    - `registrations`

- `middleware.ts`
  - Augur:
    - `middleware`
    - auth-related route/middleware support facts

- `graph.ts`
  - Augur:
    - `import-graph`
    - `hot-files`
    - later component and boundary hints

- `config.ts`
  - Augur:
    - `config`
    - env/secret/service-url facts

### Codesight AST extractor -> Augur improvement target

- `extract-go.ts`
  - build Go-specific:
    - route facts
    - handler facts
    - registration facts
    - boundary facts

- `extract-csharp.ts`
  - build C#-specific:
    - route facts
    - handler facts
    - registration facts
    - boundary facts

- `extract-python.ts`
  - strengthen Python route/model parity and use it as a model for stricter fact emitters

- `extract-schema.ts`
  - useful pattern for keeping ORM/model extraction narrow and framework-aware

## Recommended Augur Refactor

### Phase 1. Reorganize the fact extractor

Goal:

- split domain logic from orchestration

Implementation:

- keep `build_facts_payload(...)` as the orchestrator entrypoint
- move family extraction into dedicated modules
- keep the fact schema unchanged

### Phase 2. Add structured non-web extractors

First implementations:

- Go:
  - workflow/activity registration
  - gRPC and handler registration
  - queue/topic bindings
  - interface/store boundaries
- C#:
  - plugin registration
  - controller/command handlers
  - DI/service registration
  - interface/implementation boundaries

### Phase 3. Tighten concept inference inputs

Once new fact families exist:

- infer `plugin`, `workflow-engine`, `event-driven`, `repository`, `dependency-injection` from stronger evidence
- stop letting auth/config dominate concept inference by volume alone

### Phase 4. Re-benchmark on the same 8 repos

Success criteria:

- `temporal` produces handler/registration/binding facts
- `wox` produces plugin/boundary/registration signals
- `loki` produces more than hot-files/import noise
- `newpipe` and `keepassxc` produce at least some structural boundaries or handlers
- more than one repo yields meaningful semantic-review candidates

## Priority Backlog

### P0

- split extractor logic by fact family
- add Go structured extraction
- add C# structured extraction
- add direct fact emitters for:
  - registrations
  - handlers
  - dispatch-bindings
  - boundaries

### P1

- improve framework-gated detector applicability
- reduce auth/config overfiring once structural families are live
- add Java/Kotlin structured extraction

### P2

- add component/service-role extraction as a separate fact family if needed
- make detector execution more directly fact-driven instead of large fallback heuristics

## Final Recommendation

Use Codesight as a reference implementation for:

- detector decomposition
- language-specific structured extraction
- framework-aware routing of extraction logic

Do not use it as the target architecture.

Augur should become:

- Codesight-level practical extraction quality
- plus Augur's fact normalization
- plus semantic concept review
- plus atlas synthesis and evaluation

That is the right long-term combination.

## Direct Comparison Results

After the initial study, I ran direct side-by-side comparisons on representative repos and then patched Augur's deterministic layer accordingly.

### Temporal

Codesight:

- `13` routes
- `44` models
- `7` gRPC routes

Augur before Go structured extraction:

- `0` routes
- `214` models
- `0` registrations
- `0` handlers
- `0` dispatch-bindings

Augur after Go structured extraction:

- `5` routes
- `247` models
- `496` registrations
- `599` handlers
- `75` dispatch-bindings
- `108` boundaries

Interpretation:

- Codesight was materially ahead on Go route and service/workflow-style structural extraction.
- Augur closed a meaningful part of that gap once `.go` files stopped flowing through the generic extractor.
- Augur is now richer than Codesight on workflow/registration-style facts, but still needs better filtering so route and RPC signals are not drowned by volume from jobs/config.

### Wox

Codesight:

- `4` websocket routes
- `0` models
- strong library/export inventory

Augur before Go structured extraction:

- `0` routes
- `0` models
- `128` handlers
- `295` boundaries

Augur after Go structured extraction and generic noise tightening:

- `2` routes
- `46` models
- `103` handlers
- `93` boundaries

Interpretation:

- The direct gain here was mostly noise reduction plus some real Go signal recovery.
- Augur still needs a better plugin/extensibility fact family for repos like Wox; neither the old generic layer nor the current Go path is enough on its own.

### Fineract

Codesight:

- `0` routes
- `0` models
- mostly middleware/import/config style signals

Augur after generic structural family tightening:

- `0` routes
- `2` models
- `4` registrations
- `1104` handlers
- `104` dispatch-bindings
- `1247` boundaries

Interpretation:

- Codesight is not obviously stronger on this Java monolith today.
- Augur is extracting more structure, but the remaining `handler` and `boundary` volume is still too high.
- The next major extraction target after this patch set should be Java/Kotlin-specific structure, not more generic regex growth.

### ShareX

Codesight:

- detected `aspnet`
- `0` routes
- `0` models
- large library/export inventory

Augur after C# structured extraction:

- `0` routes
- `0` models
- `5` handlers
- `463` boundaries

Interpretation:

- The new C# path works and is not regressing obvious ASP.NET cases, but ShareX is a desktop-heavy codebase and not a strong route/schema validation target.
- C# still needs better filtering of common framework interface implementations.

## What These Results Mean

The useful conclusion is not "match Codesight output field for field."

The useful conclusion is:

- Go needed language-aware routing immediately, and that was correct.
- C# needed a dedicated path, but route/model-heavy validation should use a more ASP.NET-web-oriented repo than ShareX.
- Java/Kotlin are now the biggest remaining structured-extraction gap.
- generic `handlers` and `boundaries` should be treated as fallback families, not the primary source of architecture truth.
