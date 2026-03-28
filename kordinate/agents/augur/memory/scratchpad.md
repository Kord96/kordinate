---
description: Designer working notes and observations
curated: false
scope: global
---

- **2026-03-27**: map-dependencies skill improved: added multi-language support (Python/JS-TS/Go), ASCII graph examples (box and flat-list formats), error handling for missing modules/infra/deep cycles, --reverse performance note mentioning context:fork, pushy description for better triggering, reasoning-based language instead of ALWAYS/NEVER directives.
- **2026-03-27**: assess-debt skill rewritten (78 to 113 lines). Key additions: explicit detect-patterns dependency section explaining the patterns.md relationship and fallback behavior; grading scale table with interpretation and suggested actions per grade (A=healthy through F=urgent); edge case handling for no patterns detected, small projects, and all-MINOR violations; new prioritized Recommendations section in output format ranking by severity/blast-radius/effort/clustering; full example output with realistic violation data; description made pushy for better triggering (tech debt assessment, code quality scoring, debt prioritization, refactoring planning, architecture health checks).
