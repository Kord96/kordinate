## Deployment

Enforce replace-not-patch semantics and ensure images are versioned artifacts, never mutated in place.

### Rollout Implications

- Every deployment creates new instances from a versioned image -- never patch running instances
- Rollback means deploying the previous known-good image version, not reverting changes on live hosts
- Blue-green or canary strategies work naturally since each version is a distinct, immutable artifact
- Configuration is injected at startup (environment variables, mounted secrets), not baked into images

### Pre-deploy Checklist

- Verify image tags use commit SHA or semantic version, never `latest`
- Confirm no SSH access or remote exec is available in the production environment
- Validate that the image build is reproducible (pinned base images, locked dependency versions)
- Ensure rollback procedure references a specific previous image tag, not a manual revert process

