---
description: Generic checklist for deciding what to inspect before changing a skill, detector, prompt, or output format
---

# Skill Improvement Checklist

Use this before editing a skill or building a benchmark. The goal is to identify which layer is actually weak instead of changing everything at once.

## 1. Identify The Failure Layer

Ask:

- Is the failure in triggering?
- Is the failure in task decomposition or workflow?
- Is the failure in deterministic extraction or detection?
- Is the failure in semantic interpretation or synthesis?
- Is the failure in output format, organization, or usability?
- Is the failure in latency, token cost, or variance?

Do not start by rewriting prompts if the real issue is missing evidence or weak evaluation.

## 2. Check The Evaluation Itself

Ask:

- Are the evals testing real user tasks or toy prompts?
- Are assertions concrete and falsifiable?
- Are we measuring false positives as well as misses?
- Are repeated runs stable enough to trust the result?
- Are we overfitting to one repo, one task, or one benchmark format?

Weak evals create fake progress.

## 3. Separate Evidence From Interpretation

For skills that analyze code or systems, identify:

- What is deterministic evidence?
- What is inferred or semantic interpretation?
- What can auto-confirm safely?
- What should remain a candidate until reviewed?

If this boundary is fuzzy, improve it before adding more heuristics.

## 4. Classify The Error Pattern

Use one or more of:

- precision problem
- recall problem
- grounding problem
- orchestration problem
- prompt-shape problem
- formatting/schema problem
- performance problem
- benchmark problem

This makes it easier to choose the next change.

## 5. Choose The Smallest Useful Change

Prefer this order:

1. Fix broken evals or missing instrumentation.
2. Fix missing evidence or deterministic extraction.
3. Fix decision policy or semantic review logic.
4. Fix synthesis and output organization.
5. Tune prompts only after the earlier layers are understood.

## 6. Verify What Improved

After changes, answer:

- What metric improved?
- What did not improve?
- What regressed?
- On which tasks or repos did the change matter?
- Did runtime or token cost increase?

If you cannot answer this, the change was not measured well enough.

## 7. Persist The Right Lesson

Decide whether the result should become:

- a code change
- a benchmark change
- a detector/policy change
- a reusable methodology note
- a durable memory/reflection

Not every run-level observation deserves promotion into memory.
