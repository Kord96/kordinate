---
description: Evaluation of external skill marketplaces (anthropic-agent-skills, alirezarezvani/claude-skills) for integration into deployer, sauron, designer, scribe — verdicts, priorities, cross-agent dependencies
curated: true
scope: global
preloaded: scribe
---

# External Skill Marketplace Evaluation (2026-03-25)

## Sources Evaluated
- **anthropic-agent-skills** marketplace (17 skills) — `/plugin marketplace add anthropics/skills`
- **alirezarezvani/claude-skills** GitHub repo (205 skills, all stdlib Python, zero pip deps)

## Verdicts by Agent

### Deployer
| Skill | Verdict | Notes |
|---|---|---|
| senior-devops | SKIP | Agent-as-pipeline model — no CI/CD pipelines |
| helm-chart-builder | SKIP | Kustomize + raw manifests, not Helm |
| ci-cd-pipeline-builder | SKIP | Same as senior-devops |
| docker-development | REFERENCE | Image optimization checklist for infra images → memory/infra.md |
| env-secrets-manager | REFERENCE | Rotation procedure only → memory/infra.md (already uses pass store) |
| runbook-generator | ABSORB | Template structure → new /infra runbook subcommand |
| incident-commander | ABSORB | Severity matrix (SEV1-4) → memory/incident-severity.md + kord |

Self-improvements: /infra preflight, /infra rollback, post-deploy-verify kord, deployment audit trail

### Sauron
| Skill | Verdict | Notes |
|---|---|---|
| observability-designer | ABSORB | slo_designer.py, alert_optimizer.py, dashboard_generator.py → new /sauron:alert |
| incident-commander | ABSORB | incident_classifier.py, timeline_reconstructor.py, pir_generator.py → new /sauron:incident |
| runbook-generator | ABSORB | Template into enhanced /diagnose output |
| performance-profiler | SKIP | No tracing infra yet — inverts priority |
| webapp-testing | REFERENCE | Memory note only (Grafana smoke test) |

Self-improvements: /sauron:alert (biggest system gap — no alerting at all), extend catalog with slos/alerts/runbooks, enhance /scan + /diagnose, /sauron:incident
**Prerequisite**: deployer must add Alertmanager manifest + Prometheus rule_files config

### Designer
| Skill | Verdict | Notes |
|---|---|---|
| senior-architect | PARTIAL ABSORB | Decision frameworks → memory; dependency mapping → new skill |
| tech-debt-tracker | ABSORB | New /designer:assess-debt with scoring matrix |
| api-design-reviewer | ABSORB | New /designer:review-api |
| database-designer | REFERENCE | Schema review checklist → memory |
| agent-workflow-designer | SKIP | Wrong domain (AI agent patterns, not app architecture) |
| dependency-auditor | REFERENCE | Hygiene checklist → memory |

Self-improvements: **fill 12/16 empty pattern sections** (highest ROI), new skills (review-api, assess-debt, map-dependencies, record-decision), enhance detect-patterns with observability coverage, pattern files may belong as skill resources not memory

### Scribe
| Skill | Verdict | Notes |
|---|---|---|
| self-improving-agent | PARTIAL ABSORB | Memory health + curation → /audit. Skip rule promotion (incompatible model) |
| codebase-onboarding | REFERENCE | Pointer from /onboard step 9 |
| skill-creator | REFERENCE | Development tool, not runtime |

Self-improvements: /recall (cross-agent search, stateless kord — more value at scale), /audit (health check), /remember dedup enhancement

## Implementation Priority
1. Fill Designer's 12 empty pattern Monitoring/Deployment/Testing sections
2. Sauron /alert skill (+ Alertmanager prerequisite)
3. Wire deployer→sauron coordination into roll (make existing kords work)
4. Scribe /audit
5. Extend /scan catalog format (slos, alerts, runbooks sections)
6. Scribe /recall (scale play — low urgency at 4 agents)

## Key Insight
Biggest limitation is coordination depth, not skill coverage. Kords exist but aren't systematically invoked. Designer patterns have empty monitoring sections so Sauron can't reference them. Fix the wiring before adding new capabilities.
