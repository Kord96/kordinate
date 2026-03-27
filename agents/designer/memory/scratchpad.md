---
description: Designer working notes and observations
curated: false
scope: global
---
- **2026-03-27**: AST-grep eval framework built at `skills/detect-patterns/{eval,audit,tune}-ast-rules.sh`. First eval pass (159 rules x 8 repos) baseline: 20,903 total matches, 49 suspects. After fixing 13 overly-generic rules, reduced to 15,301 matches (26.8% reduction), 30 suspects. Key false-positive patterns: generic `.parse()` matching JSON.parse, `.load()` matching cheerio.load, `import()` matching all dynamic imports, guard clauses (`if not: raise`) too broad for aggregate, `const x = () => {}` matching all arrow functions, 5-deep property chains too common in frameworks (raised to 6). Test repos at `/tmp/eval-repos/`. Remaining high counts (decorator 6331, active-record 3292 in Django) are true positives.
