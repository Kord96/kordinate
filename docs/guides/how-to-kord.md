# How to Kord?

Adding the **designer** agent to the team — step by step using `/scribe:kord`.

## 1. Run the skill

```bash
/scribe:kord designer "reviews architecture and owns design patterns"
```

Scribe asks for anything missing:

- **Triggers?** → `review architecture`, `design review`, `check design consistency`
- **Exclusive tools?** → Gemini (design validation)
- **Consultation expertise?** → Component topology, design patterns, data flow, failure modes, dependencies

## 2. What gets created

```
agents/designer/
├── KORD.md                    # identity — role, triggers, commands, rules
├── instructions/
│   └── consultation.md         # what to answer when consulted, cache sources
├── memory/
│   ├── static/                 # domain knowledge (patterns/*.md, libraries/*.md)
│   └── dynamic/                # auto-managed notes
└── commands/
    └── detect-patterns.md      # /designer:detect-patterns skill
```

## 3. What gets updated

- **Root KORD.md** — designer added to the routing table and consultation directory
- **settings.json** — guard hook registered (if exclusive tools specified)
- **link-claude.sh** — run to register the new agent with the runtime

## 4. Customize

The generated files are starting points. For designer, we added:

- `memory/static/patterns/*.md` — 16 pattern definitions (circuit breaker, saga, etc.)
- `memory/static/libraries/*.md` — shared library docs (stoik, orchestrator, klog)
- `commands/detect-patterns.md` — skill that scans a project for recognized patterns

## Result

Designer is now part of the team:

| | |
|---|---|
| **Triggers** | `review architecture`, `design review`, `check design consistency` |
| **Authority** | Pattern definitions, architecture review |
| **Exclusive Tools** | Gemini (design validation) |
| **Commands** | `/designer:detect-patterns` |
| **Consults** | deployer (infrastructure reality), sauron (observability gaps) |
