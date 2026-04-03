---
name: publish-docs
description: >
  Publish augur's atlas output to the docs website. Copies atlas, stories, and
  journeys to the docs repo and wires the project into the home page navigation.
argument-hint: "<project-name>"
context: inherit
---

Publish a project's architecture documentation to the docs site.

## Arguments

`$ARGUMENTS` — Required: `<project-name>`. The project must have augur output at
`/kord/agents/augur/memory/projects/<project>/atlas.json`.

## Prerequisites

- Docs repo: `Kord96/kordinate-docs` (GitHub)
- Augur output exists: atlas.json + stories/ + journeys/

## Procedure

### Step 1 — Verify augur output

Check that these exist:
- `/kord/agents/augur/memory/projects/<project>/atlas.json`
- `/kord/agents/augur/memory/projects/<project>/stories/` (at least 1 file)

If missing, report: "No augur output for <project>. Run augur /analyze first."

Read atlas.json to extract:
- `purpose` — for the project card description
- `project` — project name

### Step 2 — Clone docs repo

```bash
git clone --depth 1 https://github.com/Kord96/kordinate-docs.git /tmp/docs-publish
cd /tmp/docs-publish
```

### Step 3 — Copy content

```bash
PROJECT_DIR="src/content/docs/<project>"
mkdir -p "$PROJECT_DIR/stories" "$PROJECT_DIR/journeys"

cp /kord/agents/augur/memory/projects/<project>/atlas.json "$PROJECT_DIR/"
cp /kord/agents/augur/memory/projects/<project>/stories/*.yaml "$PROJECT_DIR/stories/"
cp /kord/agents/augur/memory/projects/<project>/journeys/*.yaml "$PROJECT_DIR/journeys/" 2>/dev/null
```

If augur also produced `manifest.json` or `storyByNode.json`, copy those too.

### Step 4 — Wire to home page

Read `src/content/docs/index.mdx`. Check if a `<LinkCard>` for this project already exists.

If not, add one inside the `<CardGrid>` block:

```mdx
<LinkCard title="<Project Name>" description="<purpose from atlas>" href="/dev/<project>/" />
```

Capitalize the project name for the title. Use the `purpose` field from atlas.json as the description.

If the card already exists, update the description to match the current atlas purpose.

### Step 5 — Push

```bash
git add -A
git commit -m "docs: publish <project> architecture (atlas + stories)"
git push origin main
```

The docs site git-sync picks up the change within 3 seconds.

### Step 6 — Report

```
## Published: <project>

Docs site: https://docs.khaledkord.com/dev/<project>/
Content: atlas.json, N stories, N journeys
Home page: card added/updated

The docs site will reflect changes within 3 seconds.
```
