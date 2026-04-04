#!/usr/bin/env node
// Job Router — HTTP/MCP frontend that publishes jobs to Kafka.
//
// Current responsibilities:
// - explicit pod-agent delegation over Kafka
// - synchronous wait for job results
// - minimal MCP wrapper for delegate/status
//
// Legacy KORD-driven route/resource handling has been removed from this
// runtime path. Pod delegation should happen through /api/delegate or the MCP
// delegate tool.

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import { Kafka } from 'kafkajs';
import { existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3100');
const HOME = process.env.HOME || '/home/claude';
const KORDINATE_HOME = process.env.KORDINATE_HOME || join(HOME, '.kord');
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka.dev.svc.cluster.local:9092').split(',');
const BOOT_TIME = new Date().toISOString();
const DEFAULT_TIMEOUT_MS = 1_800_000; // 30 minutes

// ─── Kafka ───

const kafka = new Kafka({
  clientId: 'job-router',
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const producer = kafka.producer();
const resultConsumer = kafka.consumer({ groupId: 'job-router-results' });
const admin = kafka.admin();

// Pending results: correlationId → { resolve, reject, timer }
const pendingResults = new Map();

async function publishJob(agent, prompt, opts = {}) {
  const correlationId = randomUUID();
  const job = {
    id: randomUUID(),
    agent,
    skill: opts.skill || null,
    prompt,
    correlation_id: correlationId,
    created_at: new Date().toISOString(),
    timeout_ms: opts.timeoutMs || DEFAULT_TIMEOUT_MS,
    mode: opts.mode || 'full',
    metadata: opts.metadata || {},
  };

  await producer.send({
    topic: `jobs.${agent}`,
    messages: [{ key: correlationId, value: JSON.stringify(job) }],
  });

  log(`JOB published to jobs.${agent}`, { correlation_id: correlationId, skill: opts.skill });
  return correlationId;
}

function waitForResult(correlationId, timeoutMs = DEFAULT_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pendingResults.delete(correlationId);
      reject(new Error(`Job timed out after ${timeoutMs}ms`));
    }, timeoutMs + 5000);

    pendingResults.set(correlationId, { resolve, reject, timer });
  });
}

async function submitAndWait(agent, prompt, opts = {}) {
  const correlationId = await publishJob(agent, prompt, opts);
  const result = await waitForResult(correlationId, opts.timeoutMs || DEFAULT_TIMEOUT_MS);
  if (result.status === 'error' || result.status === 'timeout') {
    throw new Error(`Agent ${agent} ${result.status}: ${result.output}`);
  }
  return result;
}

function getKnownAgents() {
  const agents = new Set();
  try {
    const agentsDir = join(KORDINATE_HOME, 'agents');
    for (const d of readdirSync(agentsDir, { withFileTypes: true })) {
      if (d.isDirectory() && existsSync(join(agentsDir, d.name, 'IDENTITY.md'))) agents.add(d.name);
    }
  } catch {}
  agents.delete('main');
  return [...agents].sort();
}

const KNOWN_AGENTS = getKnownAgents();

// ─── MCP tool registration ───

function registerTools(server) {
  server.tool(
    'delegate',
    'Delegate a prompt to a kordinate agent. Publishes to Kafka and waits for the result.',
    {
      agent: z.enum(KNOWN_AGENTS).describe('The agent to invoke'),
      prompt: z.string().describe('The prompt to send'),
    },
    async ({ agent, prompt }) => {
      log('TOOL delegate', { agent, prompt: prompt.substring(0, 100) });
      const response = await submitAndWait(agent, prompt);
      return { content: [{ type: 'text', text: response.output }] };
    },
  );

  server.tool('status', 'Server status — uptime, agents, pending jobs.', {}, async () => {
    return {
      content: [{ type: 'text', text: JSON.stringify({
        name: 'kord-router',
        boot: BOOT_TIME,
        agents: KNOWN_AGENTS,
        pending_jobs: pendingResults.size,
      }, null, 2) }],
    };
  });
}

// ─── Logging ───

