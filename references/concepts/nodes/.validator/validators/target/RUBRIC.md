---
schema: validator-rubric.v1
validation_intent: target
---

# Target Rubric

## Rubric

| Signal | Weight | Source | Success Condition | Error Condition | Scoring Guidance |
|---|---:|---|---|---|---|
| Boundary | 0.15 | Target docs and adjacent concerns. | The validated target is clearly scoped and distinct from adjacent concerns. | Scope is generic, overlapping, or unclear enough to cause noisy validation. | Score boundary clarity, exclusions, and overlap control. |
| Deterministic Signal | 0.20 | Optional validator module and machine-readable outputs. | Machine checks are precise, grounded, and useful when present. | Checks are missing despite being necessary, broad, noisy, or disconnected from the runtime contract. | Score false-positive risk, false-negative risk, grounding, and usefulness. |
| Dataset Coverage | 0.20 | Fixtures, examples, golden files, benchmark repos, expected outputs, or documented cases. | Representative active cases or goldens are enough to trust the validator. | Coverage is missing, stale, planned-only, too narrow, or lacks an oracle. | Score quantity, quality, representativeness, freshness, confounders, and oracle quality. |
| Generalization / Anti-Overfitting | 0.10 | Fixtures, examples, benchmark repos, expected outputs, detector code, and semantic guidance. | Signals are expected to transfer beyond the known validation cases. | The validator depends on benchmark-specific names, paths, fixtures, or private implementation details as if they were the target behavior. | Score transferability and resistance to benchmark memorization. |
| Semantic Guidance | 0.20 | This document, TEST.md, logs, and accepted review procedure. | Guidance lets agents make consistent accept/reject/qualify decisions. | Guidance is too generic to improve judgment or contradiction handling. | Score acceptance criteria, rejection criteria, caveats, and ambiguity handling. |
| Policy Honesty | 0.10 | Target docs, deterministic checks, and rubric claims. | The validator clearly states what is deterministic, semantic, optional, or unsupported. | The validator claims unsupported determinism or hides assumptions. | Score honesty of mode, evidence, and assumptions. |
| Downstream Usefulness | 0.05 | Validation output and intended downstream workflows. | Results help the next workflow or user decision without rediscovery. | Results are generic, noisy, or not actionable. | Score specificity, navigability, and usefulness for downstream work. |
