# Concept Detection

Level 3 resource for the architect skill. Referenced from step 2 (detect concepts). Carries the full detection procedure from the concept catalog.

## Catalog

The ontology and index layer lives under `memory/indexes/`. Use the indexes there as the stable navigational layer for categories and entry counts — use those numbers in the report, do not hardcode them.

Individual concept semantics live in `memory/catalog/concepts/<name>/concept.md` and framework semantics live in `memory/catalog/frameworks/<name>/framework.md`. Read these on demand in selective mode rather than loading every entry up front. Concepts remain the semantic layer; deterministic detection assets live separately under `detectors/`.

## Stack Detection and Category Prioritization

Before scanning, identify the project's languages and frameworks (already detected in step 1) to prioritize relevant categories:

- Python: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`; framework imports (`flask`, `fastapi`, `django`, `celery`, `sqlalchemy`, `httpx`, `requests`)
- TypeScript/JS: `package.json`, `tsconfig.json`; `express`, `nestjs`, `next`, `react`
- Go: `go.mod`; `net/http`, `grpc`, `gin`, `echo`
- Java: `pom.xml`, `build.gradle`; `spring`, `quarkus`
- Kubernetes: `kustomization.yaml`, `helm/`, Dockerfiles

Estimate project size by globbing source files (`**/*.py`, `**/*.ts`, etc.). Rank categories by relevance to the detected stack. Always scan: resilience, error-handling, security, structural, storage/data. Add stack-specific categories (concurrency for async Python, frontend for React, messaging for Kafka consumers). For projects over 500 files, limit the initial scan to the 5-8 most relevant categories and expand only if time permits.

## Pass 1 — Broad Grep (Candidate List)

Work category by category through the prioritized list. For each entry in a category, derive grep keywords from its index table row: use the `Description` column (patterns index) or `What to look for` column (anti-patterns index) to extract framework imports (`from pybreaker`, `import opossum`), directory names (`ports/`, `adapters/`), config files (`circuit_breaker.yml`), and class/function names. A hit on any keyword adds that entry to the candidate list. Skip entries with zero hits — do not read their full `concept.md`.

**Batch by category:** Build one multi-pattern regex per category (e.g., `pybreaker|opossum|CircuitBreaker|resilience4j` for Resilience) instead of grepping entry-by-entry. This keeps the number of grep invocations to one per category (~24 for patterns, ~21 for anti-patterns) rather than one per entry (~216 total).

## Pass 2 — Tool Rules (ast-grep / semgrep)

Use tool rules to gather structured evidence, not to force binary detection. Prefer concept-level detector policy from `detectors/concepts/<name>/policy.yaml` when present.

### Detector strength

Treat the 1-5 scale as policy weight for the detector, not as a prose note about whether AST is a good fit:

- **5** — highly trustworthy and specific; may be eligible for auto-confirm
- **4** — strong evidence source, but may still need light verification
- **3** — useful but requires corroboration
- **2** — weak clue only
- **1** — never decisive on its own

`detector_strength` belongs to concept metadata. `match_confidence` is run-level and comes from the evidence emitted by the detector.

Architecture-level and semantics-heavy concepts should still prefer semantic questions whenever the structural match is broad or ambiguous.

### Rule files

For each candidate, check the deterministic detector assets under `detectors/concepts/<name>/`.

Typical files:

- `detectors/concepts/<name>/ast-grep.yaml`
- `detectors/concepts/<name>/semgrep.yaml`
- `detectors/concepts/<name>/policy.yaml`
- `detectors/concepts/<name>/signatures.yaml`

Most entries will only have a subset. Check file existence before running. A rule file may contain multiple YAML documents for different languages or variants.

Run the available rule against the project:
- `ast-grep scan --rule <rule-path> <project-dir>`
- `semgrep --config <rule-path> <project-dir> --json`

Augur's end-to-end concept detection driver is `skills/analyze/scripts/run_concept_detection.py`. It orchestrates:
- `skills/analyze/scripts/run_ast_grep.py`
- `skills/analyze/scripts/run_semgrep.py`
- diagnostic-question result synthesis
- deterministic concept decision synthesis

The lower-level runners should still emit `augur-evidence-record/v1` records.

### Evidence-first interpretation

Do not treat rule output as the final concept decision. Each rule run should be interpreted as an evidence record containing at least:

- detector type
- detector strength
- match confidence
- specificity (`exact`, `narrow`, `broad`)
- grounding locations
- contradiction notes, if any
- a local verdict: `confirmed`, `candidate`, `inconclusive`, or `contradicted`

A precise high-strength match with no contradiction can confirm a concept directly. A broad or noisy match should usually produce a `candidate` and trigger semantic questions.

### Core policy

- high-strength, high-confidence, low-noise structural evidence → usually `confirmed`
- medium or broad structural evidence → ask semantic questions first
- no match, missing tool, or rule failure → treat as neutral and continue
- if multiple concepts explain the same broad match, keep them as `candidate` until questions or signatures resolve them

For `semgrep`, parse JSON output for file paths and line numbers. Rule runners should emit `augur-evidence-record/v1` records, and only confidently confirmed concepts should leave the Pass 3 worklist.

### Quality bar

Prefer tool rules that are:
- high precision — most matches are true positives
- acceptable recall — they catch canonical implementations
- general enough for common coding styles
- low noise on large codebases

If a rule does not meet that bar in practice, downgrade it to supporting evidence rather than letting it decide detection on its own.

### Error fallback

If `ast-grep` or `semgrep` is unavailable, or a rule crashes, continue with grep and manual signature verification. Record the limitation in scan metadata rather than blocking the analysis.

## Pass 3 — Manual Signature Verification

For each candidate still unconfirmed after Pass 2 (no rule file exists, or the tool produced no matches), read its `## Recognition > ### Signatures` section from `concept.md` and verify with targeted Grep/Glob: specific imports, class names, directory layouts, config keys, naming conventions, or structural smells listed in the signatures.

