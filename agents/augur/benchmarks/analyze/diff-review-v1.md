# Delta And Contradiction Review v1

This review compares completed ablation lanes by concrete issue classes rather than validator cleanliness alone.

Issue classes used here:

- `over_split`: lane promotes too many local or subordinate concerns into atlas components
- `under_split`: lane collapses distinct runtime slices too aggressively
- `generic_naming`: architecture uses broad role names instead of repo-native terms
- `missed_cross_cutting_root`: lane leaves an important shared subsystem subordinate when it should be promoted
- `root_heavy_narrative`: narratives stay too broad instead of using the most useful child stories
- `story_not_architectural`: story looks like a local code cluster or feature stub rather than a durable architecture unit
- `atlas_story_tension`: atlas shape and story emphasis point at different architecture

## MatrixOne

### Bare Model

Observed shape:

- 10 atlas components
- roots include `service-bootstrap`, `compute-node`, `transaction-node`, `log-service`, `access-proxy`

Likely issues:

- `generic_naming`
  - `compute-node`, `transaction-node`, `log-service` are broadly correct but not repo-native
- `missed_cross_cutting_root`
  - `file-services` stays subordinate instead of being promoted as a true cross-cutting root
- `under_split`
  - CN/TN internals are flattened into broad generic roots

Strengths:

- strong overall backbone
- narratives are coherent

### Skill No Facts

Observed shape:

- 13 atlas components
- includes `cluster-runtime`, `query-compute`, `transaction-storage`, `log-coordination`, `hakeeper-control-loop`

Likely issues:

- mild `over_split`
  - `service-launcher`, `raft-log-store`, `txn-rpc-layer` read more local than the strongest final atlas
- mild `generic_naming`
  - still broader than repo-native current-policy naming

Strengths:

- better than bare-model at surfacing control-plane/runtime structure
- shows workflow + validator can shape architecture substantially

### Facts No Memory

Observed shape:

- 10 atlas components
- includes `mo-service-runtime`, `dynamic-cn-control`, `cn-service`, `tn-service`, `file-service`, `file-cache-layer`

Likely issues:

- mild `over_split`
  - `cn-service`, `cn-pipeline-rpc`, `tn-memorytable`, `file-cache-layer`
- mild `atlas_story_tension`
  - facts encourage deeper decomposition, but final grouping is less coherent than current-policy

Strengths:

- strong deterministic surfacing of deep runtime/storage slices
- much more repo-native than bare-model

### Current Policy

Observed shape:

- 11 atlas components
- `service-runtime`, `dynamic-cluster-controller`, `cn-query-runtime`, `sql-frontend`, `execution-engine`, `transaction-storage`, `txn-service`, `log-ha-coordination`, `logservice-store`, `file-service`, `cache-layer`

Verdict:

- best overall balance
- best on:
  - repo-native naming
  - promotion of cross-cutting roots
  - narrative specificity

Main takeaway:

- MatrixOne is still the clearest case where Augur adds real architecture value, not just cleanup.

## RustPBX

### Bare Model

Observed shape:

- 11 atlas components
- `application-host`, `sip-proxy`, `control-surfaces`, `recording-storage`
- also `addon-registry`, `shared-storage`, `call-record-pipeline`, `sipflow-capture`

Likely issues:

- `over_split`
  - `addon-registry`, `shared-storage`, `call-record-pipeline`, `sipflow-capture`
- mild `atlas_story_tension`
  - stories are teaching-oriented, atlas is more like a subsystem inventory

Strengths:

- very strong first-principles result
- narratives are practical and specific

### Skill No Facts

Observed shape:

- 13 atlas components
- `control-plane`, `http-host`, `proxy-core`, `route-resolution`, `data-plane`, `persistence-services`

Likely issues:

- strong `over_split`
- `generic_naming`
  - `control-plane`, `data-plane`, `app-execution`
- some `story_not_architectural`
  - several stories feel more like local execution paths than durable architecture units

Strengths:

- still coherent
- validator/repair core is clearly useful

### Facts No Memory

Observed shape:

- 9 atlas components
- `web-control-plane`, `rwi-control-api`, `sip-call-plane`, `call-automation`, `data-recording-plane`

Likely issues:

- mild `generic_naming`
- mild `under_split`
  - compresses some UI/control/runtime distinctions into a smaller number of plane-style buckets

Strengths:

- cleaner than `skill-no-facts`
- good narrative compression

### Current Policy

Observed shape:

- 12 atlas components
- `application-host`, `call-processing-core`, `sip-routing-engine`, `session-command-runtime`, `rwi-control-plane`, `media-and-data-services`, `media-fabric`, `call-record-pipeline`, `persistence-backends`, `admin-and-addons`, `console-surface`, `addon-platform`

Likely issues:

- mild `over_split`
  - `admin-and-addons`, `console-surface`, `addon-platform` may be one layer more explicit than necessary

Strengths:

- best repo-native grouping
- best separation of control/runtime/media/persistence concerns
- strongest story set

Main takeaway:

