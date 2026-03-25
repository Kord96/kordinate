# Claude Code Session Structure

Internal reference — not referenced by SKILL.md.

Source: https://code.claude.com/docs/en/sub-agents

## Directory Layout

```
~/.claude/projects/<project>/
├── <session-id>.jsonl              # main agent transcript
├── <session-id>/
│   ├── subagents/
│   │   ├── agent-<id>.jsonl        # subagent transcript
│   │   └── agent-<id>.meta.json    # subagent metadata
│   └── tool-results/
├── <session-id>.jsonl              # another session
├── <session-id>/
│   └── subagents/
│       └── ...
└── memory/                         # auto memory (shared across all sessions)
    ├── MEMORY.md                   # index — first 200 lines auto-loaded
    └── *.md                        # topic files — read on-demand
```

## Key Facts

- `<project>` is derived from the git repo path (e.g. `-home-claude-kordinate`)
- Multiple sessions per project. Each session has its own transcript + subagent transcripts.
- Auto memory is the only thing shared across sessions.
- Transcripts are cleaned up after `cleanupPeriodDays` (default: 30 days).
- `/resume` reads the `.jsonl` file to restore a session.

## Transcript Format

Each line in a `.jsonl` file is a JSON event:

```json
{
  "parentUuid": "...",
  "type": "system|user|assistant",
  "subtype": "local_command|...",
  "content": "...",
  "timestamp": "2026-03-23T19:49:17.259Z",
  "uuid": "...",
  "sessionId": "...",
  "version": "2.1.78",
  "gitBranch": "main"
}
```

Event types include: user messages, assistant responses, tool calls, tool results, file history snapshots, system events.

## Subagent Transcripts

- Stored at `<session-id>/subagents/agent-<agentId>.jsonl`
- Persist independently of the main conversation
- Not affected by main conversation compaction
- Can be resumed by sending a message to the agent ID
