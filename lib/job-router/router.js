#!/usr/bin/env node
// Job Router — HTTP/MCP frontend that publishes jobs to Kafka.
//
// Current responsibilities:
// - explicit pod-agent delegation over Kafka
// - synchronous wait for job results
// - minimal MCP wrapper for delegate/status
// - worker session registry over websocket for warm-path routing

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import { Kafka } from 'kafkajs';
import { WebSocketServer } from 'ws';
import { createServer } from 'node:http';
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
const DEFAULT_TIMEOUT_MS = 1_800_000;

const kafka = new Kafka({
  clientId: 'job-router',
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const producer = kafka.producer();
const resultConsumer = kafka.consumer({ groupId: 'job-router-results' });
const admin = kafka.admin();

const pendingResults = new Map();
const pendingSocketRequests = new Map();
const pendingClientJobsByCorrelation = new Map();
const pendingClientJobsByJobId = new Map();
const workerSessions = new Map();
const clientSessionBindings = new Map();

function sendJson(socket, payload) {
  if (!socket || socket.readyState !== 1) return;
  socket.send(JSON.stringify(payload));
}

function registerPendingClientJob(job, socket, requestId) {
  const record = { socket, request_id: requestId, job_id: job.id, correlation_id: job.correlation_id, agent: job.agent };
  pendingClientJobsByCorrelation.set(job.correlation_id, record);
  pendingClientJobsByJobId.set(job.id, record);
}

function clearPendingClientJob(record) {
  if (!record) return;
  pendingClientJobsByCorrelation.delete(record.correlation_id);
  pendingClientJobsByJobId.delete(record.job_id);
}

function notifyClientPickedUp(jobId, session) {
  const record = pendingClientJobsByJobId.get(jobId);
  if (!record) return;
  sendJson(record.socket, {
    type: 'picked_up',
    request_id: record.request_id,
    job_id: record.job_id,
    agent: record.agent,
    session_id: session?.session_id || null,
    pod_name: session?.pod_name || null,
    model: session?.model || null,
  });
}

function notifyClientCompleted(result) {
  const record = pendingClientJobsByCorrelation.get(result.correlation_id);
  if (!record) return;
  sendJson(record.socket, {
    type: result.status === 'success' ? 'completed' : 'failed',
    request_id: record.request_id,
    job_id: record.job_id,
    agent: record.agent,
    output: result.output,
    backend: result.backend || null,
    status: result.status,
    error: result.status === 'success' ? null : result.output,
  });
  clearPendingClientJob(record);
}

function notifyClientDisconnected(socket) {
  for (const record of pendingClientJobsByCorrelation.values()) {
    if (record.socket !== socket) continue;
    clearPendingClientJob(record);
  }
}

function findLiveWorker(agent, model = null) {
  return findAttachableWorker(agent, model);
}

function clientQueueJob(agent, prompt, body, socket, requestId) {
  const job = makeJob(agent, prompt, body);
  registerPendingClientJob(job, socket, requestId);
  producer.send({
    topic: `jobs.${job.agent}`,
    messages: [{ key: job.correlation_id, value: JSON.stringify(job) }],
  }).then(() => {
    log(`JOB published to jobs.${job.agent}`, { correlation_id: job.correlation_id, job_id: job.id, model: job.metadata?.model || null });
    sendJson(socket, {
      type: 'queued',
      request_id: requestId,
      job_id: job.id,
      correlation_id: job.correlation_id,
      agent: job.agent,
      model: body.model || null,
    });
  }).catch((e) => {
    clearPendingClientJob(pendingClientJobsByCorrelation.get(job.correlation_id));
    sendJson(socket, { type: 'failed', request_id: requestId, agent: job.agent, error: e.message, status: 'error' });
  });
}

function attachClientSocket(socket) {
  clientSockets.add(socket);
  socket.on('message', (raw) => {
    let event;
    try {
      event = JSON.parse(raw.toString());
    } catch {
      sendJson(socket, { type: 'error', error: 'invalid_json' });
      return;
    }

    if (event.type === 'list_workers') {
      sendJson(socket, { type: 'workers', items: snapshotWorkerSessions() });
      return;
    }

    if (event.type === 'attach') {
      const { agent, model, request_id } = event;
      const live = findLiveWorker(agent, model || null);
      if (!live) {
        sendJson(socket, { type: 'queued', request_id, agent, model: model || null });
        return;
      }
      clientSessionBindings.set(socket, { session_id: live.session_id, agent, model: live.model });
      sendJson(socket, { type: 'attached', request_id, session_id: live.session_id, pod_name: live.pod_name, agent, model: live.model });
      return;
    }

    if (event.type === 'delegate' || event.type === 'queue') {
      const { agent, prompt, project, repo, model, request_id } = event;
      if (!agent || !prompt) {
        sendJson(socket, { type: 'error', request_id, error: 'agent and prompt required' });
        return;
      }
      const live = findLiveWorker(agent, model || null);
      if (live) {
        clientSessionBindings.set(socket, { session_id: live.session_id, agent, model: live.model });
        sendJson(socket, { type: 'attached', request_id, session_id: live.session_id, pod_name: live.pod_name, agent, model: live.model });
        const job = makeJob(agent, prompt, { project, repo, model });
        sendViaWorkerSession(live, prompt, job, request_id || randomUUID()).then((result) => {
          sendJson(socket, {
            type: result.status === 'success' ? 'completed' : 'failed',
            request_id,
            agent,
            output: result.output,
            backend: result.backend || null,
            status: result.status,
            error: result.status === 'success' ? null : result.output,
          });
        }).catch((e) => {
          sendJson(socket, { type: 'failed', request_id, agent, error: e.message, status: 'error' });
        });
      } else {
        clientQueueJob(agent, prompt, { project, repo, model }, socket, request_id || randomUUID());
      }
      return;
    }

    if (event.type === 'message') {
      const binding = clientSessionBindings.get(socket);
      if (!binding || !binding.session_id) {
        sendJson(socket, { type: 'error', request_id: event.request_id, error: 'no attached session' });
        return;
      }
      const session = workerSessions.get(binding.session_id);
      if (!session) {
        sendJson(socket, { type: 'error', request_id: event.request_id, error: 'attached session no longer available' });
        clientSessionBindings.delete(socket);
        return;
      }
      const job = makeJob(binding.agent, event.content, { model: binding.model });
      sendViaWorkerSession({ session_id: binding.session_id, ...session }, event.content, job, event.request_id || randomUUID()).then((result) => {
        sendJson(socket, {
          type: result.status === 'success' ? 'completed' : 'failed',
          request_id: event.request_id,
          agent: binding.agent,
          output: result.output,
          backend: result.backend || null,
          status: result.status,
          error: result.status === 'success' ? null : result.output,
        });
      }).catch((e) => {
        sendJson(socket, { type: 'failed', request_id: event.request_id, agent: binding.agent, error: e.message, status: 'error' });
      });
      return;
    }

    if (event.type === 'close') {
      clientSessionBindings.delete(socket);
      sendJson(socket, { type: 'closed', request_id: event.request_id || null });
      return;
    }
  });

  socket.on('close', () => {
    notifyClientDisconnected(socket);
    clientSessionBindings.delete(socket);
    clientSockets.delete(socket);
  });
}

function attachClientWss(clientWss) {
  clientWss.on('connection', (socket) => {
    attachClientSocket(socket);
  });
}

function chooseWarmPath(agent, model = null) {
  return findLiveWorker(agent, model);
}

function shouldUseWarmPath(agent, model = null) {
  return !!chooseWarmPath(agent, model);
}

function currentKnownAgents() {
  return KNOWN_AGENTS;
}

function makeClientError(error) {
  return { type: 'error', error };
}

function sessionSummary() {
  return snapshotWorkerSessions();
}

function notifyAllClientsWorkers(clientSockets) {
  for (const socket of clientSockets) {
    sendJson(socket, { type: 'workers', items: snapshotWorkerSessions() });
  }
}

const clientSockets = new Set();

function snapshotWorkerSessions() {
  return [...workerSessions.entries()].map(([session_id, session]) => ({
    session_id,
    agent: session.agent,
    model: session.model,
    pod_name: session.pod_name,
    state: session.state,
    current_job: session.current_job,
    connected_at: session.connected_at,
    last_heartbeat: session.last_heartbeat,
  }));
}

function existingConnectedAt(sessionId) {
  return workerSessions.get(sessionId)?.connected_at || new Date().toISOString();
}

function upsertWorkerSession(sessionId, partial) {
  const existing = workerSessions.get(sessionId) || {};
  workerSessions.set(sessionId, {
    ...existing,
    ...partial,
    last_heartbeat: new Date().toISOString(),
  });
}

function removeWorkerSession(sessionId) {
  workerSessions.delete(sessionId);
}

function findAttachableWorker(agent, model = null) {
  for (const [session_id, session] of workerSessions.entries()) {
    if (session.agent !== agent) continue;
    if (model && session.model !== model) continue;
    if ((session.state || 'idle') !== 'idle') continue;
    if (!session.socket || session.socket.readyState !== 1) continue;
    return { session_id, ...session };
  }
  return null;
}

function clearSocketRequestsForSession(sessionId) {
  for (const [requestId, pending] of pendingSocketRequests.entries()) {
    if (pending.session_id !== sessionId) continue;
    clearTimeout(pending.timer);
    pendingSocketRequests.delete(requestId);
    pending.reject(new Error('Worker session disconnected'));
  }
}

function resolveSocketRequest(requestId, payload, isError = false) {
  const pending = pendingSocketRequests.get(requestId);
  if (!pending) return;
  clearTimeout(pending.timer);
  pendingSocketRequests.delete(requestId);
  upsertWorkerSession(pending.session_id, {
    state: 'idle',
    current_job: null,
  });
  pending.resolve({ output: payload, is_error: isError, backend: null, status: isError ? 'error' : 'success' });
}

function rejectSocketRequest(requestId, errorText) {
  const pending = pendingSocketRequests.get(requestId);
  if (!pending) return;
  clearTimeout(pending.timer);
  pendingSocketRequests.delete(requestId);
  upsertWorkerSession(pending.session_id, {
    state: 'idle',
    current_job: null,
  });
  pending.reject(new Error(errorText));
}

function attachWorkerSocket(socket) {
  const sessionIdRef = { value: null };

  socket.on('message', (raw) => {
    let event;
    try {
      event = JSON.parse(raw.toString());
    } catch {
      return;
    }

    if (event.type === 'register' && event.session_id) {
      sessionIdRef.value = event.session_id;
      upsertWorkerSession(sessionIdRef.value, {
        socket,
        agent: event.agent || null,
        model: event.model || null,
        pod_name: event.pod_name || null,
        state: event.state || 'idle',
        current_job: event.current_job || null,
        connected_at: existingConnectedAt(sessionIdRef.value),
      });
      log('WORKER registered', { session_id: sessionIdRef.value, agent: event.agent, model: event.model, pod_name: event.pod_name });
      socket.send(JSON.stringify({ type: 'registered', session_id: sessionIdRef.value }));
      notifyAllClientsWorkers(clientSockets);
      return;
    }

    if (event.type === 'heartbeat' && sessionIdRef.value) {
      upsertWorkerSession(sessionIdRef.value, {
        state: event.state || 'idle',
        current_job: event.current_job || null,
      });
      if (event.current_job) {
        notifyClientPickedUp(event.current_job, { session_id: sessionIdRef.value, ...workerSessions.get(sessionIdRef.value) });
      }
      return;
    }

    if (event.type === 'result' && event.request_id) {
      if (event.is_error) rejectSocketRequest(event.request_id, event.error || event.output || 'Worker session error');
      else resolveSocketRequest(event.request_id, event.output || '', false);
      return;
    }

    if (event.type === 'error' && event.request_id) {
      rejectSocketRequest(event.request_id, event.error || 'Worker session error');
    }
  });

  socket.on('close', () => {
    if (!sessionIdRef.value) return;
    log('WORKER disconnected', { session_id: sessionIdRef.value });
    clearSocketRequestsForSession(sessionIdRef.value);
    removeWorkerSession(sessionIdRef.value);
  });
}

setInterval(() => {
  const now = Date.now();
  for (const [sessionId, session] of workerSessions.entries()) {
    const ts = Date.parse(session.last_heartbeat || '');
    if (!Number.isNaN(ts) && now - ts > 120000) {
      log('WORKER stale', { session_id: sessionId, agent: session.agent, model: session.model });
      clearSocketRequestsForSession(sessionId);
      workerSessions.delete(sessionId);
      try { session.socket?.terminate?.(); } catch {}
    }
  }
}, 30000);

function log(msg, data) {
  const entry = { level: 'info', component: 'router', event: msg, timestamp: new Date().toISOString(), ...data };
  console.log(JSON.stringify(entry));
}

function makeJob(agent, prompt, body = {}) {
  const metadata = {};
  if (body.project) metadata.project = body.project;
  if (body.repo) metadata.repo = body.repo;
  if (body.model) metadata.model = body.model;
  return {
    id: randomUUID(),
    agent,
    skill: null,
    prompt,
    project: body.project || null,
    repo: body.repo || null,
    correlation_id: randomUUID(),
    created_at: new Date().toISOString(),
    timeout_ms: DEFAULT_TIMEOUT_MS,
    mode: 'full',
    metadata,
  };
}

async function publishAndWaitJob(job) {
  const topic = `jobs.${job.agent}`;
  await producer.send({
    topic,
    messages: [{ key: job.correlation_id, value: JSON.stringify(job) }],
  });
  log(`JOB published to ${topic}`, { correlation_id: job.correlation_id, job_id: job.id, model: job.metadata?.model || null });
  const result = await waitForResult(job.correlation_id, job.timeout_ms || DEFAULT_TIMEOUT_MS);
  if (result.status === 'error' || result.status === 'timeout') {
    throw new Error(`Agent ${job.agent} ${result.status}: ${result.output}`);
  }
  return result;
}

function sendViaWorkerSession(session, prompt, job, requestId = randomUUID()) {
  return new Promise((resolve, reject) => {
    const socketRequestId = requestId;
    const timer = setTimeout(() => {
      pendingSocketRequests.delete(socketRequestId);
      reject(new Error(`Live session timed out after ${job.timeout_ms}ms`));
    }, (job.timeout_ms || DEFAULT_TIMEOUT_MS) + 5000);

    pendingSocketRequests.set(socketRequestId, { resolve, reject, timer, session_id: session.session_id });
    upsertWorkerSession(session.session_id, { state: 'busy', current_job: job.id });

    try {
      session.socket.send(JSON.stringify({
        type: 'prompt',
        request_id: socketRequestId,
        prompt,
        job,
      }));
    } catch (e) {
      clearTimeout(timer);
      pendingSocketRequests.delete(socketRequestId);
      upsertWorkerSession(session.session_id, { state: 'idle', current_job: null });
      reject(new Error(`Failed to write to worker socket: ${e.message}`));
    }
  });
}

async function routeJob(agent, prompt, body = {}) {
  const job = makeJob(agent, prompt, body);
  const liveSession = findAttachableWorker(agent, body.model || null);
  if (liveSession) {
    log('JOB routed via live session', { agent, session_id: liveSession.session_id, model: liveSession.model, job_id: job.id });
    return sendViaWorkerSession(liveSession, prompt, job);
  }
  return publishAndWaitJob(job);
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
      const response = await routeJob(agent, prompt, {});
      return { content: [{ type: 'text', text: response.output }] };
    },
  );

  server.tool('status', 'Server status — uptime, agents, pending jobs, worker sessions.', {}, async () => {
    return {
      content: [{ type: 'text', text: JSON.stringify({
        name: 'kord-router',
        boot: BOOT_TIME,
        agents: KNOWN_AGENTS,
        pending_jobs: pendingResults.size,
        worker_sessions: snapshotWorkerSessions(),
      }, null, 2) }],
    };
  });
}

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'kord-router', boot: BOOT_TIME, pending: pendingResults.size, worker_sessions: workerSessions.size });
});

