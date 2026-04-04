---
description: Proposed schema for per-concept meta.yaml files and evidence-first detection records used by Augur during analysis
---

# Augur concept metadata schema

Purpose:
- keep `concept.md` as the canonical human-readable concept narrative
- add one optional per-concept `meta.yaml` for machine-readable detection policy and structured operational guidance
- keep `ast-grep.yaml` and `semgrep.yaml` as separate support artifacts
- make Augur detection evidence-first: tools emit structured evidence, then policy derives a verdict
- support incremental migration by making all `meta.yaml` sections optional

## Design principles

1. **Evidence-first, not score-first.** Scores support evidence; they do not replace it.
2. **`concept.md` remains canonical for semantics.** Recognition signatures, architectural meaning, and nuanced interpretation stay in Markdown.
3. **`meta.yaml` holds structured policy.** Questions, detector policy, and operational guidance live there.
4. **Rule files remain external.** `ast-grep.yaml` and `semgrep.yaml` stay executable support artifacts.
5. **Negative rule output is usually neutral.** No rule hit is not strong evidence of absence.
6. **Ambiguity produces `candidate`, not forced detection.**

## Concept directory shape

```text
concepts/<name>/
  concept.md        # canonical narrative: meaning, signatures, confidence, architecture notes
  meta.yaml         # optional structured companion: detector policy + questions + ops guidance
  ast-grep.yaml     # optional structural support artifact
  semgrep.yaml      # optional semantic/security support artifact
  questions.yaml    # legacy optional questions during migration
  testing.md        # legacy optional testing guidance during migration
  monitoring.md     # legacy optional monitoring guidance during migration
  deployment.md     # legacy optional deployment guidance during migration
```

## 1. `meta.yaml` schema

```yaml
schema: augur-concept-meta/v2

concept: <kebab-case concept id>
kind: pattern | anti-pattern | domain-model | flow-shape | structure-shape
summary: <optional one-line summary>

taxonomy:
  type: pattern | anti-pattern | domain-model | flow-shape | structure-shape
  categories:
    - <category>
    - <category>

detectors:
  ast_grep:
    enabled: true | false
    file: ast-grep.yaml
    detector_strength: 1 | 2 | 3 | 4 | 5
    notes: <optional detector note>

  semgrep:
    enabled: true | false
    file: semgrep.yaml
    detector_strength: 1 | 2 | 3 | 4 | 5
    notes: <optional detector note>

  signatures:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5

  questions:
    enabled: true | false
    detector_strength: 1 | 2 | 3 | 4 | 5
    ask_when:
      - noisy_rule_match
      - conflicting_evidence
      - architecture_level_concept
      - broad_match
      - low_rule_confidence

policy:
  auto_confirm:
    allowed: true | false
    min_detector_strength: 1 | 2 | 3 | 4 | 5
    min_match_confidence: 1 | 2 | 3 | 4 | 5
    requires_no_contradiction: true | false

  unresolved_state: candidate | inconclusive
  negative_rule_result_means: neutral
  broad_match_requires_questions: true | false

diagnostic_questions:
  threshold: <integer>
  questions:
    - id: <stable question id>
      prompt: <question text>
      weight: <integer>
      signals:
        - <optional grep hint>
        - <optional grep hint>

analysis:
  testing:
    summary: <optional one-line summary>
    unit:
      - <test guidance>
    integration:
      - <test guidance>
    failure_injection:
      - <test guidance>

  monitoring:
    summary: <optional one-line summary>
    metrics:
      - name: <metric name>
        kind: counter | gauge | histogram | summary | other
        description: <what it measures>
    alerts:
      - <alert guidance>

  deployment:
    summary: <optional one-line summary>
    rollout_implications:
      - <deployment behavior note>
    pre_deploy_checklist:
      - <checklist item>

artifacts:
  support_rules:
    ast_grep: ast-grep.yaml | null
    semgrep: semgrep.yaml | null

migration:
  replaces:
    - questions.yaml
    - testing.md
    - monitoring.md
    - deployment.md
```

## 2. Score semantics

