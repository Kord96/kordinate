#!/usr/bin/env node
// Memory Service — Cross-agent memory merge.
//
// Runs as a CronJob every 30 minutes. For each agent:
// 1. Reads all per-job scratchpads (scratchpad-<jobid>.md)
// 2. Appends unique insights to the main scratchpad.md
// 3. Deletes processed per-job files
// 4. Commits changes to git

import { readFileSync, writeFileSync, readdirSync, unlinkSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { execSync } from 'node:child_process';

const KORDINATE_HOME = process.env.KORDINATE_HOME || '/kord/kordinate';
const AGENTS_DIR = join(KORDINATE_HOME, 'agents');
const DRY_RUN = process.argv.includes('--dry-run');

function log(msg) {
  console.log(JSON.stringify({ level: 'info', component: 'memory-sync', event: msg, timestamp: new Date().toISOString() }));
}

function getAgentDirs() {
  try {
    return readdirSync(AGENTS_DIR, { withFileTypes: true })
      .filter(d => d.isDirectory() && existsSync(join(AGENTS_DIR, d.name, 'IDENTITY.md')))
      .map(d => d.name);
  } catch { return []; }
}

function getJobScratchpads(agent) {
  const memoryDir = join(AGENTS_DIR, agent, 'memory');
  if (!existsSync(memoryDir)) return [];
  return readdirSync(memoryDir)
    .filter(f => f.startsWith('scratchpad-') && f.endsWith('.md'))
    .map(f => join(memoryDir, f));
}

function extractInsights(content) {
  // Extract bullet points and non-empty lines as insights
  return content.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0 && !line.startsWith('#') && !line.startsWith('---'));
}

function readMainScratchpad(agent) {
  const path = join(AGENTS_DIR, agent, 'memory', 'scratchpad.md');
  if (!existsSync(path)) return '';
  return readFileSync(path, 'utf8');
}

function deduplicateInsights(existing, newInsights) {
  const existingSet = new Set(existing.split('\n').map(l => l.trim().toLowerCase()));
  return newInsights.filter(line => !existingSet.has(line.toLowerCase()));
}

function syncAgent(agent) {
  const jobFiles = getJobScratchpads(agent);
  if (jobFiles.length === 0) return 0;

  log(`Processing ${jobFiles.length} scratchpads for ${agent}`);

  // Collect all new insights from per-job scratchpads
  const allInsights = [];
  for (const file of jobFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const insights = extractInsights(content);
      allInsights.push(...insights);
    } catch (e) {
      log(`Failed to read ${file}: ${e.message}`);
    }
  }

  if (allInsights.length === 0) {
    // No useful content — just clean up files
    if (!DRY_RUN) {
      for (const file of jobFiles) {
        try { unlinkSync(file); } catch {}
      }
    }
    return 0;
  }

  // Deduplicate against existing scratchpad
  const existing = readMainScratchpad(agent);
  const uniqueInsights = deduplicateInsights(existing, allInsights);

  if (uniqueInsights.length === 0) {
    log(`No new unique insights for ${agent}`);
    if (!DRY_RUN) {
      for (const file of jobFiles) {
        try { unlinkSync(file); } catch {}
      }
    }
    return 0;
  }

  // Append to main scratchpad
  const scratchpadPath = join(AGENTS_DIR, agent, 'memory', 'scratchpad.md');
  const datestamp = new Date().toISOString().split('T')[0];
  const newSection = `\n\n## Merged ${datestamp}\n\n${uniqueInsights.map(l => l.startsWith('- ') ? l : `- ${l}`).join('\n')}`;

  if (DRY_RUN) {
    log(`[DRY RUN] Would append ${uniqueInsights.length} insights to ${scratchpadPath}`);
  } else {
    const current = existsSync(scratchpadPath) ? readFileSync(scratchpadPath, 'utf8') : `# ${agent} scratchpad\n`;
    writeFileSync(scratchpadPath, current + newSection + '\n');

    // Delete processed per-job files
    for (const file of jobFiles) {
      try { unlinkSync(file); } catch {}
    }
  }

  log(`Merged ${uniqueInsights.length} insights for ${agent}`);
  return uniqueInsights.length;
}

function gitCommit() {
  try {
    // Check for changes
    const status = execSync('git status --porcelain', { cwd: KORDINATE_HOME, encoding: 'utf8' }).trim();
    if (!status) {
      log('No changes to commit');
      return;
    }

    execSync('git add agents/*/memory/', { cwd: KORDINATE_HOME });
    execSync('git commit -m "memory-sync: merge per-job scratchpads"', { cwd: KORDINATE_HOME });
    log('Committed memory changes');
  } catch (e) {
    log(`Git commit failed: ${e.message}`);
  }
}

// ─── Main ───

function main() {
  log('Memory sync started');

  const agents = getAgentDirs();
  let totalMerged = 0;

  for (const agent of agents) {
    try {
      totalMerged += syncAgent(agent);
    } catch (e) {
      log(`Error syncing ${agent}: ${e.message}`);
    }
  }

  if (totalMerged > 0 && !DRY_RUN) {
    gitCommit();
  }

  log(`Memory sync complete: ${totalMerged} insights merged across ${agents.length} agents`);
}

main();
