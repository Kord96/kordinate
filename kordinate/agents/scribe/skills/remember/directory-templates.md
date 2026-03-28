# Directory Templates

Level 3 resource for the remember, onboard, and create-kord skills. Defines the expected directory structure for each type of kordinate entity.

When creating or validating a directory, check that all required files exist.

## Concept Directory

Path: `agents/augur/memory/concepts/<concept-name>/` (canonical path)

| File | Required | Purpose |
|------|----------|---------|
| `concept.md` | yes | Core concept definition — frontmatter + Recognition + Architecture sections. See [concept-template.md](concept-template.md). |
| `README.md` | no | Extended documentation for the human-facing docs site |
| `<impl>.md` | no | Implementation-specific reference (e.g., `stoik.md` for stream-to-store, `orchestrator.md` for service-manager) |

## Kord Directory

Path: `agents/<provider>/kords/<kord-name>/`

| File | Required | Purpose |
|------|----------|---------|
| `contract.md` | yes | Frontmatter (description, requester, mode, skill, curated, cache_inputs) defining the consultation contract |
| `data.md` | stateful only | Cached state — stores last response with `.valid` timestamp |
| `expiry.sh` | stateful only | Cache check script — delegates to `lib/kord-expiry.sh`. Exit 0 (fresh), 1 (stale), 2 (uncertain) |
| `review.md` | stateful only | Prompt template for stage 2 agent review — must contain `{{DIFF}}` and `{{CACHED_DATA}}` placeholders |

Stateless kords (like remember, sanitize) only need `contract.md`. Stateful kords (like charon-default, cluster-topology) need all four files.

## Agent Directory

Path: `agents/<agent-name>/`

| File/Dir | Required | Purpose |
|----------|----------|---------|
| `IDENTITY.md` | yes | Agent definition — frontmatter (name, description, model, color, memory, tools, curated, preloaded) + skills table + rules + consultation |
| `memory/` | yes | Agent's knowledge store |
| `memory/scratchpad.md` | yes | Uncurated working notes (curated: false) |
| `memory/tools.md` | no | Tools reference for the agent |
| `memory/workflow.md` | no | Agent's standard workflow |
| `skills/` | no | Agent-specific skills (not all agents have skills) |

## Skill Directory

Path: `agents/<agent-name>/skills/<skill-name>/` or `skills/<skill-name>/` (global)

| File | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | yes | Skill definition — frontmatter (name, description, curated) + procedure with numbered steps |
| `*.md` | no | Level 3 resources referenced from SKILL.md (e.g., `extractors.md`, `schema.md`, `checks.md`) |
| `*.sh` | no | Helper scripts (e.g., `generate-kord.sh`) |
| `*.py` | no | Helper scripts |

## Global Skill Directory

Path: `skills/<skill-name>/`

Same structure as agent skill directories. Global skills (boot, kord, authenticate, merge, install) are available to all agents.

## Shared Protocol

Path: `shared/<protocol-name>.md`

Single file, no directory. Frontmatter with description, curated, preloaded. Included via `@~/.kord/shared/<name>.md` in CLAUDE.md.

## Validation

When creating any directory, verify:
1. All required files exist
2. Frontmatter fields are present and valid
3. Cross-references resolve (e.g., SKILL.md links to Level 3 resources that exist)
4. The parent index (KORD.md, MEMORY.md) includes an entry for the new item
