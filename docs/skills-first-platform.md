# Skills-First Platform Direction

Kordinate is pivoting away from a broad set of long-running platform agents.
The target shape is a smaller operational repo made of docs, scripts, and Codex
skills used by one main agent.

## Direction

- Absorb simple platform-agent responsibilities into Codex skills.
- Keep complex systems as their own repos when they have enough independent
  state, tests, runtime, and deployment needs.
- Treat Augur as the current example of a complex system that deserves its own
  boundary.
- Preserve Augur's useful pattern for future reuse: deterministic containerized
  execution separated from semantic agent reasoning.
- Stop designing new workflows around implicit shared Kubernetes mounts such as
  `/kord/shared` unless a surviving workload proves it needs one.

## Consequences

- Broken simple-agent pods are not automatically worth repairing.
- Missing provider secrets in dormant namespaces can stay dormant until the
  namespace is intentionally revived.
- Missing `/kord/shared` PVCs should be repaired only for surviving workloads.
- Charon and Alfred knowledge should be retained as skills, scripts, and docs
  where useful, not necessarily as always-on actors.
- Build/deploy automation remains valuable, but it should target the remaining
  containerized projects rather than preserve old agents for their own sake.

## Classification Rubric

Use this rubric for each current platform agent or responsibility.

`absorb into skill`:
- mostly procedural or advisory
- can run inside the main Codex session
- has no durable service state
- only needs repo files, shell commands, or connector access

`keep as project/repo`:
- has its own runtime or API
- has deterministic workers, queues, databases, or persistent state
- needs independent tests and deployment lifecycle
- is too large to be reliable as instructions alone

`retire`:
- duplicates a skill or script
- exists only to support the old multi-agent model
- has no active workflow owner
- is broken and not needed for the new target state

## Near-Term Checklist

- [ ] Inventory current agents and responsibilities.
- [ ] Classify each responsibility with the rubric above.
- [ ] Convert one simple responsibility into a Codex skill as a pilot.
- [ ] Retire or scale down one confirmed-unused workload through source control.
- [ ] Identify the minimum build/deploy workflow still needed for Augur and
      other containerized projects.
- [ ] Remove `/kord/shared` assumptions from new skills and scripts.