app.get('/api/sessions', (_req, res) => {
  res.json({ sessions: snapshotWorkerSessions() });
});

app.post('/api/delegate', async (req, res) => {
  const { agent, prompt, project, repo, model } = req.body || {};
  if (!agent || !prompt) {
    return res.status(400).json({ error: 'Required: agent, prompt' });
  }
  if (model && (typeof model !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(model))) {
    return res.status(400).json({ error: 'Invalid model. Use a short model/backend identifier.' });
  }
  if (typeof agent !== 'string' || !/^[a-z][a-z0-9._-]{0,62}$/.test(agent)) {
    return res.status(400).json({ error: 'Invalid agent name. Use lowercase alphanumeric, dots, hyphens, or underscores (max 63 chars).' });
  }

  try {
    const result = await routeJob(agent, prompt, { project, repo, model });
    res.json({ agent, status: 'success', output: result.output, backend: result.backend || null });
  } catch (e) {
    log('API delegate error', { agent, error: e.message });
    const status = e.message.includes('timed out') ? 504 : 500;
    res.status(status).json({ agent, status: 'error', error: e.message });
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
        notifyClientCompleted(result);
      } catch {}
    },
  });

  const server = createServer(app);
  const workerWss = new WebSocketServer({ noServer: true });
  const clientWss = new WebSocketServer({ noServer: true });

  workerWss.on('connection', (socket) => {
    attachWorkerSocket(socket);
  });
  attachClientWss(clientWss);

  server.on('upgrade', (req, socket, head) => {
    if (req.url === '/ws/worker') {
      workerWss.handleUpgrade(req, socket, head, (ws) => {
        workerWss.emit('connection', ws, req);
      });
      return;
    }
    if (req.url === '/ws/client') {
      clientWss.handleUpgrade(req, socket, head, (ws) => {
        clientWss.emit('connection', ws, req);
        sendJson(ws, { type: 'workers', items: snapshotWorkerSessions() });
      });
      return;
    }
    socket.destroy();
  });
  server.listen(PORT, '0.0.0.0', () => {
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
