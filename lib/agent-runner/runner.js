#!/usr/bin/env node
// Agent Runner — persistent Claude session that consumes jobs from Kafka.
//
// Each pod runs one instance. On startup it:
// 1. Boots a persistent Claude session (with agent identity + memory)
// 2. Connects to Kafka as consumer group `agent-<name>`
// 3. Pipes each job into the session via --continue
// 4. Produces results to `jobs.result`
// 5. Logs structured JSON to stdout (Alloy ships to Loki)
// 6. Exposes /status on port 9090 (idle/busy)
//
// The persistent session means: boot once, warm forever. No cold start per job.
// Context accumulates across jobs. Claude Code handles compression when the
// window fills.

import { Kafka } from 'kafkajs';
import { execSync, spawnSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';

// ─── Config ───

const AGENT_NAME = process.env.AGENT_NAME;
if (!AGENT_NAME) {
  console.error('AGENT_NAME environment variable is required');
  process.exit(1);
}

const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka.dev.svc.cluster.local:9092').split(',');
const KORDINATE_HOME = process.env.KORDINATE_HOME || '/kord/kordinate';
const STATUS_PORT = parseInt(process.env.STATUS_PORT || '9090');
const DEFAULT_TIMEOUT_MS = 900_000; // 15 minutes
const POD_NAME = process.env.HOSTNAME || `agent-${AGENT_NAME}-local`;

const CLAUDE_ENV = {
  ...process.env,
  CLAUDE_CODE_DISABLE_MEMORY: '1',
  KAFKAJS_NO_PARTITIONER_WARNING: '1',
};

// ─── State ───

let currentJob = null;
let sessionBooted = false;
let jobCount = 0;
const SESSION_ID = randomUUID(); // fixed per pod lifetime

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

// ─── Claude persistent session ───

function loadSystemPrompt() {
  const parts = [];
  const identityPath = join(KORDINATE_HOME, 'agents', AGENT_NAME, 'IDENTITY.md');
  if (existsSync(identityPath)) {
    const raw = readFileSync(identityPath, 'utf8');
    parts.push(raw.replace(/^---\n[\s\S]*?\n---\n?/, ''));
  }

  try {
    const preloadScript = join(KORDINATE_HOME, 'team', 'scripts', 'preload.py');
    if (existsSync(preloadScript)) {
      const output = execSync(
        `python3 "${preloadScript}" "${AGENT_NAME}"`,
        { cwd: KORDINATE_HOME, timeout: 30_000, encoding: 'utf8' }
      ).trim();
      if (output) parts.push(output);
    }
  } catch (e) {
    log('warn', 'preload_failed', { error: e.message });
  }

  return parts.join('\n\n');
}

function bootSession() {
  const systemPrompt = loadSystemPrompt();
  const bootPrompt = [
    `You are ${AGENT_NAME}, a kordinate agent running as a persistent Kubernetes pod.`,
    `You will receive jobs one at a time. For each job, do the work and respond with your output.`,
    `Write observations to agents/${AGENT_NAME}/memory/scratchpad-<jobid>.md (the job ID will be provided).`,
    `Do NOT write to the shared scratchpad.md.`,
    `Confirm you are ready by saying: READY`,
  ].join('\n');

  const args = [
    '-p', bootPrompt,
    '--session-id', SESSION_ID,
    '--dangerously-skip-permissions',
    '--output-format', 'text',
  ];
  if (systemPrompt) args.push('--system-prompt', systemPrompt);

  log('info', 'session_boot_start');

  const result = spawnSync('claude', args, {
    cwd: KORDINATE_HOME,
    env: CLAUDE_ENV,
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: 120_000,
  });

  if (result.status !== 0) {
    const stderr = result.stderr?.toString().slice(0, 500) || '';
    throw new Error(`Boot failed (code ${result.status}): ${stderr}`);
  }

  const output = result.stdout?.toString().trim() || '';
  sessionBooted = true;
  log('info', 'session_booted', { output: output.slice(0, 200) });
  return output;
}

function runJob(prompt, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const args = [
    '--resume', SESSION_ID,
    '-p', prompt,
    '--dangerously-skip-permissions',
    '--output-format', 'text',
  ];

  const result = spawnSync('claude', args, {
    cwd: KORDINATE_HOME,
    env: CLAUDE_ENV,
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: timeoutMs,
  });

  if (result.status !== 0) {
    const stderr = result.stderr?.toString().slice(0, 1000) || '';
    throw new Error(`Claude exited with code ${result.status}: ${stderr}`);
  }

  return result.stdout?.toString().trim() || '';
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
  log('info', 'job_start', { skill: job.skill, mode: job.mode || 'full', job_number: jobCount });

  const startTime = Date.now();
  let status = 'success';
  let output = '';

  try {
    const timeoutMs = job.timeout_ms || DEFAULT_TIMEOUT_MS;
    const scratchpadNote = `\n\n[Job ID: ${job.id} — write observations to agents/${AGENT_NAME}/memory/scratchpad-${job.id}.md]`;
    output = runJob(job.prompt + scratchpadNote, timeoutMs);
    log('info', 'job_complete', { duration_ms: Date.now() - startTime, job_number: jobCount });
  } catch (e) {
    status = e.message.includes('timed out') ? 'timeout' : 'error';
    output = e.message;
    log('error', 'job_failed', { status, error: e.message, duration_ms: Date.now() - startTime });

    // If Claude crashed, re-boot the session for the next job
    if (status === 'error') {
      log('warn', 'session_reboot', { reason: 'claude crash' });
      try { bootSession(); } catch (e2) {
        log('error', 'session_reboot_failed', { error: e2.message });
      }
    }
  }

  // Produce result
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

// ─── Health/Status endpoint ───

const statusServer = createServer((req, res) => {
  if (req.url === '/status' && req.method === 'GET') {
    const body = currentJob
      ? { state: 'busy', job_id: currentJob.id, since: currentJob.startedAt, jobs_completed: jobCount - 1 }
      : { state: 'idle', session_booted: sessionBooted, jobs_completed: jobCount };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body));
  } else if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end('ok');
  } else {
    res.writeHead(404);
    res.end('not found');
  }
});

// ─── Main ───

async function main() {
  log('info', 'agent_boot', { brokers: KAFKA_BROKERS });

  statusServer.listen(STATUS_PORT, () => {
    log('info', 'status_server_ready', { port: STATUS_PORT });
  });

  // Boot persistent Claude session BEFORE connecting to Kafka
  bootSession();

  await producer.connect();
  await consumer.connect();
  await consumer.subscribe({ topic: `jobs.${AGENT_NAME}`, fromBeginning: false });

  log('info', 'kafka_ready', { topic: `jobs.${AGENT_NAME}` });

  await consumer.run({
    eachMessage: async ({ message }) => {
      await processJob(message);
    },
  });
}

// ─── Shutdown ───

async function shutdown() {
  log('info', 'agent_shutdown', { jobs_completed: jobCount });
  try { await consumer.disconnect(); await producer.disconnect(); } catch {}
  statusServer.close();
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('error', 'agent_fatal', { error: e.message });
  process.exit(1);
});
