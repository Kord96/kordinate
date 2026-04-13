# Shared Repo Profile

This directory contains deterministic repo-introspection utilities shared across the system.

The current purpose is to centralize early repo detection that multiple downstream tools depend on:

- dominant language
- secondary languages
- build system signals
- package manager signals
- likely frameworks

This runs before deeper detectors so later extractors can choose the right backend without rediscovering the same metadata repeatedly.

Current consumers:

- shared Joern runtime
- Augur fact extraction metadata

Primary entrypoint:

```bash
python3 shared/tools/repo_profile/detect_repo_profile.py /abs/path/to/repo --json
```
