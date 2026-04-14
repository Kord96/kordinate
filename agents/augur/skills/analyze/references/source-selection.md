# Source Selection

Use this reference when deterministic facts are not enough and semantic review needs targeted code reads.

## Read Order

Prefer this order:

1. package manifests and top-level README
2. runtime entrypoints and worker entrypoints
3. route and handler files
4. models, schemas, and migrations
5. config and deployment files
6. high-fan-in business logic
7. tests only when they clarify expected behavior

## Include

- primary source files for the detected languages
- package manifests and lock-adjacent manifests
- deployment and runtime config
- schema and IDL files
- top-level docs that explain runtime shape

## Exclude

- generated output
- vendored dependencies
- caches and build directories
- binaries, assets, and minified files
- large files unless they are clearly architecturally important

## Large Repos

- start from `facts/index.json`
- read only the domains relevant to the current question
- use targeted `rg`, `jq`, or small reads instead of full-file slurps
- avoid broad repo walks unless the blast slice or facts prove they are needed
