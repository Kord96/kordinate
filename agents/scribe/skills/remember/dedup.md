# Dedup Procedure

Level 3 resource for the remember skill. Prevents duplicate memory files.

Before creating a new topic file, scan existing memory descriptions for duplicates. This step runs after sanitize (step 1) and before scope determination (step 3).

## Procedure

1. **Read existing descriptions** — read the frontmatter `description` from all existing memory files in the target agent's memory directory. Check both global (`$KORDINATE_HOME/agents/<name>/memory/`) and project (`.kord/agents/<name>/memory/`) scope directories as applicable.

2. **Compare** — compare the new memory's intended description against every existing description.

3. **Decision matrix**:
    - **Exact match** — update the existing file instead of creating a new one. Append or merge the new content into the existing file's body. Preserve the existing frontmatter (update `description` only if the new content meaningfully expands the scope).
    - **Near match** — warn the caller with the existing file path and description. Ask: "Update existing `<filename>` or create new file?" Wait for response before proceeding.
    - **No match** — proceed to step 3 (scope determination) normally.

4. **Scratchpad appends** — skip dedup entirely. Scratchpads accumulate by design and are not subject to duplicate detection.

## Near match heuristic

Use LLM judgment, not scripted string comparison. Guidelines:

- **Same noun phrase** — 2+ word overlap excluding stop words (`the`, `a`, `an`, `is`, `are`, `for`, `of`, `in`, `to`, `and`, `or`).
- **Substring relationship** — one description contains the other as a substring.
- **Semantic similarity** — descriptions refer to the same concept with different wording.

## Examples

| New description | Existing description | Verdict |
|-----------------|---------------------|---------|
| "Deployer tools reference" | "Deployer tools reference -- postgres.py" | Exact match (substring) |
| "Infrastructure cluster setup" | "Cluster infrastructure and setup" | Near match (same nouns) |
| "Grafana dashboard conventions" | "Prometheus alerting rules" | No match |
| "Sauron workflow and validation" | "Sauron workflow -- understand, implement, validate, report" | Exact match (substring) |
| "Kubernetes networking overview" | "K8s network policies" | Near match (semantic) |
