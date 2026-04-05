# JSON Schemas

Defines the JSON schemas used by the improve skill's eval and benchmark modes.

---

## evals.json

Test case definitions for a skill. Located at `evals/evals.json` within the workspace.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {"text": "...", "passed": true, "evidence": "..."}
  ],
  "summary": {"passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67},
  "execution_metrics": {
    "tool_calls": {"Read": 5, "Write": 2, "Bash": 8},
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450
  },
  "timing": {
    "total_tokens": 84852,
    "duration_ms": 23332,
    "total_duration_seconds": 23.3
  },
  "claims": [
    {"claim": "...", "type": "factual", "verified": true, "evidence": "..."}
  ],
  "user_notes_summary": {"uncertainties": [], "needs_review": [], "workarounds": []},
  "eval_feedback": {
    "suggestions": [{"assertion": "...", "reason": "..."}],
    "overall": "..."
  }
}
```

---

## benchmark.json

Output from benchmark mode. Located at `benchmarks/<timestamp>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "...",
    "skill_path": "...",
    "executor_model": "...",
    "analyzer_model": "...",
    "timestamp": "...",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85, "passed": 6, "failed": 1, "total": 7,
        "time_seconds": 42.5, "tokens": 3800, "tool_calls": 18, "errors": 0
      },
      "expectations": [{"text": "...", "passed": true, "evidence": "..."}],
      "notes": ["Extracted from user_notes_summary"]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.71, "max": 1.0},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 30.0, "max": 55.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.43},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 22.0, "max": 40.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1700, "max": 2500}
    },
    "delta": {"pass_rate": "+0.50", "time_seconds": "+13.0", "tokens": "+1700"}
  },
  "notes": ["Observation strings from analyzer"]
}
```

**Important:** The eval-viewer reads these field names exactly. Use `configuration` (not `config`), nest `pass_rate` under `result` (not top-level). See eval-viewer/viewer.html source for rendering logic.

---

## comparison.json

Output from blind comparator. Located at `<grading-dir>/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "...",
  "rubric": {
    "A": {"content": {}, "structure": {}, "content_score": 4.7, "structure_score": 4.3, "overall_score": 9.0},
    "B": {"content": {}, "structure": {}, "content_score": 2.7, "structure_score": 2.7, "overall_score": 5.4}
  },
  "output_quality": {
    "A": {"score": 9, "strengths": [], "weaknesses": []},
    "B": {"score": 5, "strengths": [], "weaknesses": []}
  },
  "expectation_results": {
    "A": {"passed": 5, "failed": 1, "total": 6},
    "B": {"passed": 3, "failed": 3, "total": 6}
  }
}
```

---

## analysis.json

Output from post-hoc analyzer. Located at `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {"winner": "A", "winner_skill": "...", "loser_skill": "...", "comparator_reasoning": "..."},
  "winner_strengths": [],
  "loser_weaknesses": [],
  "instruction_following": {
    "winner": {"score": 9, "issues": []},
    "loser": {"score": 6, "issues": []}
  },
  "improvement_suggestions": [
    {"priority": "high", "category": "instructions", "suggestion": "...", "expected_impact": "..."}
  ],
  "transcript_insights": {}
}
```

---

## trigger-eval.json

Trigger evaluation queries for description optimization.

```json
[
  {"query": "realistic user prompt", "should_trigger": true},
  {"query": "similar but unrelated prompt", "should_trigger": false}
]
```

Queries should be realistic — not abstract requests but concrete with file paths, context, casual speech. Focus on edge cases, not clear-cut matches.
