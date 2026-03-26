---
description: Immutable Infrastructure architectural pattern
curated: true
scope: global
preloaded: none
---
# Immutable Infrastructure

## Recognition

How to identify this pattern in code.

### Signatures

- Dockerfiles building application images with all dependencies baked in
- Packer templates (`.pkr.hcl`, `packer.json`) producing machine images (AMIs, GCE images)
- No SSH-based configuration management (no Ansible playbooks running against live servers)
- Image tags pinned to specific versions or commit SHAs, not `latest`
- Replace-not-patch deployment strategy (terminate old instances, launch new ones)
- No in-place update scripts or hot-patching mechanisms in production

### Confidence

- **high** -- image build pipeline producing versioned artifacts, deployments always replace instances with new images, no remote shell access
- **medium** -- containerized deployments with immutable image tags but occasional `kubectl exec` for debugging
- **low** -- Docker images are built but `latest` tags are used or containers are patched in place

## Architecture

Look for a build-once-deploy-everywhere pipeline where running instances are never modified after creation.

### Review Checklist

- Images are versioned with immutable tags (commit SHA or semantic version, never `latest`)
- No mechanism exists to modify running instances (no SSH, no remote exec in production)
- Configuration is injected at startup via environment variables or mounted config, not baked into the image
- Rollback means deploying a previous known-good image version, not reverting changes on a live instance
- Image build is reproducible (pinned base images, locked dependency versions)

### Anti-patterns

- Using `latest` tag allowing the same tag to reference different image contents
- SSH access to production instances for ad-hoc patching or configuration changes
- Baking environment-specific secrets or configuration into the image itself
- In-place updates via `kubectl exec` or remote script execution on running containers