## Pass 3.5 — Diagnostic Question Evaluation

For candidates still unconfirmed after Pass 3 (signature verification was inconclusive or contradictory), load structured detector metadata from `detectors/concepts/<name>/`. During migration, legacy `memory/catalog/concepts/<name>/meta.yaml` may still exist as a mixed metadata source.

When either source provides diagnostic questions, evaluate them like this. Until semantic evaluation is implemented, unanswered questions must stay neutral in the emitted `augur-question-result/v1` record rather than counting as yes or no. Feed those records into `agents/augur/scripts/concept_decision.py` alongside rule evidence:

- For questions with `signals` hints, grep for those signals first. If all signals return zero results, answer "no" without further analysis.
- For remaining questions, read relevant code and answer yes/no with a one-line justification.
- Compute the weighted score (sum of weights for "yes" answers).
- If score >= `threshold`, mark as detected. Derive confidence from score/max_score ratio: >= 80% = high, >= threshold = medium.

`detectors/concepts/<name>/policy.yaml` should be treated as the canonical structured detector source. Legacy `meta.yaml` may still exist during migration for fallback analysis guidance, but it is no longer the long-term detector authority. Keep `ast-grep.yaml` and `semgrep.yaml` as separate support artifacts, and route structured detector loading through the detector layer so `/analyze` and `/design` converge on one deterministic path.

Batch all questions for one concept into a single analysis pass — do not make separate passes per question. This pass typically adds 2-5 minutes for 10-30 candidate concepts.

## Confidence Assessment

After confirming a candidate in Pass 2, 3, or 3.5, synthesize concept-level verdicts through the deterministic decision layer (`agents/augur/scripts/concept_decision.py`). Then read the concept's `## Recognition > ### Confidence` section to refine the final human-facing confidence narrative. Combine that narrative with the evidence record verdict (`confirmed`, `candidate`, `inconclusive`, `contradicted`) rather than relying on scores alone. If the entry lacks a `### Confidence` section, apply the default rubric:

- **high** — unambiguous: library import, framework config, or tool rule match with no false-positive risk.
  Example: `from pybreaker import CircuitBreaker` in `client.py` — direct library usage, high.
- **medium** — partial: structural indicators present (directory layout, naming) but implementation deviates from canonical form.
  Example: `src/ports/` and `src/adapters/` exist but two modules import adapters directly — medium.
- **low** — traces only: a single keyword hit or a hand-rolled implementation without standard libraries or naming.
  Example: a `for i in range(3)` retry loop with no backoff and no library — low.

Record for each: name, category (from catalog), confidence level, file locations, one-sentence evidence note.

**Domain models** (concepts with `category: domain-model` in frontmatter) are special: a project usually has one primary domain model that defines its core data shape (e.g., property-graph for a network analysis tool, ledger for a financial system). When detected, promote the primary domain model to the atlas `purpose` field and note it explicitly in the component descriptions that implement it. Secondary domain models (e.g., search-index alongside a catalog) are recorded normally alongside implementation patterns.

## Gap Identification

Determine which patterns are absent but expected given what was found. Use three checks:

1. **External calls without resilience.** Grep for HTTP clients, database drivers, and RPC stubs. If external calls exist but no circuit-breaker, retry, timeout, or bulkhead was detected, flag each as a gap.
2. **Stack-implied patterns.** Match the project's stack against expected patterns: web API implies input validation and rate limiting; async workers imply backpressure and dead-letter handling; microservices imply service discovery and distributed tracing; any service implies structured logging and health checks.
3. **Catalog cross-references.** Review which detected patterns commonly pair together. If one half of a well-known pair is present but the other was not detected, flag it (e.g., event sourcing detected without CQRS, or circuit-breaker without retry).

## Error Handling

- **No patterns detected:** Valid for small/unconventional projects. Produce empty concept sections and focus on gaps.
- **Uncommon languages:** Catalog is strongest for Python, TS/JS, Go, Java, K8s. Grep still works for structural patterns; note coverage gaps in scan_metadata.
- **Tool unavailable:** If ast-grep or semgrep is missing or a rule fails, continue with grep fallback. Note which tools were unavailable in scan_metadata.
