import { createServer } from 'node:http';
import { Kafka } from 'kafkajs';
import { log } from './log.js';
const host = process.env.GATEWAY_HOST ?? '0.0.0.0';
const port = Number.parseInt(process.env.GATEWAY_PORT ?? '9092', 10);
const kafkaBrokers = (process.env.KAFKA_BROKERS ?? 'localhost:9092').split(',');
const discoveryServerUrl = process.env.DISCOVERY_SERVER_URL ?? 'http://127.0.0.1:9091';
const replyTopic = process.env.GATEWAY_REPLY_TOPIC ?? 'kord-gateway-replies';
const defaultTimeoutMs = Number.parseInt(process.env.GATEWAY_DEFAULT_TIMEOUT_MS ?? '120000', 10);
const allowedApiKeys = new Set([
    ...(process.env.GATEWAY_API_KEYS ?? '').split(','),
    process.env.GATEWAY_API_KEY ?? '',
].map(value => value.trim()).filter(Boolean));
const kafka = new Kafka({
    clientId: 'klaude-gateway',
    brokers: kafkaBrokers,
});
const producer = kafka.producer();
const consumer = kafka.consumer({ groupId: 'klaude-gateway' });
const pending = new Map();
let ready = false;
function json(res, statusCode, payload) {
    res.statusCode = statusCode;
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify(payload));
}
function unauthorized(res) {
    json(res, 401, { error: 'unauthorized' });
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
        json(res, 503, { error: 'gateway auth is not configured' });
        return false;
    }
    const apiKey = extractApiKey(req);
    if (!apiKey || !allowedApiKeys.has(apiKey)) {
        unauthorized(res);
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
async function fetchDiscovery(path) {
    const response = await fetch(new URL(path, discoveryServerUrl));
    if (!response.ok) {
        throw new Error(`discovery request failed with ${response.status}`);
    }
    return response.json();
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
        && (body.session_id === undefined || typeof body.session_id === 'string');
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
async function sendPrompt(agent, body) {
    const correlationId = `${agent}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
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
    return reply;
}
const server = createServer(async (req, res) => {
    try {
        const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
        if (req.method === 'GET' && url.pathname === '/health') {
            json(res, ready ? 200 : 503, { ok: ready });
            return;
        }
        if (!requireAuth(req, res)) {
            return;
        }
        if (req.method === 'GET' && url.pathname === '/agents') {
            const verbose = url.searchParams.get('verbose') === '1';
            const payload = await fetchDiscovery(verbose ? '/agents?verbose=1' : '/agents');
            json(res, 200, payload);
            return;
        }
        if (req.method === 'GET' && url.pathname.startsWith('/agents/')) {
            const name = decodeURIComponent(url.pathname.slice('/agents/'.length));
            const verbose = url.searchParams.get('verbose') === '1';
            const payload = await fetchDiscovery(verbose ? `/agents/${name}?verbose=1` : `/agents/${name}`);
            json(res, 200, payload);
            return;
        }
        if (req.method === 'POST' && url.pathname.startsWith('/agents/')) {
            const suffix = url.pathname.slice('/agents/'.length);
            if (!suffix.endsWith('/prompt')) {
                json(res, 404, { error: 'not found' });
                return;
            }
            const name = decodeURIComponent(suffix.slice(0, -'/prompt'.length));
            const record = await fetchDiscovery(`/agents/${name}?verbose=1`);
            const body = await parseBody(req);
            if (!isPromptBody(body)) {
                json(res, 400, { error: 'invalid prompt body' });
                return;
            }
            const startedAt = Date.now();
            const reply = await sendPrompt(record.name, body);
            const completedAt = Date.now();
            const metadata = {
                ...(reply.metadata ?? {}),
                gateway_timing: {
                    started_at: new Date(startedAt).toISOString(),
                    completed_at: new Date(completedAt).toISOString(),
                    total_ms: completedAt - startedAt,
                },
            };
            json(res, 200, { ...reply, metadata });
            return;
        }
        json(res, 404, { error: 'not found' });
    }
    catch (error) {
        json(res, 500, { error: error instanceof Error ? error.message : String(error) });
    }
});
async function main() {
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
    log('gateway_ready', {
        host,
        port,
        reply_topic: replyTopic,
        discovery_server_url: discoveryServerUrl,
    });
}
main().catch(error => {
    log('gateway_fatal', { error: error instanceof Error ? error.message : String(error) });
    process.exit(1);
});
