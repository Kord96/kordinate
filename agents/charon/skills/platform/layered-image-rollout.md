# Layered Image Rollout

Use this when rolling the daemon-backed platform after image contract changes.

## Goal

Ensure `agent-base` carries the shared `klaude-daemon` binary and that specialist images layer cleanly on top of it.

## Images

- `agent-base`
  - copies the repo to `/app`
  - installs and builds `shared/klaude-daemon`
  - globally installs the `klaude-daemon` binary into the image
- `agent-charon`
  - derives from `agent-base`
- `agent-augur`
  - derives from `agent-base`
- `agent-alfred`
  - derives from `agent-base`
- `agent-sauron`
  - derives from `agent-base`

## Rollout Order

1. Build and verify `agent-base`
2. Build and verify specialist images that derive from it
3. Regenerate platform manifests if the runtime contract changed
4. Deploy with `/platform deploy <env>` or:

```bash
bash lib/scripts/apply-platform-manifests.sh <env> shared/runtime/profile/overlays/platform/<env>
```

## Local Docker Path

When Docker is available, prefer:

```bash
lib/scripts/build-agent-images.sh <registry-host> --verify-local
```

This verifies each built image contains `klaude-daemon` before pushing.

For targeted image refreshes after the platform is already healthy, prefer:

```bash
lib/scripts/build-agent-images.sh <registry-host> --image agent-augur --tag <timestamp> --verify-local
python3 lib/scripts/roll-platform-image.py agent-augur <registry-host> <timestamp> --env <env>
```

This keeps image ownership in the Charon/platform path instead of ad hoc deployment patching.

## Verification

- `kubectl exec` into an agent pod and confirm `which klaude-daemon`
- confirm `/app/shared/klaude-daemon/dist/index.js` exists
- confirm the deployment command is `exec klaude-daemon`
- confirm the agent responds on its Kafka request topic
