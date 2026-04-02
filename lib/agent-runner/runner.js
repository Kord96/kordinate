#!/usr/bin/env node
// Agent Runner — Kafka consumer that invokes Claude CLI for each job.
//
// Each pod runs one instance of this process. It:
// 1. Connects to Kafka as consumer group `agent-<name>`
// 2. Polls `jobs.<name>` topic for work
// 3. Invokes Claude CLI with the agent's identity + memory
// 4. Produces result to `jobs.result`
// 5. Logs structured JSON to stdout (Alloy ships to Loki)
// 6. Exposes /status on port 9090 (idle/busy)

import { Kafka } from 'kafkajs';
import { spawn, execSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
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
const LOKI_URL = process.env.LOKI_URL || 'http://loki.monitor.svc.cluster.local:3100';
const KORDINATE_HOME = process.env.KORDINATE_HOME || '/kord/kordinate';
const STATUS_PORT = parseInt(process.env.STATUS_PORT || '9090');
const DEFAULT_TIMEOUT_MS = 900_000; // 15 minutes
const POD_NAME = process.env.HOSTNAME || `agent-${AGENT_NAME}-local`;

// ─── State ───

let currentJob = null; // { id, correlationId, startedAt }

// ─── Logging ───

function log(level, event, data = {}) {
  const entry = {
    level,
    agent: AGENT_NAME,
    job_id: currentJob?.id || null,
    correlation_id: currentJob?.correlationId || null,
    event,
    pod_name: POD_NAME,
    timestamp: new Date().toISOString(),
    ...data,
  };
  console.log(JSON.stringify(entry));
}

// ─── Claude CLI invocation ───

function loadSystemPrompt() {
  const parts = [];

  // Load IDENTITY.md
  const identityPath = join(KORDINATE_HOME, 'agents', AGENT_NAME, 'IDENTITY.md');
  if (existsSync(identityPath)) {
    const raw = readFileSync(identityPath, 'utf8');
    parts.push(raw.replace(/^---\n[\s\S]*?\n---\n?/, ''));
  }

  // Load preloaded memory via preload.py
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

function invokeClaude(prompt, jobId, timeoutMs = DEFAULT_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const systemPrompt = loadSystemPrompt();

    // Write per-job scratchpad instruction into the prompt
    const scratchpadPath = `agents/${AGENT_NAME}/memory/scratchpad-${jobId}.md`;
    const wrappedPrompt = [
      prompt,
      '',
      `## Memory`,
      `Write any observations or insights to: ${scratchpadPath}`,
      `Do NOT write to the shared scratchpad.md — use this per-job file only.`,
    ].join('\n');

    const args = [
      '-p', wrappedPrompt,
      '--dangerously-skip-permissions',
      '--output-format', 'text',
    ];

    if (systemPrompt) {
      args.push('--system-prompt', systemPrompt);
    }

    log('info', 'claude_start', { timeout_ms: timeoutMs });

    const proc = spawn('claude', args, {
      cwd: KORDINATE_HOME,
      env: {
        ...process.env,
        CLAUDE_CODE_DISABLE_MEMORY: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: timeoutMs,
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });

    proc.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    proc.on('close', (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error(`Claude exited with code ${code}: ${stderr.slice(0, 1000)}`));
      }
    });

    proc.on('error', (err) => {
      reject(err);
    });

    // Timeout kill
    setTimeout(() => {
      try { proc.kill('SIGTERM'); } catch {}
      setTimeout(() => {
        try { proc.kill('SIGKILL'); } catch {}
      }, 5000);
      reject(new Error(`Claude timed out after ${timeoutMs}ms`));
    }, timeoutMs);
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

  log('info', 'job_start', {
    skill: job.skill,
    mode: job.mode || 'full',
  });

  const startTime = Date.now();
  let status = 'success';
  let output = '';

  try {
    const timeoutMs = job.timeout_ms || DEFAULT_TIMEOUT_MS;
    output = await invokeClaude(job.prompt, job.id, timeoutMs);
    log('info', 'job_complete', { duration_ms: Date.now() - startTime });
  } catch (e) {
    status = e.message.includes('timed out') ? 'timeout' : 'error';
    output = e.message;
    log('error', 'job_failed', {
      status,
      error: e.message,
      duration_ms: Date.now() - startTime,
    });
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
  };

  try {
    await producer.send({
      topic: 'jobs.result',
      messages: [{
        key: job.correlation_id,
        value: JSON.stringify(result),
      }],
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
      ? { state: 'busy', job_id: currentJob.id, since: currentJob.startedAt }
      : { state: 'idle' };
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
  log('info', 'agent_shutdown');
  try {
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