Augur uses two numeric scores plus a discrete verdict.

### `detector_strength`
Concept-level prior maintained in `meta.yaml`.

Meaning: how much policy weight this detector type should carry for this concept in general.

- **5** — highly trustworthy and specific; may be eligible for auto-confirm
- **4** — strong evidence source, but may still need light verification
- **3** — useful but requires corroboration
- **2** — weak clue only
- **1** — metadata only; never decisive on its own

### `match_confidence`
Run-level score emitted by the detector.

Meaning: how convincing this specific evidence instance is.

- **5** — precise, canonical, low-noise match
- **4** — strong match with minor ambiguity
- **3** — partial or somewhat noisy evidence
- **2** — weak or broad signal
- **1** — unusable or misleading signal

### Verdict states
Detector-local and concept-final decisions use these verdicts:

- `confirmed`
- `candidate`
- `inconclusive`
- `contradicted`

## 3. Evidence record schema

Rule runners and other detection steps should emit structured evidence records. Augur can then combine those records with the deterministic decision layer in `agents/augur/scripts/concept_decision.py`.

```yaml
schema: augur-evidence-record/v1

concept: <concept id>

detector:
  type: ast_grep | semgrep | signatures | questions | grep
  rule_id: <optional rule id>
  rule_file: <optional rule file>
  language: <optional language>
  framework: <optional framework>

polarity: positive | negative | neutral

scores:
  detector_strength: 1 | 2 | 3 | 4 | 5
  match_confidence: 1 | 2 | 3 | 4 | 5

verdict: confirmed | candidate | inconclusive | contradicted

summary:
  matched: true | false
  match_count: <integer>
  specificity: exact | narrow | broad
  scope: file | component | repo
  noise: low | medium | high
  contradiction_flags:
    - <flag>
  notes:
    - <short explanation>

locations:
  - path: <repo path>
    line: <line number>
    excerpt: <optional excerpt>

signals:
  - <signal>
  - <signal>

follow_up:
  recommended_next_step: none | ask_questions | verify_signatures | targeted_read
  question_ids:
    - <question id>
```

## 4. Question result schema

Questions are another evidence source and should produce structured output too. Their outputs should feed the same deterministic concept decision layer as ast-grep and semgrep evidence.

```yaml
schema: augur-question-result/v1

concept: <concept id>
detector: questions
polarity: positive | negative | neutral

scores:
  detector_strength: 1 | 2 | 3 | 4 | 5
  match_confidence: 1 | 2 | 3 | 4 | 5

verdict: confirmed | candidate | inconclusive | contradicted

summary:
  threshold: <integer>
  total_yes_weight: <integer>
  max_weight: <integer>
  specificity: exact | narrow | broad
  scope: file | component | repo
  noise: low | medium | high
  contradiction_flags:
    - <flag>

answers:
  - id: <question id>
    answer: yes | no | unknown
    weight: <integer>
    justification: <short reason>

locations:
  - path: <repo path>
    line: <line number>
```

## 5. Final concept decision schema

Augur should combine all evidence records into one concept decision.

```yaml
schema: augur-concept-decision/v1

concept: <concept id>

decision:
  detected: true | false
  verdict: confirmed | candidate | inconclusive | contradicted
  confidence: high | medium | low

reasoning:
  supporting_evidence:
    - detector: <detector type>
      verdict: <verdict>
      note: <short reason>

  contradictions:
    - <short contradiction>

  rationale:
    - <plain-language justification>

grounding:
  files:
    - <path:line>

policy_trace:
  auto_confirm_used: true | false
  semantic_questions_used: true | false
  rule_negative_treated_as_neutral: true | false
```

## 6. Deterministic decision policy

Use a small deterministic layer before freeform LLM judgment.

### Confirmed
Set final verdict to `confirmed` when one of these is true:

1. one evidence record has:
   - `detector_strength >= 5`
   - `match_confidence >= 5`
   - `specificity in {exact, narrow}`
   - no contradiction flags
2. semantic questions pass threshold with strong grounding
3. two independent medium-strong evidence sources agree

