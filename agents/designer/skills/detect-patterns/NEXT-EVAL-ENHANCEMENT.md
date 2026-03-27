# Eval Enhancement: Dynamic Repo Discovery

**Priority:** Apply after current eval pass completes.

## Requirements

Each eval run should start by discovering and cloning NEW repos that haven't been tested before. This builds a growing database of test repos over time.

### 1. Repo Discovery Step (runs before eval)

- Use `gh api search/repositories` to find popular repos in Python and TypeScript
- Query examples: `stars:>5000 language:python`, `stars:>5000 language:typescript`
- Pick 2-3 random repos not already in `/tmp/eval-repos/`
- Clone them with `--depth=1`
- Add them to a persistent repo registry at `/kord/kordinate/agents/designer/memory/concepts/eval-repos.json`:
```json
{
  "repos": [
    { "url": "https://github.com/django/django", "language": "python", "added": "2026-03-27", "runs": 3 },
    { "url": "https://github.com/some/new-repo", "language": "typescript", "added": "2026-03-27", "runs": 0 }
  ]
}
```
- Each run adds new repos AND tests all existing ones
- Over time this becomes a massive diverse test suite

### 2. Diversity Heuristics for Repo Selection

- Mix languages (don't pick 5 Python repos in a row)
- Mix domains (web frameworks, CLI tools, data science, DevOps, etc.)
- Mix sizes (some small focused libs, some large frameworks)
- Avoid forks and archived repos

### 3. Persistence

The repo registry persists in git so it survives across sessions.