function log(msg, data) {
  const entry = { level: 'info', component: 'router', event: msg, timestamp: new Date().toISOString(), ...data };
  console.log(JSON.stringify(entry));
}

// ─── Express app ───

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'kord-router', boot: BOOT_TIME, pending: pendingResults.size });
});

app.post('/api/delegate', async (req, res) => {
  const { agent, prompt, project, repo } = req.body || {};
  if (!agent || !prompt) {
    return res.status(400).json({ error: 'Required: agent, prompt' });
  }
  if (typeof agent !== 'string' || !/^[a-z][a-z0-9_-]{0,62}$/.test(agent)) {
    return res.status(400).json({ error: 'Invalid agent name. Use lowercase alphanumeric, hyphens, or underscores (max 63 chars).' });
  }

  const jobId = randomUUID();
  const correlationId = randomUUID();
  const topic = `jobs.${agent}`;
  const metadata = {};
  if (project) metadata.project = project;
  if (repo) metadata.repo = repo;

  log('API delegate', { agent, job_id: jobId, correlation_id: correlationId, prompt: prompt.substring(0, 100) });

  try {
    const job = {
      id: jobId,
      agent,
      skill: null,
      prompt,
      project: project || null,
      repo: repo || null,
      correlation_id: correlationId,
      created_at: new Date().toISOString(),
      timeout_ms: DEFAULT_TIMEOUT_MS,
      mode: 'full',
      metadata,
    };

    await producer.send({
      topic,
      messages: [{ key: correlationId, value: JSON.stringify(job) }],
    });

    log(`JOB published to ${topic}`, { correlation_id: correlationId });

    const result = await waitForResult(correlationId, DEFAULT_TIMEOUT_MS);
    if (result.status === 'error' || result.status === 'timeout') {
      return res.status(502).json({ agent, job_id: jobId, correlation_id: correlationId, status: result.status, error: result.output, backend: result.backend || null });
    }
    res.json({ agent, job_id: jobId, correlation_id: correlationId, status: 'success', output: result.output, backend: result.backend || null });
  } catch (e) {
    log('API delegate error', { agent, job_id: jobId, correlation_id: correlationId, error: e.message });
    const status = e.message.includes('timed out') ? 504 : 500;
    res.status(status).json({ agent, job_id: jobId, correlation_id: correlationId, status: 'error', error: e.message });
  }
});

app.get('/api/agents', async (_req, res) => {
  try {
    const topics = await admin.listTopics();
    const agents = topics
      .filter(t => t.startsWith('jobs.') && t !== 'jobs.result')
      .map(t => t.slice('jobs.'.length))
      .sort();
    res.json({ agents });
  } catch (e) {
    log('API agents error', { error: e.message });
    res.status(500).json({ error: 'Failed to list agents', detail: e.message });
  }
});

app.post('/mcp', async (req, res) => {
  try {
    const server = new McpServer({ name: 'kord', version: '3.0.0' });
    registerTools(server);
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (e) {
    log('MCP error', { error: e.message });
    if (!res.headersSent) res.status(500).json({ jsonrpc: '2.0', error: { code: -32603, message: e.message }, id: null });
  }
});

// ─── Start ───

async function main() {
  await admin.connect();
  await producer.connect();
  await resultConsumer.connect();
  await resultConsumer.subscribe({ topic: 'jobs.result', fromBeginning: false });

  await resultConsumer.run({
    eachMessage: async ({ message }) => {
      try {
        const result = JSON.parse(message.value.toString());
        const pending = pendingResults.get(result.correlation_id);
        if (pending) {
          clearTimeout(pending.timer);
          pendingResults.delete(result.correlation_id);
          pending.resolve(result);
        }
      } catch {}
    },
  });

  app.listen(PORT, '0.0.0.0', () => {
    log('Router started', { port: PORT, agents: KNOWN_AGENTS });
  });
}

async function shutdown() {
  log('Router shutdown');
  try {
    await resultConsumer.disconnect();
    await producer.disconnect();
    await admin.disconnect();
  } catch {}
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('Fatal', { error: e.message });
  process.exit(1);
});