### Candidate
Use `candidate` when:
- evidence is positive but broad
- structural evidence exists without semantic confirmation
- evidence is mixed but not strongly contradictory

### Inconclusive
Use `inconclusive` when:
- only weak clues exist
- evidence is too sparse or noisy to support either direction

### Contradicted
Use `contradicted` when:
- semantic evidence clearly rejects the concept
- matched structure is better explained by a neighboring concept
- concept-defining questions fail clearly

## 7. Ambiguity policy

- Broad structural matches should trigger semantic questions.
- No rule hit is usually **neutral**, not evidence of absence.
- Negative semantic answers are stronger than missing rule hits.
- If two concepts explain the same broad structural evidence, keep both as `candidate` until differentiating questions resolve them.
- Architecture-level concepts should generally require semantic confirmation unless the structural evidence is unusually specific.

## 8. Minimal migration rules

1. `concept.md` remains required and authoritative for concept meaning.
2. If `meta.yaml` exists, Augur should prefer it for detector policy, questions, and structured operational guidance.
3. If `meta.yaml` is missing a subsection, Augur should fall back to legacy files.
4. `ast-grep.yaml` and `semgrep.yaml` remain separate support artifacts.
5. Migrate concept-by-concept; do not require catalog-wide parity before adoption.

## 9. Minimal example

```yaml
schema: augur-concept-meta/v2

concept: circuit-breaker
kind: pattern
summary: Stop calling a failing dependency until recovery is likely.

taxonomy:
  type: pattern
  categories: [resilience, integration]

detectors:
  ast_grep:
    enabled: true
    file: ast-grep.yaml
    detector_strength: 4
    notes: Canonical library and state-machine matches are strong, but hand-rolled variants may need verification.

  semgrep:
    enabled: false

  signatures:
    enabled: true
    detector_strength: 4

  questions:
    enabled: true
    detector_strength: 5
    ask_when:
      - low_rule_confidence
      - conflicting_evidence
      - broad_match

policy:
  auto_confirm:
    allowed: true
    min_detector_strength: 5
    min_match_confidence: 5
    requires_no_contradiction: true

  unresolved_state: candidate
  negative_rule_result_means: neutral
  broad_match_requires_questions: true

diagnostic_questions:
  threshold: 6
  questions:
    - id: breaker-state-machine
      prompt: Is there a closed/open/half-open state machine that governs calls to a dependency?
      weight: 3
      signals: [closed, open, half-open, breaker state]

    - id: breaker-threshold
      prompt: Do failures accumulate to a threshold that opens the circuit?
      weight: 3
      signals: [failure threshold, fail_max, trip circuit]

    - id: breaker-probes
      prompt: Are limited probe calls used to test recovery before closing the circuit?
      weight: 2
      signals: [probe request, half-open test, recovery check]

analysis:
  testing:
    summary: Test full state transitions and fallback behavior.
    unit:
      - Verify closed-to-open transition after failures reach threshold.
      - Verify successful probe calls move the circuit back to closed.
    integration:
      - Degrade a real dependency and verify the breaker opens and later recovers.
    failure_injection:
      - Simulate a flapping dependency and verify the breaker does not oscillate excessively.

  monitoring:
    summary: Track circuit state transitions and dependency failure rates.
    metrics:
      - name: circuit_state
        kind: gauge
        description: Current breaker state per dependency.
      - name: circuit_failures_total
        kind: counter
        description: Failure count that drives the breaker.
    alerts:
      - Circuit open for longer than expected recovery window.
      - Repeated open-close cycling indicates a flapping dependency.

  deployment:
    summary: Consider dependency health and rollout coordination.
    rollout_implications:
      - Avoid synchronized breaker opens during rollout when a dependency is already degraded.
    pre_deploy_checklist:
      - Verify recovery timeouts and readiness behavior are compatible.

artifacts:
  support_rules:
    ast_grep: ast-grep.yaml
    semgrep: null

migration:
  replaces:
    - questions.yaml
    - testing.md
    - monitoring.md
    - deployment.md
```
