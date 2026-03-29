# Install Checklist

Verification checklist for `/install`. Run after every install or major update to confirm the system is wired correctly.

## Agent Memory

- [ ] Each agent has separate preloaded memory files in KORD.json
- [ ] Preload script (`team/scripts/preload.py`) loads the right files per agent
- [ ] Agent memory is separate from main session memory
- [ ] Memory files are owned by their agent (`owner` field in KORD.json)

## Boot

- [ ] Boot loads global preloaded files via preload.py
- [ ] Boot loads project-scoped memory (from `.kord/` in project root) if it exists
- [ ] Shared protocols (`preload: all`) load for every agent

## File Protection

- [ ] IDENTITY.md files have `validation: "scribe"` in KORD.json
- [ ] SKILL.md files are framework-protected (by convention or KORD.json entries)
- [ ] Shared protocols have `validation: "scribe"` in KORD.json
- [ ] KORD.json itself requires warden auth (guard entry)
- [ ] Agent knowledge files have `validation: "<owning-agent>"`

## User-Added Validation

- [ ] Users can add new file entries to KORD.json (with warden auth)
- [ ] New entries with `validation` field are enforced by the guard
- [ ] KORD-seed.json provides factory reset capability

## Warden Completion Token

- [ ] `/kord warden validate <dir>` runs the registered validator
- [ ] Validator returns completion token (sha256) on success
- [ ] Validator returns errors on failure with fix instructions
- [ ] Skills that need validation include the token in their report
- [ ] Improve loop can verify: hash(current files) == reported token

## Subagent Communication

- [ ] Agents can call other agents via `/kord <agent> <skill>`
- [ ] Kord delegate returns gate secret for local spawns
- [ ] Agent-gate hook allows spawns with valid gate secret
- [ ] Sauron can call augur and alfred via kord
- [ ] Augur can call warden via kord

## Install Hygiene

- [ ] Install wipes `~/.claude/skills/` before copying (prevents stale skills)
- [ ] Install wipes `~/.claude/agents/` before copying (prevents stale agent defs)
- [ ] Install preserves `~/.claude/projects/` (user auto-memory)
- [ ] Install preserves `~/.claude/settings.json` user-specific settings (merges, not overwrites)
- [ ] Backup of previous `~/.kord/` taken before wipe
- [ ] Only team skills copied to `~/.claude/skills/` (agent skills go through kord)
- [ ] Agent definitions copied to `~/.claude/agents/`
- [ ] KORD.json assembled and copied to `~/.kord/`
- [ ] Hooks copied to `~/.kord/hooks/`
- [ ] Settings.json hooks merged into `~/.claude/settings.json`

## Sanitize

- [ ] Push guard scans diff for secrets via `sanitize-scan.py`
- [ ] Patterns loaded from `sanitize/patterns.yaml`
- [ ] Critical findings block push
- [ ] Error message directs to `/kord alfred store key`

## No Stale Files

- [ ] No stale skills in `~/.claude/skills/` from previous installs
- [ ] No stale agent definitions in `~/.claude/agents/`
- [ ] No stale hooks in `~/.kord/hooks/`
- [ ] Old `skills/` global directory doesn't exist (replaced by `team/skills/`)
