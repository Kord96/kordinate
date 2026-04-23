# Augur Qualitative Comparison v1

This note compares the single-commit analysis quality of four lanes:

- `bare-model`
- `skill-no-facts`
- `facts-no-memory`
- `current-policy`

The goal is not just validator cleanliness. It is to judge:

- atlas quality
- story decomposition quality
- narrative usefulness
- repo-native architectural judgment

## Summary

The strongest current conclusion is:

- the base model is much stronger than expected
- Augur's most clearly defensible value is still workflow discipline and output shaping
- the current semantic preload is under pressure to prove it buys more than modest architectural polish on easier repos
- Augur's architectural advantage is clearest on harder repos like `matrixone`

At a high level:

- `matrixone`: `current-policy` is clearly best
- `rustpbx`: `bare-model` is surprisingly close; Augur advantage is modest and mostly about shaping
- `jPOS`: all lanes are viable, but `current-policy` and `facts-no-memory` compress the architecture better than `bare-model`

## MatrixOne

### Bare Model

Strengths:

- recovers the repo's major runtime slices from repo + schemas alone
- plausible roots: `service-bootstrap`, `compute-node`, `transaction-node`, `log-service`, `access-proxy`
- narratives are usable and coherent

Weaknesses:

- naming is generic rather than repo-native
- atlas over-flattens some deep runtime structure
- `file-service` stays subordinate instead of being promoted as a cross-cutting root
- overall result feels like a strong generic model summary rather than a repo-specific architecture synthesis

### Skill No Facts

Strengths:

- strong root framing: `cluster-runtime`, `query-compute`, `transaction-storage`, `log-coordination`
- shows how much value comes from workflow, schemas, validator, and repair loop alone

Weaknesses:

- still broader and more generic than the best Augur run
- decomposes more than the final current-policy shape in some places

### Facts No Memory

Strengths:

- deterministic prep helps surface deep runtime/storage slices
- better root candidates than the bare baseline in some areas

Weaknesses:

- less stable than full workflow-led runs
- not as coherent as `current-policy`
- still not the best final shape

### Current Policy

Strengths:

- best root promotion and compression:
  - `service-runtime`
  - `cn-query-runtime`
  - `transaction-storage`
  - `log-ha-coordination`
  - `file-service`
- most repo-native naming
- best cross-cutting subsystem promotion
- best teaching structure

Verdict:

- `current-policy` clearly wins on architecture quality
- this repo is the strongest evidence that Augur adds real value beyond the base model

## RustPBX

Note:

- the `current-policy` ablation lane is still running as of this draft
- the comparison below uses the best completed Augur reference run at:
  - `/kord/agents/augur-local-codex/memory/projects/restsend--rustpbx/analysis/9e8f9100da2828ac6f627329655d55cac524dffb/2026-04-17T23-44-23Z`

### Bare Model

Strengths:

- exceptionally strong from repo + schemas alone
- validator-clean: `0 warnings`
- very good narrative set:
  - `getting-started`
  - `live-call-control`
  - `recording-and-replay`
- finds legitimate runtime slices:
  - `application-host`
  - `sip-proxy`
  - `control-surfaces`
  - `recording-storage`

Weaknesses:

- over-splits implementation-adjacent components at atlas level:
  - `addon-registry`
  - `shared-storage`
  - `call-record-pipeline`
  - `sipflow-capture`
- architecture reads more like a well-organized subsystem inventory than a compressed architecture map

### Skill No Facts

Strengths:

- strong validator outcome, only one low grounding warning
- shows that workflow discipline alone can shape a decent result

Weaknesses:

- over-fragments more than the bare model:
  - `control-plane`
  - `http-host`
  - `proxy-core`
  - `route-resolution`
  - `data-plane`
  - `persistence-services`
- less elegant than either the bare-model atlas or the best Augur reference atlas

### Facts No Memory

Strengths:

- decent compression compared with `skill-no-facts`
- coherent two-narrative teaching set

Weaknesses:

- still not as strong as the best Augur reference shape
- only modest gain over the bare baseline

### Current Policy Reference

Strengths:

- best repo-native grouping:
  - `service-host`
  - `sip-edge`
  - `call-control`
  - `console-surface`
  - `addon-runtime`
- strongest child stories:
  - `sip-edge-routing`
  - `call-control-rwi`
  - `service-host-recording-state`
  - `service-host-addon-runtime`
- best teaching-oriented compression

Weaknesses:

- previous reference run still carried low state-grounding warnings

Verdict:

- `rustpbx` is the strongest challenge to Augur
- the bare model is very close
- Augur's advantage here is mostly taste, grouping, and repo-native shaping, not basic correctness

## jPOS

### Bare Model

Strengths:

- validator-clean: `0 warnings`
- finds the right broad subsystems:
  - `q2-runtime`
  - `iso-messaging`
  - `transaction-processing`
  - `state-spaces`
  - `cryptography`
- good three-narrative set

Weaknesses:

- clearly over-split at atlas level:
  - `qbean-lifecycle`
  - `runtime-ops`
  - `channel-transport`
  - `message-packaging`
  - `transaction-manager-core`
  - `transaction-participants`
  - `space-backends`
  - `name-registry`
  - `jce-security-module`
- reads more like a detailed subsystem taxonomy than a high-level architecture map

### Skill No Facts

Strengths:

- also strong and nearly clean
- slightly more disciplined grouping than bare-model

Weaknesses:

- still over-split
- atlas remains larger than necessary for teaching:
  - 14 components

### Facts No Memory

Strengths:

- surprisingly strong
- best compression of the four on raw component count:
  - `core-config`
  - `q2-runtime`
  - `iso-messaging`
  - `transaction-runtime`
  - `space-persistence`
  - `logging-observability`
- validator-clean

Weaknesses:

- risks being slightly too compressed
- can lose some of the distinct Q2 deployment and service-wiring structure that `current-policy` preserves

### Current Policy

Strengths:

- best balance between compression and explicit structure:
  - `q2-runtime`
  - `qbean-deployment`
  - `q2-iso-adaptors`
  - `iso-messaging`
  - `transaction-processing`
  - `shared-space`
  - `platform-services`
- cleaner teaching shape than the bare and skill-only lanes
- preserves more runtime semantics than the aggressively compressed facts-only lane

Weaknesses:

- the quality gap versus the stronger baselines is smaller than expected

Verdict:

- `current-policy` is best overall
- `facts-no-memory` is surprisingly competitive
- `bare-model` is good, but too taxonomy-shaped to be the best teaching artifact

## Cross-Repo Verdict

### What is clearly valuable

- schemas and explicit output contract
- validator + repair loop
- quality gate
- architectural shaping on harder repos

### What is under the most pressure

- broad semantic preload / memory

The current evidence does not yet show that heavy semantic preload is the main driver of quality on easier or mid-difficulty repos.

### Working hypothesis

Augur's value likely comes from:

1. strong workflow and repair discipline
2. deterministic shaping on hard repos
3. semantic preload only when repo difficulty or ambiguity justifies it

That suggests the product should likely become more conditional:

- lighter default lane on clean repos
- heavier Augur lane on large, broad, or ambiguous repos

