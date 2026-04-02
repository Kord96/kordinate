#!/usr/bin/env node
// Agent Pod Daemon — stream-json bridge between Kafka and a persistent Claude session.
//
// Pod = Claude session. Claude runs as a long-lived process for the pod's
// entire lifetime. The daemon is a thin bridge:
//
//   Kafka consumer → parse job → write to Claude stdin (stream-json)
//   Claude stdout (stream-json) → parse result → Kafka producer
//
// No --system-prompt, --resume, --session-id, preload.py, or boot step.
// Claude loads CLAUDE.md (with @ imports) natively from cwd.
//
// KEDA scales the pod itself. Scale down = kill pod = kill Claude.
// Scale up = new pod = new Claude session = fresh memory from shared PVC.

import { Kafka } from 'kafkajs';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { createInterface } from 'node:readline';
import { randomUUID } from 'node:crypto';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, relative } from 'node:path';

// ─── Config ───

const AGENT_NAME = process.env.AGENT_NAME;
if (!AGENT_NAME) { console.error('AGENT_NAME required'); process.exit(1); }

const AGENT_PROJECT_DIR = process.env.AGENT_PROJECT_DIR || `/kord/agents/${AGENT_NAME}`;
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka-kafka-bootstrap.dev.svc.cluster.local:9092').split(',');
const STATUS_PORT = parseInt(process.env.STATUS_PORT || '9090');
const DEFAULT_TIMEOUT_MS = 900_000;
const POD_NAME = process.env.HOSTNAME || `agent-${AGENT_NAME}-local`;
const RESPAWN_DELAY_MS = 3000;
const KORDINATE_HOME = process.env.KORDINATE_HOME || '/data/repos/kordinate';
const PROJECTS_ROOT = process.env.PROJECTS_ROOT || '/data/repos';

// Read model from .model file (written by setup-agent-dir.sh from IDENTITY.md)
let AGENT_MODEL = 'sonnet';
try {
  AGENT_MODEL = readFileSync(`${AGENT_PROJECT_DIR}/.model`, 'utf8').trim();
} catch {}

const MODEL_MAP = {
  'opus': 'claude-opus-4-6',
  'sonnet': 'claude-sonnet-4-6',
  'haiku': 'claude-haiku-4-5-20251001',
};
const CLAUDE_MODEL = MODEL_MAP[AGENT_MODEL] || MODEL_MAP['sonnet'];

// Memory dirs — Claude reads directly, no local copies
const AGENT_GLOBAL_DIR = `${AGENT_PROJECT_DIR}/memory/global`;
const TEAM_GLOBAL_DIR = '/kord/team/memory/global';

// Load reflection prompt template once at startup
let REFLECTION_PROMPT = '';
try {
  REFLECTION_PROMPT = readFileSync(`${KORDINATE_HOME}/lib/templates/reflection-prompt.md`, 'utf8');
} catch {
  REFLECTION_PROMPT = '';
}

// ─── Hash-based change detection ───
// Tracks MD5 hashes of files in watched directories.
// No copies — Claude reads directly from the shared dirs.
// Before each job, re-hash and report what changed.

function hashFile(filePath) {
  try {
    return createHash('md5').update(readFileSync(filePath)).digest('hex');
  } catch { return null; }
}

function walkDir(dir, base = dir) {
  const entries = [];
  if (!existsSync(dir)) return entries;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    const rel = relative(base, full);
    if (entry.isDirectory()) entries.push(...walkDir(full, base));
    else entries.push(rel);
  }
  return entries;
}

function createWatcher(dir) {
  const hashes = new Map();

  function snapshot() {
    if (!existsSync(dir)) return 0;
    const files = walkDir(dir);
    for (const rel of files) hashes.set(rel, hashFile(join(dir, rel)));
    return files.length;
  }

  function detectChanges() {
    const changes = { modified: [], added: [], removed: [] };
    if (!existsSync(dir)) return changes;

    const currentFiles = new Set(walkDir(dir));

    for (const rel of currentFiles) {
      const currentHash = hashFile(join(dir, rel));
      const prevHash = hashes.get(rel);
      if (!prevHash) {
        hashes.set(rel, currentHash);
        changes.added.push(rel);
      } else if (currentHash !== prevHash) {
        hashes.set(rel, currentHash);
        changes.modified.push(rel);
      }
    }

    for (const rel of hashes.keys()) {
      if (!currentFiles.has(rel)) {
        hashes.delete(rel);
        changes.removed.push(rel);
      }
    }

    return changes;
  }

  return { snapshot, detectChanges, dir };
}

