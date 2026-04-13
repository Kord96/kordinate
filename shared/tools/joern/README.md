# Shared Joern Runtime

This directory provides a standalone Joern runtime for experiments and shared static-analysis workflows.

It is intentionally **not** coupled to Augur. The goal is to let us:

- build one shared Joern image
- generate CPGs for arbitrary repos
- run ad hoc Joern queries or scripts
- inspect whether Joern adds enough value before integrating anything into Augur

## Layout

- `Dockerfile`
  - minimal Joern image
- `scripts/build-image.sh`
  - builds the shared image
- `scripts/generate-cpg.sh`
  - one-shot CPG generation for a local repo
- `export_call_edges.py`
  - emits normalized generic call-edge records as JSON
- `export_data_touches.py`
  - emits normalized generic data-touch records as JSON
- `export_execution_slices.py`
  - emits normalized generic execution-slice records as JSON
- `export_augur_facts.py`
  - emits the three Augur-facing Joern domains using one CPG build
- `scripts/run-script.sh`
  - run a Joern script against an existing CPG
- `scripts/run-shell.sh`
  - interactive shell inside the Joern image
- `workspace/`
  - local cache/output area for generated CPGs and copied scripts

## Design

This runtime is deliberately simple:

- no MCP wrapper
- no hardcoded security workflows
- no Augur-specific output contract
- no long-lived shared Joern server requirement

We use one shared Docker image and one-shot container executions with mounted volumes.
That keeps the runtime isolated and easy to remove if it does not prove useful.

## Prerequisites

- Docker with working daemon access
- enough disk for the Joern image and CPG artifacts
- enough memory for the repo/language being analyzed

Joern is heavy. Cold setup is expected to be expensive.

## Build

```bash
shared/tools/joern/scripts/build-image.sh
```

## Generate a CPG

```bash
shared/tools/joern/scripts/generate-cpg.sh /abs/path/to/repo go
```

This writes:

- `shared/tools/joern/workspace/cpgs/<repo>-<language>/cpg.bin`

The script prints the exact output path on success.

Supported language keys currently match Joern frontends wired here:

- `java`
- `c`
- `cpp`
- `javascript`
- `python`
- `go`
- `kotlin`
- `csharp`
- `ghidra`
- `jimple`
- `php`
- `ruby`
- `swift`

## Run an interactive shell

```bash
shared/tools/joern/scripts/run-shell.sh
```

## Run a Joern script against a CPG

```bash
shared/tools/joern/scripts/run-script.sh \
  shared/tools/joern/workspace/cpgs/my-repo-go/cpg.bin \
  /abs/path/to/query.sc
```

The script is copied into the container workspace before execution.

## Recommended evaluation path

Before integrating anything into Augur, compare:

1. current Augur outputs
2. Joern-derived evidence we can actually extract cheaply
3. runtime and storage cost

The likely first useful evidence types are:

- call/control edges
- data-touch or variable-flow evidence
- bounded execution slices

If those do not materially improve flow/journey/drift quality, this runtime should remain standalone.

## Export call edges

```bash
python3 shared/tools/joern/export_call_edges.py /abs/path/to/repo --output /tmp/call-edges.json
```

This emits a generic JSON payload:

- `version`
- `tool`
- `language`
- `root`
- `records[]`

Each record contains caller, callee, and callsite fields. It is intentionally not Augur-specific; Augur can normalize it into a fact domain without reading raw CPG structures directly.

## Export data touches

```bash
python3 shared/tools/joern/export_data_touches.py /abs/path/to/repo --output /tmp/data-touches.json
```

This emits normalized read, write, and emit-style touch records derived from Joern callsites.

## Export execution slices

```bash
python3 shared/tools/joern/export_execution_slices.py /abs/path/to/repo --output /tmp/execution-slices.json
```

This emits normalized ordered call slices per owner method, filtered to remove obvious operator noise.

## Export Augur fact domains in one run

```bash
python3 shared/tools/joern/export_augur_facts.py /abs/path/to/repo --output /tmp/joern-augur-facts.json
```

This builds one CPG and exports:
- `call-edges`
- `data-touches`
- `execution-slices`
