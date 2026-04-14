# Platform Health Checklist

Run through this checklist to verify the current `kordinate` platform is healthy.

Use these result labels consistently:

- `PASS`: verified directly with current evidence.
- `WARN`: partially verified, degraded, stale, or dependent on a known exception.
- `FAIL`: incorrect, missing, or contradicted by current evidence.

For every section, record:

- the command, API call, or MCP tool used
- the exact deployment or logical agent tested
- the concrete evidence that justified the result

Do not mark a section `PASS` based on stale assumptions, old screenshots, or generated files alone when the live cluster can be checked directly.

## Source Of Truth

- `main` is up to date locally and on origin.
- Generated platform artifacts match source:
  - [agent-spec.yaml](/kord/workstation/home/project/kordinate/agents/charon/skills/platform/agent-spec.yaml)
  - [agents.yaml](/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base/agents.yaml)
  - [keda.yaml](/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base/keda.yaml)
  - [kafka-topics.yaml](/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base/kafka-topics.yaml)
  - [discovery-catalog.json](/kord/workstation/home/project/kordinate/agents/charon/skills/platform/manifests/base/discovery-catalog.json)
- Rendered manifests contain no unresolved `REGISTRY/` placeholders.
- Generated manifests were not patched manually after render without the same change being reflected back into source.

## Persistent Storage

### Shared Runtime PVC

- `/kord/shared/memory/` exists and is writable by running agent pods.
- Alfred shared pass store exists at `/kord/alfred/pass`.
- Alfred shared GPG home exists at `/kord/alfred/gnupg`.
- Agent state directories exist for live deployments under `/kord/<deployment-name>/`.

### Repo/Data Mounts

- Shared repo mount exists and is readable from agent pods.
- Running pods can read project files from the shared repo path.
- Agent pods cannot write to the shared repo mount if it is intended to be read-only.

## Kubernetes Resources

### Secrets

- Required provider secrets exist in the target namespace with key `api-key`.
- `validate-provider-secrets.py --probe-provider` passes for all deployed agents.
- Secret rotation path is verified for at least one provider-backed deployment.
- A failed provider probe is treated as a blocking `FAIL`, not as a runtime issue to debug later.

### Operators And Core Services

- KEDA operator is healthy.
- Kafka operator and broker are healthy.
- `kord-api` is healthy and reachable.

## Platform Inventory

### Request Topics

- Kafka request topics exist for all currently deployed agents:
  - `generic-opus`
  - `augur-opus`
  - `augur-gpt54`
  - `augur-gemini-31-pro`
  - `augur-deepseek-reasoner`
  - `augur-glm5`
  - `charon-gpt53-codex`
  - `sauron-gpt53-codex`
  - `alfred-deepseek-chat`
  - `alfred-gpt-oss-20b`
- Memory update topics exist for the same deployments.
- `agent.dlq` exists.
- Topic partition counts match the intended scaling strategy for each deployment.

### Deployments And ScaledObjects

- Expected Deployments exist and become ready.
- Expected Services exist for active deployments.
- Expected ScaledObjects exist and point to the right topic and consumer group.
- Removed agents are actually gone from Deployments, Services, ScaledObjects, and Kafka topics.

## Discovery And Routing

- `kord-api` discovery returns the current logical agents and variants.
- Removed or renamed variants do not persist in discovery longer than the configured TTL.
- Logical routing resolves to the expected default variant.
- Explicit variant routing works for renamed variants:
  - `augur-gemini-31-pro`
  - `sauron-gpt53-codex`
- Legacy compatibility names only work when intentionally supported.
- Discovery metadata is consistent with live runtime facts:
  - `backend_provider`
  - `backend_model`
  - `runtime`
  - `active`

## Runtime Correctness

- Running pods pass `/health` on port `9090`.
- `klaude-daemon` starts with the expected runtime, provider, and model.
- Each pod receives:
  - `DAEMON_WORKING_DIRECTORY`
  - `DAEMON_STATE_DIR`
  - `DAEMON_SESSION_MAP_PATH`
- No pod attempts to create relative `.daemon-state` or `.daemon-logs` paths under `/app`.
- Claude SDK resume path recovers cleanly from stale session IDs.

## End-To-End Request Flow

- A simple request succeeds for each active logical service or explicit variant that should be live.
- Response contains:
  - `status`
  - `output`
  - matching `correlation_id`
- Error responses preserve actionable runtime details.
- normalized request summary/transcript should explain the path from request receipt to response publication.
- Request-scoped logs can distinguish:
  - queue wait
  - consumer assignment delay
  - runtime execution time
  - reply publication time

### Minimum E2E Matrix

- `alfred`
  - store a non-sensitive test secret
  - retrieve the same secret
- `charon`
  - perform a harmless live platform inspection
- `augur`
  - run one logical-agent request
  - run one explicit-variant request
- `generic`
  - run one prompt through the default generic deployment

Treat any request that succeeds only after the caller timeout as `WARN` or `FAIL`, not `PASS`.

## Scaling And Queueing

- A single warm pod processes one request correctly.
- Concurrent requests create Kafka lag and trigger KEDA scale-up when configured to do so.
- Scale-up stops at `maxReplicaCount`.
- Requests beyond max replicas remain queued in Kafka rather than being dropped.
- Once one pod finishes, it consumes the next queued request automatically.
- Scale-down returns to the configured minimum after cooldown.
- Partition count is appropriate for the configured `maxReplicaCount`.

### Required Scaling Exercise

- Pick one deployment that is allowed to scale above `1`.
- Submit enough concurrent work to force lag above the KEDA threshold.
- Verify:
  - initial replica count
  - peak replica count
  - time to first scale-up
  - whether queued work drains after workers finish
- Record whether throughput is actually improved by extra replicas or limited by partition count.

Do not mark this section `PASS` without a live burst test.

## Rebalance Behavior

- Consumer-group rebalances cause temporary delay only, not silent request loss.
- No duplicate processing is observed during pod churn or rollout.
- Reply correlation remains correct during and after rebalances.
- API timeout vs late reply is visible in logs and E2E traces.

### Rebalance Triggers To Exercise

- pod start
- pod restart
- rolling deployment rollout
- scale up
- scale down

For at least one trigger, capture a request that overlaps the rebalance and verify whether it:

- completed in time
- completed late
- timed out but replied later
- was lost or duplicated

## Rollout Safety

- Rolling restart of an active deployment does not lose queued work.
- Renamed deployments come up before old ones are removed, when applicable.
- Registry/discovery converges to the new deployment names after rollout.
- Old services and stale discovery state are cleaned up after renames/removals.
- Topic, service, and discovery cleanup is verified after deletion of a deployment, not just after rename.

## Shared Skills And Ownership

- Shared `validate-output` skill is present and callable.
- Shared `sanitize` skill is present and callable.
- No live workflow still depends on the removed Warden agent.
- Ownership policy reflects the current shared skill layout and no longer assigns removed domains to Warden.

## Suggested Evidence Sources

- `mcp__kord__list_agents`
- `mcp__kord__get_agent`
- `mcp__kord__delegate`
- `mcp__kord__resume_request`
- raw event/log tools only when debugging transport failures
- `kubectl get deploy,svc,scaledobject,secret,kafkatopic -n kord`
- provider secret probe script
- direct health checks against `/health`