const globalWatcher = createWatcher(AGENT_GLOBAL_DIR);
const teamWatcher = createWatcher(TEAM_GLOBAL_DIR);

// ─── State ───

let currentJob = null;
let jobCount = 0;
let claudeProcess = null;
let claudeReady = false;
let pendingResolve = null;
let resultBuffer = '';

// ─── Logging ───

function log(level, event, data = {}) {
  console.log(JSON.stringify({
    level, agent: AGENT_NAME,
    job_id: currentJob?.id || null,
    correlation_id: currentJob?.correlationId || null,
    event, pod_name: POD_NAME,
    timestamp: new Date().toISOString(),
    ...data,
  }));
}

// ─── Claude process management ───

function spawnClaude() {
  log('info', 'claude_spawn', { cwd: AGENT_PROJECT_DIR });

  const proc = spawn('claude', [
    '--print',
    '--input-format', 'stream-json',
    '--output-format', 'stream-json',
    '--verbose',
    '--model', CLAUDE_MODEL,
    '--dangerously-skip-permissions',
  ], {
    cwd: AGENT_PROJECT_DIR,
    env: {
      ...process.env,
      CLAUDE_CODE_DISABLE_MEMORY: '1',
      KAFKAJS_NO_PARTITIONER_WARNING: '1',
    },
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  // Parse stdout line by line (stream-json is newline-delimited JSON)
  const rl = createInterface({ input: proc.stdout });
  rl.on('line', (line) => {
    if (!line.trim()) return;
    try {
      const event = JSON.parse(line);
      handleClaudeEvent(event);
    } catch {
      // Non-JSON output (e.g., startup messages) — log it
      log('debug', 'claude_raw', { line: line.slice(0, 200) });
    }
  });

  // Log stderr
  proc.stderr.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) log('debug', 'claude_stderr', { text: text.slice(0, 500) });
  });

  proc.on('exit', (code, signal) => {
    log('warn', 'claude_exited', { code, signal });
    claudeReady = false;

    // Reject pending job if any
    if (pendingResolve) {
      pendingResolve({ text: `Claude exited (code=${code}, signal=${signal})`, is_error: true });
      pendingResolve = null;
      resultBuffer = '';
    }

    // Respawn after delay
    setTimeout(() => {
      log('info', 'claude_respawn');
      claudeProcess = spawnClaude();
    }, RESPAWN_DELAY_MS);
  });

  proc.on('error', (err) => {
    log('error', 'claude_spawn_error', { error: err.message });
  });

  // claudeReady is set true only when the 'system' event arrives
  return proc;
}

function handleClaudeEvent(event) {
  switch (event.type) {
    case 'system':
      // System init message — Claude is ready
      log('info', 'claude_ready', { session_id: event.session_id });
      claudeReady = true;
      break;

    case 'assistant':
      // Assistant message — extract text content
      if (event.message?.content) {
        for (const block of event.message.content) {
          if (block.type === 'text') resultBuffer += block.text;
        }
      }
      break;

    case 'result':
      // Turn complete — resolve pending promise
      const text = resultBuffer || event.result || '';
      const isError = event.is_error || false;
      if (pendingResolve) {
        pendingResolve({ text, is_error: isError });
        pendingResolve = null;
      }
      resultBuffer = '';
      break;

    default:
      // Other events (tool_use, tool_result, etc.) — ignore for result collection
      break;
  }
}

function sendMessage(prompt) {
  return new Promise((resolve, reject) => {
    if (!claudeProcess || !claudeReady) {
      return reject(new Error('Claude not ready'));
    }

    pendingResolve = resolve;
    resultBuffer = '';

    const msg = JSON.stringify({
      type: 'user',
      message: { role: 'user', content: prompt },
    });

    try {
      claudeProcess.stdin.write(msg + '\n');
    } catch (e) {
      pendingResolve = null;
      reject(new Error(`Failed to write to Claude stdin: ${e.message}`));
    }
  });
}

