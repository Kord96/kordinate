# Augur Pilot Execution Matrix

Execution plan for the first curated pilot set.

Pilot set source:

- `references/augur-pilot-repo-set-v1.json`

## Goal

Measure:

- quality differences across bundle combinations
- runtime and token tradeoffs
- whether bundle benefits depend on repo type

## Matrix

For Augur, run the full `2x2` matrix:

- `selective memory + selective skill`
- `selective memory + holistic skill`
- `holistic memory + selective skill`
- `holistic memory + holistic skill`

Use one run each on all pilot repos for the first pass.

## Pilot Repos

Use the 12 repos in `augur-pilot-repo-set-v1.json`.

## Phase 1

Run Augur only:

- all 12 repos
- all 4 bundle combinations
- `1` run each

Total runs: `48`

Purpose:

- establish baseline quality and cost by bundle
- verify manifests, reflections, scoring, and labels work

## Phase 2

Select a smaller separation subset:

- `microsoft/vscode`
- `temporalio/temporal`
- `sqlite/sqlite`
- `Wox-launcher/Wox`

Run repeated Augur trials:

- same 4 bundle combinations
- `3` runs each

Total repeated runs: `48`

Purpose:

- estimate variance
- see whether bundle rankings are stable

## Phase 3

Run one comparison model on the same 12 pilot repos.

Recommended first comparison set:

- best `1-2` Augur bundle configurations from Phase 1
- `1` comparison model configuration

Purpose:

- get early head-to-head signal without exploding cost

## Outputs Per Run

Each run should produce:

- run manifest
- raw outputs
- validation result
- score result
- raw reflection record

## Aggregate Outputs

After each phase, produce:

- bundle comparison summary
- runtime and token summary
- reflection summary
- shortlist of likely best bundle settings

## Exit Criteria

Do not scale to the larger curated set until:

- manifests are complete and stable
- reflection records are being written reliably
- labels are sufficient for at least 10 of 12 repos
- bundle differences are interpretable rather than noisy
- the scoring process surfaces useful failures instead of mostly ambiguous cases
