# Augur Analyze Reflection Prompt

Use this as `reflection_prompt` for Augur `/analyze` benchmark runs while the daemon still expects:

```json
{"project":"...","general":"..."}
```

Both values must be strings.

## Prompt

```text
Return strict JSON only with exactly these keys:
{"project":"...","general":"..."}

Context: this was an Augur /analyze run on a pinned repository snapshot.

Write `project` as a short paragraph covering only lessons specific to this repo:
- unusual architectural patterns or conventions
- naming/layout choices that could mislead shallow analysis
- signals that helped identify components, dependencies, workflows, or concepts
- false-positive traps or weak signals in this codebase

Write `general` as a short paragraph covering only transferable lessons for improving Augur:
- possible new grep signatures
- possible AST rule ideas
- possible diagnostic questions
- concept gaps or anti-pattern traps
- detector heuristics that should be strengthened or avoided

Rules:
- Output strict JSON only
- Both values must be plain strings
- Do not include markdown
- Do not repeat the task output
- Do not report timing, tokens, or benchmark metadata
- Focus on detection and architectural lessons
- Keep each string under 140 words
- If there is no strong lesson for a field, return an empty string
```

## Example Output

```json
{
  "project": "This repo hides workflow boundaries in job registration files rather than service directories. Component boundaries are signaled more by queue names and event topics than by folder structure. Several 'service' modules are just thin adapters, so naming alone would overstate architectural significance.",
  "general": "Add detector support for queue-name and event-topic evidence when inferring workflow or service boundaries. Avoid treating 'service' and 'worker' directory names as sufficient signals. Consider new grep or AST patterns for plugin registration through exported config arrays and background-job registries."
}
```

## Intended Use

This prompt is designed for current daemon compatibility and should be stored with Augur, not the generic improve framework.

Benchmark runners can attach this prompt to Augur runs, store the resulting reflections per run, and later aggregate them into detector-improvement suggestions.
