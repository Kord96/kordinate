# Consultation

## Cache Sources

Directories to hash for cache invalidation — if any change, cached answers are stale:

- `instructions/`
- `memory/static/`
- `memory/dynamic/`

When consulted, answer about:
- Component topology — processes, what they do, how they connect
- Design patterns — which framework each component uses
- Pattern perspectives — read from `patterns/<pattern>.md`, return the requested section (Architecture, Monitoring, Deployment, Testing)
- Data flow — how data moves through the system
- Failure modes — what can go wrong and the blast radius
- Dependencies — what each component depends on

## How to answer

1. For pattern perspectives: read `patterns/<pattern>.md`, return the requested section
2. For project questions: look for `docs/architecture.md` in that project
3. If no architecture doc: scan project source to infer architecture
4. Answer concisely — the caller needs facts, not explanations
5. Keep responses under 50 lines
