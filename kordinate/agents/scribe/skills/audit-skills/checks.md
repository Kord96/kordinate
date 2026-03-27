# Skill audit checks

Each check has an ID, severity, layer, and description. The audit runs every check against each SKILL.md file.

## Structure checks

| ID | Severity | Check | Details |
|----|----------|-------|---------|
| S01 | ERROR | Frontmatter exists | SKILL.md must start with `---` YAML frontmatter block |
| S02 | ERROR | `name` field present | Frontmatter must include `name` |
| S03 | WARNING | `description` field present | Without a description, Claude cannot auto-invoke the skill |
| S04 | WARNING | `curated` field present | Kordinate convention: all production skills should declare `curated: true` |
| S05 | WARNING | `scope` field present | Kordinate convention: should declare `global` or `project` scope |
| S06 | INFO | `argument-hint` present when skill accepts args | If the skill body references `$ARGUMENTS`, `$0`, or `$1`, frontmatter should include `argument-hint` |
| S07 | INFO | SKILL.md under 500 lines | Large skills should use supporting files for reference material |
| S08 | INFO | Supporting files referenced | If sibling `.md` files exist, SKILL.md should link to them |

## Quality checks

| ID | Severity | Check | Details |
|----|----------|-------|---------|
| Q01 | WARNING | Description is specific | Description should be >20 chars and describe when/why to use the skill, not just what it does |
| Q02 | WARNING | Instructions have numbered steps | Task-oriented skills should have a clear step sequence |
| Q03 | INFO | Description avoids vague terms | Flag descriptions using "stuff", "things", "various", "etc" without specifics |
| Q04 | INFO | Arguments documented | If the skill accepts arguments, there should be an Arguments section explaining them |
| Q05 | INFO | Output format specified | Skills that produce reports should describe their output format |
| Q06 | INFO | Error handling documented | Skills should describe what happens when input is invalid or missing |

## Security checks

| ID | Severity | Check | Details |
|----|----------|-------|---------|
| X01 | WARNING | `disable-model-invocation` on destructive skills | Skills that write files, deploy, or modify infrastructure should consider `disable-model-invocation: true` |
| X02 | INFO | `allowed-tools` on read-only skills | Skills that only scan/audit should restrict tools to prevent accidental writes |
| X03 | INFO | `context: fork` on heavy analysis | Long-running read-heavy skills are candidates for isolated context |

## Cross-reference checks

| ID | Severity | Check | Details |
|----|----------|-------|---------|
| R01 | WARNING | No name collisions | Two skills should not share the same `name` value |
| R02 | INFO | Supporting files not orphaned | Every `.md`, `.sh`, `.py` sibling of SKILL.md should be referenced from SKILL.md or another supporting file |
| R03 | INFO | Description fits budget | Total description text across all skills should stay under 16k chars (2% context budget) |

## Output format

```
## Skill Audit Report

**Scanned**: N skills across M agents
**Results**: X errors, Y warnings, Z info

### Errors
| Skill | Agent | Check | Details |
|-------|-------|-------|---------|
| ...   | ...   | ...   | ...     |

### Warnings
| Skill | Agent | Check | Details |
|-------|-------|-------|---------|
| ...   | ...   | ...   | ...     |

### Info
| Skill | Agent | Check | Details |
|-------|-------|-------|---------|
| ...   | ...   | ...   | ...     |

### Quick wins
- [ ] Fix 1 — resolves N findings
- [ ] Fix 2 — resolves N findings
```
