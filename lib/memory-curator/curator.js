#!/usr/bin/env node
// Memory Curator — consumes memory updates from Kafka, merges into shared files.
//
// One curator per agent type (replicas=1, strategy=Recreate).
// Has read-write access to /kord/agents/<name>/memory/.
//
// v1: Deterministic merge — batch updates per file over a 30s window,
// deduplicate against existing content, append new insights.
//
// v2 (future): Use Haiku for intelligent merge/prune/summarize.
//
// When memory files are added or removed, regenerates CLAUDE.md with
// updated @ imports.

import { Kafka } from 'kafkajs';
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { join, basename } from 'node:path';
import { execSync } from 'node:child_process';

// ─── Config ───

const AGENT_NAME = process.env.AGENT_NAME;
if (!AGENT_NAME) { console.error('AGENT_NAME required'); process.exit(1); }

const AGENT_DIR = process.env.AGENT_PROJECT_DIR || `/kord/agents/${AGENT_NAME}`;
const MEMORY_DIR = join(AGENT_DIR, 'memory');
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka-kafka-bootstrap.dev.svc.cluster.local:9092').split(',');
const BATCH_WINDOW_MS = 30_000; // 30s batch window
const POD_NAME = process.env.HOSTNAME || `curator-${AGENT_NAME}-local`;

// ─── State ───

// Pending updates: Map<filePath, [{ content, timestamp }]>
const pendingUpdates = new Map();
let batchTimer = null;

// ─── Logging ───

function log(level, event, data = {}) {
  console.log(JSON.stringify({
    level, component: 'curator', agent: AGENT_NAME,
    event, pod_name: POD_NAME,
    timestamp: new Date().toISOString(),
    ...data,
  }));
}

// ─── Merge logic ───

function extractLines(content) {
  return content.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0 && !line.startsWith('#') && !line.startsWith('---'));
}

function deduplicateAgainst(existing, newLines) {
  const existingSet = new Set(
    existing.split('\n').map(l => l.trim().toLowerCase())
  );
  return newLines.filter(line => !existingSet.has(line.toLowerCase()));
}

function mergeIntoFile(filePath, updates) {
  const absPath = filePath.startsWith('/') ? filePath : join(MEMORY_DIR, basename(filePath));

  // Ensure memory dir exists
  mkdirSync(MEMORY_DIR, { recursive: true });

  // Collect all new content
  const allContent = updates.map(u => u.content).join('\n');
  const newLines = extractLines(allContent);

  if (newLines.length === 0) {
    log('info', 'merge_skip_empty', { file: basename(absPath) });
    return false;
  }

  // Read existing content
  const existing = existsSync(absPath) ? readFileSync(absPath, 'utf8') : '';

  // Deduplicate
  const unique = deduplicateAgainst(existing, newLines);
  if (unique.length === 0) {
    log('info', 'merge_skip_duplicate', { file: basename(absPath), attempted: newLines.length });
    return false;
  }

  // Append with datestamp
  const datestamp = new Date().toISOString().split('T')[0];
  const section = `\n\n## ${datestamp}\n\n${unique.map(l => l.startsWith('- ') ? l : `- ${l}`).join('\n')}`;

  const header = existing || `# ${AGENT_NAME} — ${basename(absPath, '.md')}\n`;
  writeFileSync(absPath, header + section + '\n');

  log('info', 'merge_complete', {
    file: basename(absPath),
    new_lines: unique.length,
    total_attempted: newLines.length,
  });

  return true;
}

// ─── CLAUDE.md regeneration ───

function regenerateClaudeMd() {
  const imports = ['@identity.md'];

  // Shared files
  const sharedDir = join(AGENT_DIR, 'shared');
  if (existsSync(sharedDir)) {
    try {
      for (const f of readdirSync(sharedDir).filter(f => f.endsWith('.md')).sort()) {
        imports.push(`@shared/${f}`);
      }
    } catch {}
  }

  // Memory files
  if (existsSync(MEMORY_DIR)) {
    try {
      for (const f of readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md')).sort()) {
        if (f === 'MEMORY.md') continue;
        imports.push(`@memory/${f}`);
      }
    } catch {}
  }

  const claudeMdPath = join(AGENT_DIR, 'CLAUDE.md');
  const newContent = imports.join('\n') + '\n';

  // Only write if changed
  const existing = existsSync(claudeMdPath) ? readFileSync(claudeMdPath, 'utf8') : '';
  if (existing !== newContent) {
    writeFileSync(claudeMdPath, newContent);
    log('info', 'claude_md_regenerated', { imports: imports.length });
    return true;
  }
  return false;
}

// ─── Batch processing ───

function processBatch() {
  if (pendingUpdates.size === 0) return;

  log('info', 'batch_start', { files: pendingUpdates.size });

  let filesChanged = false;

  for (const [filePath, updates] of pendingUpdates) {
    try {
      const changed = mergeIntoFile(filePath, updates);
      if (changed) filesChanged = true;
    } catch (e) {
      log('error', 'merge_failed', { file: filePath, error: e.message });
    }
  }

  pendingUpdates.clear();

  // Regenerate CLAUDE.md if files were added
  if (filesChanged) {
    regenerateClaudeMd();
    gitCommit();
  }
}

function gitCommit() {
  try {
    const status = execSync('git status --porcelain', { cwd: AGENT_DIR, encoding: 'utf8' }).trim();
    if (!status) return;

    execSync('git add -A', { cwd: AGENT_DIR });
    execSync(`git commit -m "curator: merge memory updates for ${AGENT_NAME}"`, { cwd: AGENT_DIR });
    log('info', 'git_committed');
  } catch (e) {
    log('warn', 'git_commit_skipped', { error: e.message?.slice(0, 200) });
  }
}

function queueUpdate(filePath, content) {
  if (!pendingUpdates.has(filePath)) {
    pendingUpdates.set(filePath, []);
  }
  pendingUpdates.get(filePath).push({
    content,
    timestamp: new Date().toISOString(),
  });

  // Reset batch timer
  if (batchTimer) clearTimeout(batchTimer);
  batchTimer = setTimeout(processBatch, BATCH_WINDOW_MS);
}

// ─── Kafka ───

const kafka = new Kafka({
  clientId: `curator-${AGENT_NAME}-${POD_NAME}`,
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const consumer = kafka.consumer({ groupId: `curator-${AGENT_NAME}` });

async function main() {
  log('info', 'curator_boot', { agent: AGENT_NAME, memory_dir: MEMORY_DIR });

  // Ensure directories exist
  mkdirSync(MEMORY_DIR, { recursive: true });

  // Initial CLAUDE.md generation
  regenerateClaudeMd();

  await consumer.connect();
  await consumer.subscribe({ topic: `memory.updates.${AGENT_NAME}`, fromBeginning: false });

  log('info', 'kafka_ready', { topic: `memory.updates.${AGENT_NAME}` });

  await consumer.run({
    eachMessage: async ({ message }) => {
      try {
        const update = JSON.parse(message.value.toString());
        log('info', 'update_received', { path: update.path, content_length: update.content?.length });
        queueUpdate(update.path, update.content);
      } catch (e) {
        log('error', 'update_parse_failed', { error: e.message });
      }
    },
  });
}

async function shutdown() {
  log('info', 'curator_shutdown');
  // Process any remaining batch
  if (pendingUpdates.size > 0) processBatch();
  try { await consumer.disconnect(); } catch {}
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('error', 'curator_fatal', { error: e.message });
  process.exit(1);
});
