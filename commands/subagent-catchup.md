Catch up on parent context and code changes since your last invocation.

Native `memory: user` handles persistent memory automatically. This command catches up on parent session context and code changes only.

## Steps

1. Read your local state from `.claude/agent-state/<your-name>.json` (if it exists). This contains `session_id`, `last_line`, `last_commit`, `last_changelog_line`, and `context_summary`. If the file doesn't exist, start fresh: `last_line=0`, `last_commit=""`, `last_changelog_line=0`.

2. **Find the parent session JSONL**:
   - List files in the `.claude/projects/` directory corresponding to the repo root path, matching `*.jsonl` (exclude agent-* files)
   - Sort by modification time, pick the most recently modified — this is the active master session
   - If the filename differs from your stored `session_id`, this is a new session — reset `last_line` to 0

3. **Read the parent delta AND code changes in parallel** (these are independent — run both at once):

   a. **Parent delta**: Read the parent JSONL starting from line `last_line`
      - Filter for lines where `"type":"user"` or `"type":"assistant"` — skip progress, system, file-history-snapshot lines
      - This is your delta — the new parent conversation since your last catchup

   b. **Code changes** (at the same time): If `last_commit` is set: `git diff <last_commit>..HEAD --stat` for an overview, then `git diff <last_commit>..HEAD` filtered for files relevant to your domain. If `last_commit` is empty: skip (first run)

4. **Check changelog**: Read `agents/changelog.md` starting from line `last_changelog_line`. Note any new entries from other agents that affect your domain.

5. **Summarize through your lens**:
   - If the delta is **under 50 lines**: summarize it yourself directly based on your specialty and focus areas from your CLAUDE.md
   - If the delta is **50 lines or more**: send the delta to Gemini MCP with the prompt: "I am the <your-name> agent. My focus is <your specialty from CLAUDE.md>. Summarize the following parent conversation changes and code diff from my perspective. Focus on decisions, state changes, and anything I need to know for my domain."
   - Combine the parent context summary with any relevant code change notes
   - **Keep summaries concise** (5-10 lines max). Focus on: decisions made, current state of things you care about, and open questions. Drop historical play-by-play — the changelog has that.

6. **Save local state** — write `.claude/agent-state/<your-name>.json` directly via Bash:
   ```json
   {
     "session_id": "<current session filename>",
     "last_line": <current end of JSONL>,
     "last_commit": "<current HEAD>",
     "last_changelog_line": <current end of changelog>,
     "context_summary": "<your new summary>"
   }
   ```

7. **Project knowledge provisioning** — check if this agent has required project knowledge files:
   - Read `~/.claude/agents/<your-name>/knowledge/manifest.yaml` (if it exists)
   - If it has a `project_files` list, determine the current project name from the repo's directory name
   - For each file in `project_files`, check if `~/.claude/agents/<your-name>/knowledge/projects/<project>/<file>` exists
   - If any files are missing, consult scribe: `/consult scribe "I need project knowledge templates for <your-name>. Missing files: <list>. Please return the template content for each."`
   - Use the returned templates as a checklist — scan the project codebase to gather the required data
   - Tell scribe to write each file with the gathered content
   - If manifest.yaml doesn't exist, skip this step

8. **Proceed with your assigned task.**