// ─── Kafka ───

const kafka = new Kafka({
  clientId: `agent-${AGENT_NAME}-${POD_NAME}`,
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const consumer = kafka.consumer({ groupId: `agent-${AGENT_NAME}` });
const producer = kafka.producer();

async function processJob(message) {
  let job;
  try {
    job = JSON.parse(message.value.toString());
  } catch (e) {
    log('error', 'job_parse_failed', { error: e.message });
    return;
  }

  currentJob = {
    id: job.id,
    correlationId: job.correlation_id,
    startedAt: new Date().toISOString(),
  };

  jobCount++;
  log('info', 'job_start', { skill: job.skill, job_number: jobCount });

  const startTime = Date.now();
  let status = 'success';
  let output = '';

  try {
    // Detect memory changes since last job
    let memoryRefresh = '';
    const globalChanges = globalWatcher.detectChanges();
    const teamChanges = teamWatcher.detectChanges();

    const allLines = [];
    for (const f of globalChanges.modified) allLines.push(`- ${AGENT_GLOBAL_DIR}/${f} (updated — re-read this file)`);
    for (const f of globalChanges.added) allLines.push(`- ${AGENT_GLOBAL_DIR}/${f} (new — read this file)`);
    for (const f of globalChanges.removed) allLines.push(`- ${f} (removed from global memory — disregard previous content)`);
    for (const f of teamChanges.modified) allLines.push(`- ${TEAM_GLOBAL_DIR}/${f} (updated — re-read this file)`);
    for (const f of teamChanges.added) allLines.push(`- ${TEAM_GLOBAL_DIR}/${f} (new — read this file)`);
    for (const f of teamChanges.removed) allLines.push(`- ${f} (removed from team memory — disregard)`);

    if (allLines.length) {
      memoryRefresh = `\nMemory changes since your last job:\n${allLines.join('\n')}\n`;
      log('info', 'memory_changes', {
        global: { modified: globalChanges.modified.length, added: globalChanges.added.length, removed: globalChanges.removed.length },
        team: { modified: teamChanges.modified.length, added: teamChanges.added.length, removed: teamChanges.removed.length },
      });
    }

    // Validate project exists if specified
    if (job.project && !existsSync(`${PROJECTS_ROOT}/${job.project}`)) {
      throw new Error(`Project not found: ${PROJECTS_ROOT}/${job.project}`);
    }

    // Inject memory paths so skills don't hardcode them
    let context = `\n[Memory]\n`
      + `Global: ${AGENT_GLOBAL_DIR}/\n`
      + `Team: ${TEAM_GLOBAL_DIR}/\n`;
    if (job.project) {
      const projMemPath = `${AGENT_PROJECT_DIR}/memory/projects/${job.project}`;
      context += `Project: ${projMemPath}/\n`
        + `Project code: ${PROJECTS_ROOT}/${job.project}\n`
        + `Read the files in ${projMemPath}/ for your prior findings on this project (if the directory exists).\n`;
    }

    const prompt = memoryRefresh + job.prompt + context + `\n[Job ${job.id}]`;

    // Send job to Claude and wait for result
    const timeoutMs = job.timeout_ms || DEFAULT_TIMEOUT_MS;
    const result = await Promise.race([
      sendMessage(prompt),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Job timed out after ${timeoutMs}ms`)), timeoutMs)
      ),
    ]);

    output = result.text;
    if (result.is_error) {
      status = 'error';
      log('error', 'job_error', { duration_ms: Date.now() - startTime });
    } else {
      log('info', 'job_complete', { duration_ms: Date.now() - startTime, job_number: jobCount });
    }

    // Second turn: reflection (only on successful jobs)
    if (status === 'success' && REFLECTION_PROMPT) {
      try {
        let reflectionCtx = REFLECTION_PROMPT;
        if (job.project) {
          reflectionCtx = reflectionCtx
            .replace('{{PROJECT}}', job.project)
            .replace('{{NO_PROJECT_NOTICE}}', '');
        } else {
          reflectionCtx = reflectionCtx
            .replace('{{PROJECT}}', '')
            .replace('{{NO_PROJECT_NOTICE}}', 'No project context for this job. Only save global insights (scope: global). Skip project-scoped reflections.');
        }
        await Promise.race([
          sendMessage(reflectionCtx),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Reflection timed out')), 120_000)
          ),
        ]);
        log('info', 'reflection_complete', { job_id: job.id });
      } catch (e) {
        log('warn', 'reflection_failed', { error: e.message });
      }
    }
  } catch (e) {
    status = e.message.includes('timed out') ? 'timeout' : 'error';
    output = e.message;
    log('error', 'job_failed', { status, error: e.message, duration_ms: Date.now() - startTime });
  }

  // Produce result to Kafka
  const result = {
    id: randomUUID(),
    correlation_id: job.correlation_id,
    agent: AGENT_NAME,
    skill: job.skill || null,
    status,
    output,
    started_at: currentJob.startedAt,
    finished_at: new Date().toISOString(),
    pod_name: POD_NAME,
    job_number: jobCount,
  };

  try {
    await producer.send({
      topic: 'jobs.result',
      messages: [{ key: job.correlation_id, value: JSON.stringify(result) }],
    });
  } catch (e) {
    log('error', 'result_publish_failed', { error: e.message });
  }

  currentJob = null;
}

// ─── Status server ───

const statusServer = createServer((req, res) => {
  if (req.url === '/status' && req.method === 'GET') {
    const body = currentJob
      ? { state: 'busy', job_id: currentJob.id, since: currentJob.startedAt, jobs_completed: jobCount - 1 }
      : { state: 'idle', claude_ready: claudeReady, jobs_completed: jobCount };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body));

  } else if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(claudeReady ? 200 : 503);
    res.end(claudeReady ? 'ok' : 'claude not ready');

  } else if (req.url === '/memory-update' && req.method === 'POST') {
    // Used by agents (via curl in reflection) to publish memory updates to Kafka
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const update = JSON.parse(body);
        await producer.send({
          topic: `memory.updates.${AGENT_NAME}`,
          messages: [{ key: update.path, value: JSON.stringify(update) }],
        });
        res.writeHead(200);
        res.end('queued');
      } catch (e) {
        res.writeHead(500);
        res.end(e.message);
      }
    });

  } else {
    res.writeHead(404);
    res.end('not found');
  }
});

// ─── Main ───

async function main() {
  log('info', 'agent_boot', { brokers: KAFKA_BROKERS, project_dir: AGENT_PROJECT_DIR, model: CLAUDE_MODEL });

  // Start status server
  statusServer.listen(STATUS_PORT, () => {
    log('info', 'status_server_ready', { port: STATUS_PORT });
  });

  // Snapshot memory hashes (Claude reads directly, no copies)
  const globalFiles = globalWatcher.snapshot();
  const teamFiles = teamWatcher.snapshot();
  log('info', 'memory_init', { global_files: globalFiles, team_files: teamFiles });

  // Spawn persistent Claude session
  claudeProcess = spawnClaude();

  // Wait a moment for Claude to initialize
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Connect to Kafka
  await producer.connect();
  await consumer.connect();
  await consumer.subscribe({ topic: `jobs.${AGENT_NAME}`, fromBeginning: false });

  log('info', 'kafka_ready', { topic: `jobs.${AGENT_NAME}` });

  // Process jobs sequentially
  await consumer.run({
    eachMessage: async ({ message }) => {
      // Wait for Claude to be ready (it may be respawning)
      let retries = 0;
      while (!claudeReady && retries < 30) {
        await new Promise(r => setTimeout(r, 1000));
        retries++;
      }
      if (!claudeReady) {
        log('error', 'claude_not_ready', { waited_seconds: retries });
        return;
      }
      await processJob(message);
    },
  });
}

// ─── Shutdown ───

async function shutdown() {
  log('info', 'agent_shutdown', { jobs_completed: jobCount });
  try {
    if (claudeProcess) claudeProcess.kill('SIGTERM');
    await consumer.disconnect();
    await producer.disconnect();
  } catch {}
  statusServer.close();
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('error', 'agent_fatal', { error: e.message });
  process.exit(1);
});
