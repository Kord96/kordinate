#!/usr/bin/env node
// Agent Scribe — consumes memory updates from Kafka, deduplicates via
// Haiku, routes to global or project-scoped agent memory.
//
// One scribe per agent type (replicas=1, strategy=Recreate).
//
// Global memory:  /kord/<name>/memory/global/
// Project memory: /kord/<name>/memory/projects/<project>/
//
// Agents classify their own updates as global or project-scoped.
// Haiku handles deduplication only — semantic comparison against existing
// memory to prevent redundant entries.
//
// Regenerates the agent's CLAUDE.md with updated @ imports when global
// memory files change. Project memory is loaded per-job via the daemon,
// not via CLAUDE.md.

import { Kafka } from 'kafkajs';
import Anthropic from '@anthropic-ai/sdk';
import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { join, basename } from 'node:path';

// ─── Config ───

const AGENT_NAME = process.env.AGENT_NAME;
if (!AGENT_NAME) { console.error('AGENT_NAME required'); process.exit(1); }

const AGENT_DIR = process.env.AGENT_STATE_DIR || `/kord/${AGENT_NAME}`;
const MEMORY_DIR = join(AGENT_DIR, 'memory');
const GLOBAL_DIR = join(MEMORY_DIR, 'global');
const PROJECTS_DIR = join(MEMORY_DIR, 'projects');
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka-kafka-bootstrap.dev.svc.cluster.local:9092').split(',');
const BATCH_WINDOW_MS = 30_000;
const POD_NAME = process.env.HOSTNAME || `scribe-${AGENT_NAME}-local`;

// ─── Anthropic client ───

const anthropic = new Anthropic();

// ─── State ───

// Pending updates: Map<key, { path, content, project, scope, timestamp }[]>
const pendingUpdates = new Map();
let batchTimer = null;

// ─── Logging ───

function log(level, event, data = {}) {
  console.log(JSON.stringify({
    level, component: 'scribe', agent: AGENT_NAME,
    event, pod_name: POD_NAME,
    timestamp: new Date().toISOString(),
    ...data,
  }));
}

// ─── Haiku deduplication ───

async function deduplicateWithHaiku(newContent, existingContent) {
  if (!existingContent.trim()) return newContent;

  try {
    const response = await anthropic.messages.create({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 2048,
      messages: [{
        role: 'user',
        content: `You are a memory deduplication filter. Compare new entries against existing memory and return ONLY the entries that are genuinely new information.

## Existing memory
${existingContent}

## New entries to check
${newContent}

Return ONLY the new entries that are NOT already captured in existing memory — even if worded differently. If an existing entry already conveys the same insight, drop the new one. Return one entry per line, each starting with "- ". If everything is a duplicate, return exactly "NONE".`,
      }],
    });

    const answer = response.content[0].text.trim();
    if (answer === 'NONE') return '';
    return answer;
  } catch (e) {
    log('error', 'dedup_failed', { error: e.message, fallback: 'append_all' });
    return newContent;
  }
}

// ─── Path helpers ───

function targetDir(scope, project) {
  if (scope === 'global') return GLOBAL_DIR;
  if (scope === 'project' && !project) {
    log('warn', 'project_scope_no_project', { fallback: 'dropped' });
    return null; // caller should skip this update
  }
  return join(PROJECTS_DIR, project);
}

// ─── Merge logic ───

async function mergeIntoFile(absPath, updates) {
  mkdirSync(join(absPath, '..'), { recursive: true });

  const newContent = updates
    .map(u => u.content)
    .join('\n')
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length > 0 && !l.startsWith('#') && !l.startsWith('---'))
    .map(l => l.startsWith('- ') ? l : `- ${l}`)
    .join('\n');

  if (!newContent.trim()) {
    log('info', 'merge_skip_empty', { file: basename(absPath) });
    return false;
  }

  const existing = existsSync(absPath) ? readFileSync(absPath, 'utf8') : '';

  // Haiku dedup against existing content
  const unique = await deduplicateWithHaiku(newContent, existing);
  if (!unique.trim()) {
    log('info', 'merge_skip_duplicate', { file: basename(absPath) });
    return false;
  }

  const datestamp = new Date().toISOString().split('T')[0];
  const section = `\n\n## ${datestamp}\n\n${unique}`;

  const header = existing || `# ${AGENT_NAME} — ${basename(absPath, '.md')}\n`;
  writeFileSync(absPath, header + section + '\n');

  log('info', 'merge_complete', {
    file: basename(absPath),
    dir: join(absPath, '..'),
  });

  return true;
}

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

// Static CLAUDE.md ownership belongs to deploy/runtime generation.
// Scribe updates mutable memory files only.

// ─── Batch processing ───

async function processBatch() {
  if (pendingUpdates.size === 0) return;

  log('info', 'batch_start', { files: pendingUpdates.size });

  for (const [key, updates] of pendingUpdates) {
    try {
      const { path: filePath, project, scope } = updates[0];
      const dir = targetDir(scope, project);
      if (!dir) continue; // dropped: project scope with no project name
      const absPath = join(dir, basename(filePath));

      log('info', 'routing', {
        file: basename(filePath),
        scope,
        project: project || null,
        dest: absPath,
      });

      await mergeIntoFile(absPath, updates);
    } catch (e) {
      log('error', 'merge_failed', { key, error: e.message });
    }
  }

  pendingUpdates.clear();
}

function queueUpdate(filePath, content, project, scope) {
  const key = `${scope}:${project || 'global'}:${basename(filePath)}`;
  if (!pendingUpdates.has(key)) {
    pendingUpdates.set(key, []);
  }
  pendingUpdates.get(key).push({
    path: filePath,
    content,
    project,
    scope,
    timestamp: new Date().toISOString(),
  });

  if (batchTimer) clearTimeout(batchTimer);
  batchTimer = setTimeout(processBatch, BATCH_WINDOW_MS);
}

// ─── Kafka ───

const kafka = new Kafka({
  clientId: `scribe-${AGENT_NAME}-${POD_NAME}`,
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const consumer = kafka.consumer({ groupId: `scribe-${AGENT_NAME}` });

async function main() {
  log('info', 'scribe_boot', {
    agent: AGENT_NAME,
    global_dir: GLOBAL_DIR,
    projects_dir: PROJECTS_DIR,
  });

  mkdirSync(GLOBAL_DIR, { recursive: true });
  mkdirSync(PROJECTS_DIR, { recursive: true });

  await consumer.connect();
  await consumer.subscribe({ topic: `memory.updates.${AGENT_NAME}`, fromBeginning: false });

  log('info', 'kafka_ready', { topic: `memory.updates.${AGENT_NAME}` });

  await consumer.run({
    eachMessage: async ({ message }) => {
      try {
        const update = JSON.parse(message.value.toString());
        const scope = update.scope || 'project';
        log('info', 'update_received', {
          path: update.path,
          project: update.project || null,
          scope,
          content_length: update.content?.length,
        });
        queueUpdate(update.path, update.content, update.project || '', scope);
      } catch (e) {
        log('error', 'update_parse_failed', { error: e.message });
      }
    },
  });
}

async function shutdown() {
  log('info', 'scribe_shutdown');
  if (pendingUpdates.size > 0) await processBatch();
  try { await consumer.disconnect(); } catch {}
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('error', 'scribe_fatal', { error: e.message });
  process.exit(1);
});
