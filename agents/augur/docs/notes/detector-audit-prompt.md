# Augur Bundle And Detector Audit Prompt

Use this prompt when asking an external model to audit Augur's analyze bundles, detector source, and detector runners with the goal of improving detection quality.

## Objective

Audit Augur's `/analyze` implementation with a detector-improvement mindset.

Focus on:

- whether the memory bundles are meaningfully distinct
- whether the selective bundle is lean enough for constrained models
- whether the holistic bundle is helping large-context models in the ways it is supposed to
- whether detector source files are specific enough to support reliable extraction
- whether AST and grep support are missing or too weak
- whether the current detector runners are likely to miss concepts or create false positives
- what concrete detector improvements would most improve architecture analysis quality

Important assumption:

- the holistic bundle is intentionally enormous
- the goal is not to make holistic small
- the real question is whether the selective/holistic split and model-to-bundle policy are well designed

## Files To Provide

At minimum, provide:

- `agents/augur/.generated/bundles/memory/analyze-selective-v1.md`
- `agents/augur/.generated/bundles/memory/analyze-holistic-v1.md`
- `agents/augur/memory/workflow.md`
- `agents/augur/detectors/facts/**/policy.yaml`
- `agents/augur/detectors/facts/**/signatures.yaml`
- `agents/augur/detectors/facts/concept-evidence/**/meta.yaml`
- `agents/augur/detectors/facts/concept-evidence/**/signatures.yaml`
- `agents/augur/skills/analyze/references/detection-method.md`
- `agents/augur/detectors/scripts/detector_loader.py`
- `agents/augur/detectors/scripts/run_ast_grep.py`
- `agents/augur/detectors/scripts/run_concept_detection.py`
- `agents/augur/detectors/scripts/infer_concepts_from_facts.py`

## Instructions

Review the files deeply. Do not give generic architecture advice.

I want concrete feedback on:

1. Bundle design
- Are selective and holistic bundles materially different in useful ways?
- Is selective lean enough for models with tighter context limits?
- What shared sections inside selective are likely wasting tokens without improving analysis?
- Does holistic appear to be carrying the right kind of semantic preload for large-context models?

2. Detector source quality
- Which fact domains are underspecified?
- Which signatures are too broad and likely to create false positives?
- Which domains need stronger negative signals?
- Which concepts are currently too semantic to rely on grep alone?

3. AST and grep opportunities
- Which fact domains should get AST rules first?
- Which concepts should get AST rules first?
- For each recommendation, explain why it is high leverage.

4. Runner and pipeline quality
- What implementation weaknesses in the scripts will limit detection quality or reliability?
- Where is the pipeline still placeholder logic rather than real detection?
- What should be fixed before adding many more detectors?

5. Prioritized improvement plan
- Give a ranked list of the top 10 improvements.
- Separate into:
  - quick fixes
  - medium detector work
  - larger refactors

## Output Format

Return JSON only with this shape:

```json
{
  "bundle_findings": [
    {
      "issue": "",
      "severity": "high|medium|low",
      "evidence": ["path"],
      "recommendation": ""
    }
  ],
  "detector_findings": [
    {
      "issue": "",
      "severity": "high|medium|low",
      "evidence": ["path"],
      "recommendation": ""
    }
  ],
  "ast_grep_priorities": [
    {
      "target": "",
      "kind": "fact-domain|concept",
      "why": "",
      "example_signals": []
    }
  ],
  "grep_priorities": [
    {
      "target": "",
      "why": "",
      "negative_signals_needed": []
    }
  ],
  "pipeline_findings": [
    {
      "issue": "",
      "severity": "high|medium|low",
      "evidence": ["path"],
      "recommendation": ""
    }
  ],
  "top_10_actions": [
    {
      "rank": 1,
      "action": "",
      "scope": "quick-fix|medium|refactor",
      "expected_impact": ""
    }
  ]
}
```
