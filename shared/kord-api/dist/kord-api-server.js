import { createServer } from 'node:http';
import { Kafka } from 'kafkajs';
import { createDiscoveryRegistry, isAgentDiscoveryRecord } from './discovery-registry.js';
import { log } from './log.js';
const host = process.env.KORD_API_HOST ?? '0.0.0.0';
const port = Number.parseInt(process.env.KORD_API_PORT ?? '9091', 10);
const statePath = process.env.DISCOVERY_STATE_PATH ?? '.daemon-state/discovery-agents.json';
const catalogPath = process.env.DISCOVERY_CATALOG_PATH ?? '/app/agents/charon/skills/platform/manifests/base/discovery-catalog.json';
const ttlMs = Number.parseInt(process.env.DISCOVERY_TTL_MS ?? '120000', 10);
const kafkaBrokers = (process.env.KAFKA_BROKERS ?? 'localhost:9092').split(',');
const replyTopic = process.env.KORD_API_REPLY_TOPIC ?? 'kord-api-replies';
const defaultTimeoutMs = Number.parseInt(process.env.KORD_API_DEFAULT_TIMEOUT_MS ?? '120000', 10);
const allowedApiKeys = new Set([
    ...(process.env.KORD_API_KEYS ?? '').split(','),
    process.env.KORD_API_KEY ?? '',
].map(value => value.trim()).filter(Boolean));
const registry = createDiscoveryRegistry({ statePath, catalogPath, ttlMs });
const kafka = new Kafka({
    clientId: 'kord-api',
    brokers: kafkaBrokers,
});
const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'kord-api' });
const pending = new Map();
const requests = new Map();
let ready = false;
function json(res, statusCode, payload) {
    res.statusCode = statusCode;
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify(payload));
}
function extractApiKey(req) {
    const direct = req.headers['x-api-key'];
    if (typeof direct === 'string' && direct.trim())
        return direct.trim();
    const auth = req.headers.authorization;
    if (!auth)
        return undefined;
    const match = auth.match(/^Bearer\s+(.+)$/i);
    return match?.[1]?.trim();
}
function requireAuth(req, res) {
    if (allowedApiKeys.size === 0) {
        json(res, 503, { error: 'kord api auth is not configured' });
        return false;
    }
    const apiKey = extractApiKey(req);
    if (!apiKey || !allowedApiKeys.has(apiKey)) {
        json(res, 401, { error: 'unauthorized' });
        return false;
    }
    return true;
}
async function parseBody(req) {
    const chunks = [];
    for await (const chunk of req) {
        chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }
    if (chunks.length === 0)
        return undefined;
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}
function isPromptBody(value) {
    if (!value || typeof value !== 'object')
        return false;
    const body = value;
    return typeof body.prompt === 'string'
        && (body.working_dir === undefined || typeof body.working_dir === 'string')
        && (body.timeout_ms === undefined || typeof body.timeout_ms === 'number')
        && (body.reflect === undefined || typeof body.reflect === 'boolean')
        && (body.reflection_prompt === undefined || typeof body.reflection_prompt === 'string')
        && (body.agent_params === undefined || typeof body.agent_params === 'object')
        && (body.session_id === undefined || typeof body.session_id === 'string')
        && (body.async === undefined || typeof body.async === 'boolean');
}
function deferReply(correlationId, timeoutMs) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            pending.delete(correlationId);
            reject(new Error(`timed out waiting for ${correlationId}`));
        }, timeoutMs);
        pending.set(correlationId, { resolve, reject, timer });
    });
}
async function sendPrompt(agent, body, requestId) {
    const correlationId = requestId ?? `${agent}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    const timeoutMs = body.timeout_ms ?? defaultTimeoutMs;
    const request = {
        type: 'request',
        sender: replyTopic,
        correlation_id: correlationId,
        prompt: body.prompt,
        working_dir: body.working_dir,
        timeout_ms: body.timeout_ms,
        reflect: body.reflect,
        reflection_prompt: body.reflection_prompt,
        agent_params: body.agent_params,
        session_id: body.session_id,
    };
    const reply = deferReply(correlationId, timeoutMs);
    await producer.send({
        topic: agent,
        messages: [{
                key: body.session_id ?? correlationId,
                value: JSON.stringify(request),
            }],
    });
    return { correlationId, reply };
}
function completeRequest(requestId, response) {
    const existing = requests.get(requestId);
    if (!existing)
        return;
    requests.set(requestId, {
        ...existing,
        status: response.status === 'error' ? 'error' : 'completed',
        completed_at: new Date().toISOString(),
        response,
        error: response.status === 'error' ? response.output : undefined,
    });
}
const server = createServer(async (req, res) => {
    try {
        const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
        if (req.method === 'GET' && url.pathname === '/health') {
            json(res, ready ? 200 : 503, { ok: ready, agents: registry.list().length });
            return;
        }
        if (req.method === 'POST' && url.pathname === '/register') {
            const body = await parseBody(req);
            if (!isAgentDiscoveryRecord(body)) {
                json(res, 400, { error: 'invalid agent discovery record' });
                return;
            }
            const record = await registry.register(body);
            json(res, 200, record);
            return;
        }
        if (!requireAuth(req, res)) {
            return;
        }
        if (req.method === 'GET' && url.pathname === '/agents') {
            const verbose = url.searchParams.get('verbose') === '1';
            const agents = registry.list().map(record => verbose ? record : registry.compact(record));
            json(res, 200, { agents });
            return;
        }
        if (req.method === 'GET' && url.pathname.startsWith('/agents/')) {
            const name = decodeURIComponent(url.pathname.slice('/agents/'.length));
            const verbose = url.searchParams.get('verbose') === '1';
            const record = registry.get(name);
            if (!record) {
                json(res, 404, { error: `agent '${name}' not found` });
                return;
            }
            json(res, 200, verbose ? record : registry.compact(record));
            return;
        }
        if (req.method === 'GET' && url.pathname.startsWith('/requests/')) {
            const requestId = decodeURIComponent(url.pathname.slice('/requests/'.length));
            const requestRecord = requests.get(requestId);
            if (!requestRecord) {
                json(res, 404, { error: `request '${requestId}' not found` });
                return;
            }
            json(res, 200, requestRecord);
            return;
        }
        if (req.method === 'POST' && url.pathname.startsWith('/agents/')) {
            const suffix = url.pathname.slice('/agents/'.length);
            if (!suffix.endsWith('/prompt')) {
                json(res, 404, { error: 'not found' });
                return;
            }
            const name = decodeURIComponent(suffix.slice(0, -'/prompt'.length));
            const record = registry.get(name);
            if (!record) {
                json(res, 404, { error: `agent '${name}' not found` });
                return;
            }
            const body = await parseBody(req);
            if (!isPromptBody(body)) {
                json(res, 400, { error: 'invalid prompt body' });
                return;
            }
            const startedAt = Date.now();
            const requestId = `${record.name}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
            requests.set(requestId, {
                request_id: requestId,
                agent: record.name,
                status: 'pending',
                created_at: new Date(startedAt).toISOString(),
            });
            const { reply } = await sendPrompt(record.name, body, requestId);
            if (body.async) {
                void reply.then(response => completeRequest(requestId, response), error => {
                    const existing = requests.get(requestId);
                    if (!existing)
                        return;
                    requests.set(requestId, {
                        ...existing,
                        status: 'error',
                        completed_at: new Date().toISOString(),
                        error: error instanceof Error ? error.message : String(error),
                    });
                });
                json(res, 202, {
                    request_id: requestId,
                    status: 'pending',
                    agent: record.name,
                    status_url: `/requests/${requestId}`,
                });
                return;
            }
            const syncReply = await reply;
            const completedAt = Date.now();
            const metadata = {
                ...(syncReply.metadata ?? {}),
                gateway_timing: {
                    started_at: new Date(startedAt).toISOString(),
                    completed_at: new Date(completedAt).toISOString(),
                    total_ms: completedAt - startedAt,
                },
            };
            const enrichedReply = { ...syncReply, metadata };
            completeRequest(requestId, enrichedReply);
            json(res, 200, enrichedReply);
            return;
        }
        json(res, 404, { error: 'not found' });
    }
    catch (error) {
        json(res, 500, { error: error instanceof Error ? error.message : String(error) });
    }
});
async function main() {
    await registry.load();
    await producer.connect();
    await consumer.connect();
    await consumer.subscribe({ topic: replyTopic, fromBeginning: false });
    await consumer.run({
        eachMessage: async ({ message }) => {
            const raw = message.value?.toString() ?? '';
            let parsed;
            try {
                parsed = JSON.parse(raw);
            }
            catch {
                return;
            }
            if (!parsed || typeof parsed !== 'object' || parsed.type !== 'response') {
                return;
            }
            const response = parsed;
            const waiter = pending.get(response.correlation_id);
            if (!waiter)
                return;
            clearTimeout(waiter.timer);
            pending.delete(response.correlation_id);
            waiter.resolve(response);
        },
    });
    await new Promise((resolve, reject) => {
        server.once('error', reject);
        server.listen(port, host, () => resolve());
    });
    ready = true;
    log('kord_api_ready', {
        host,
        port,
        reply_topic: replyTopic,
        state_path: statePath,
        catalog_path: catalogPath,
        ttl_ms: ttlMs,
    });
}
main().catch(error => {
    log('kord_api_fatal', { error: error instanceof Error ? error.message : String(error) });
    process.exit(1);
});