- RustPBX is the strongest challenge to Augur.
- The bare-model lane is already very strong.
- Augur’s margin here is mostly architecture taste and grouping, not baseline correctness.

## jPOS

### Bare Model

Observed shape:

- 14 atlas components
- `q2-runtime`, `iso-messaging`, `transaction-processing`, `state-spaces`, `cryptography`
- plus many narrow subordinate slices

Likely issues:

- strong `over_split`
  - `qbean-lifecycle`, `runtime-ops`, `channel-transport`, `message-packaging`, `transaction-manager-core`, `transaction-participants`, `space-backends`, `name-registry`, `jce-security-module`
- mild `story_not_architectural`
  - some stories resemble capability buckets more than architecture units

Strengths:

- broad coverage
- good runtime intuition

### Skill No Facts

Observed shape:

- 14 atlas components
- `q2-deployer`, `q2-service-factory`, `mux-routing`, `packager-model`, `runtime-services`, `space-backplane`, `security-services`, `logging-metrics`

Likely issues:

- `over_split`
- mild `generic_naming`
  - `runtime-services`, `security-services`, `logging-metrics`

Strengths:

- better runtime emphasis than bare-model
- keeps Q2/ISO/transaction/space architecture coherent

### Facts No Memory

Observed shape:

- 6 atlas components
- `core-config`, `q2-runtime`, `iso-messaging`, `transaction-runtime`, `space-persistence`, `logging-observability`

Likely issues:

- `under_split`
  - compresses runtime/service distinctions aggressively
- mild `missed_cross_cutting_root`
  - configuration and runtime service wiring are compacted into `core-config`

Strengths:

- cleanest compression
- strong teaching simplicity

### Current Policy

Observed shape:

- 7 atlas components
- `q2-runtime`, `qbean-deployment`, `q2-iso-adaptors`, `iso-messaging`, `transaction-processing`, `shared-space`, `platform-services`

Strengths:

- best balance between compression and explicit runtime structure
- better than bare-model on reducing taxonomy drift
- better than facts-only on preserving Q2-specific deployment semantics

Main takeaway:

- Current-policy wins, but by less than expected.
- Facts-plus-structure is surprisingly competitive.

## CNSpec

This repo is useful because it separates raw model, schemas, validator, deterministic facts, and full current policy more cleanly.

### Raw Model

Observed shape:

- no validator, no schemas, no repair
- output organized as numbered stories:
  - `product-shape`
  - `scan-pipeline`
  - `policy-and-framework-model`
  - `reporting-surface`
  - `vuln-and-sbom`
  - `content-docs-tests`

Likely issues:

- `generic_naming`
- `story_not_architectural`
  - story set includes `content-docs-tests`, which is not a strong architecture unit
- likely `under_split` on deep runtime/policy mechanisms

Strengths:

- very fast
- useful repo map floor

### Schemas Only

Observed shape:

- 13 atlas components
- includes `cli-surface`, `policy-bundle-system`, `bundle-loader`, `bundle-linter`, `scan-runtime`, `disk-queue`, `report-output-handler`, `sbom-generator`, `packaged-content`

Likely issues:

- strong `over_split`
- some `story_not_architectural`
  - `bundle-linter`, `report-output-handler`, `packaged-content`

Strengths:

- schemas clearly add structure even without validation

### Schemas Plus Validator

Observed shape:

- 13 atlas components
- still broad and explicit

Likely issues:

- `over_split`
- `atlas_story_tension`
  - validator cleanliness does not eliminate the sense that several components are really implementation slices

Strengths:

- validator/repair can make a very clean result even without facts

### Facts Plus Validator

Observed shape:

- 5 atlas components
- `apps-cnspec`, `policy-runtime`, `scan-results-store`, `cli-reporting`, `onboarding-automation`

Likely issues:

- mild `under_split`
  - may compress command/runtime distinctions too aggressively
- mild `generic_naming`
  - `apps-cnspec` and `cli-reporting` are broad but still somewhat surface-oriented

Strengths:

- strongest compression of the non-current lanes
- surprisingly competitive

### Current Policy

Observed shape:

- 8 atlas components
- `command-runtime`, `background-scan-service`, `scan-api-endpoint`, `policy-engine`, `data-lake-backends`, `report-rendering`, `sbom-export`, `onboarding-tooling`

Strengths:

- best balance between CLI glue and deeper runtime slices
- best on avoiding both taxonomy explosion and over-compression
- strongest story tree

Main takeaway:

- validator/repair is again the big step up
- facts + validator is strong, but current-policy still has the best architecture balance

## Overall

### What seems genuinely valuable

- schemas
- validator and repair loop
- quality gate
- architecture shaping on harder repos

### Where the product still has pressure

- semantic preload must justify itself more clearly
- on easier repos, current-policy often wins by taste and grouping rather than obvious structural superiority

### Best current evaluation method

Compare lanes by:

- `over_split`
- `under_split`
- `generic_naming`
- `missed_cross_cutting_root`
- `story_not_architectural`
- `atlas_story_tension`

This is more informative than warning counts alone, because many lanes now validate cleanly.

