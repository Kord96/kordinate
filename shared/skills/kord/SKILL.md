---
name: kord
description: Discover and prompt daemon-backed agents through the central kord API.
---

# Kord

Use this skill whenever you need to:
- discover which daemon-backed agents exist
- choose the right agent for a task
- prompt one or more agents
- submit long-running agent work asynchronously and check back later

## What This Skill Does

`kord` is the single public surface for agent discovery and prompting.

It hides:
- stored API authentication
- discovery refresh and caching
- alias resolution
- request tracking for async work

It should be used instead of exposing:
- raw Kafka topics
- Kubernetes commands
- direct transport details
- ad hoc prompt envelopes

## Default Behavior

When using this skill:
- load stored auth automatically
- refresh discovery if the cached view is stale
- prefer exact agent names, but allow simple aliases when unambiguous
- use the compact discovery view by default
- use async mode only when the task is likely to take long enough that blocking is undesirable

## How To Use It

For discovery:
- ask `kord` to list available agents
- ask `kord` for verbose discovery only when transport or runtime debugging is needed

For prompting:
- ask `kord` to send a task to a named agent
- include a working directory when the task should focus on a particular repo or subtree

For long-running work:
- ask `kord` to submit the request asynchronously
- `kord` should return the request id and track the result through its local request state

## Discovery Shape

Default discovery should emphasize caller-facing routing information:
- `name`
- `capabilities`
- `backend_provider`
- `backend_model`
- `supported_agent_params`
- `active`

Verbose discovery may include:
- `specialization`
- `runtime`
- `health_url`
- `last_seen_at`
- `request_topic`
- `default_working_dir`

## Prompting Guidance

Use the discovered capabilities to choose the agent. Prefer:
- specialist agents for specialist tasks
- generic agents only when no specialist is a better fit

If a model alias is used, prefer the matching `generic-*` agent when one exists and there is no more specific exact match.

## Authentication

`kord` should authenticate once and reuse stored auth automatically. The user should not have to keep passing API keys during normal skill usage.

## Internal Note

The implementation currently lives behind the internal wrapper script:
- [kord](/kord/workstation/home/project/kordinate/shared/skills/kord/scripts/kord)

That script is implementation detail, not the intended user-facing contract.
