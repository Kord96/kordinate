import { createServer } from 'node:http';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
const port = Number.parseInt(process.env.DISCOVERY_PORT ?? '9091', 10);
const host = process.env.DISCOVERY_HOST ?? '0.0.0.0';
const statePath = process.env.DISCOVERY_STATE_PATH ?? '.daemon-state/discovery-agents.json';
const catalogPath = process.env.DISCOVERY_CATALOG_PATH ?? '/app/agents/charon/skills/platform/manifests/base/discovery-catalog.json';
const ttlMs = Number.parseInt(process.env.DISCOVERY_TTL_MS ?? '120000', 10);
const registry = new Map();
const catalog = new Map();
function sanitizeRecord(record) {
    return {
        ...record,
        active: record.active ?? false,
    };
}
async function loadState() {
    try {
        const raw = await readFile(statePath, 'utf8');
        const parsed = JSON.parse(raw);
        const now = Date.now();
        for (const record of parsed) {
            if (record.last_seen_at && now - Date.parse(record.last_seen_at) <= ttlMs) {
                registry.set(record.name, record);
            }
        }
    }
    catch {
        // ignore missing state
    }
}
async function loadCatalog() {
    try {
        const raw = await readFile(catalogPath, 'utf8');
        const parsed = JSON.parse(raw);
        for (const record of parsed) {
            catalog.set(record.name, sanitizeRecord(record));
        }
    }
    catch {
        // ignore missing catalog
    }
}
async function persistState() {
    await mkdir(dirname(statePath), { recursive: true });
    const payload = JSON.stringify([...registry.values()], null, 2) + '\n';
    await writeFile(statePath, payload, 'utf8');
}
function activeRecords() {
    const now = Date.now();
    const merged = new Map(catalog);
    for (const [name, record] of registry.entries()) {
        if (record.last_seen_at && now - Date.parse(record.last_seen_at) > ttlMs) {
            registry.delete(name);
            continue;
        }
        const base = merged.get(name);
        merged.set(name, {
            ...(base ?? {}),
            ...record,
            active: true,
        });
    }
    const records = [...merged.values()].map(record => {
        if (!record.active) {
            return {
                ...record,
                active: false,
            };
        }
        return record;
    });
    records.sort((a, b) => a.name.localeCompare(b.name));
    return records;
}
function compactRecord(record) {
    return {
        name: record.name,
        capabilities: record.capabilities,
        backend_provider: record.backend_provider,
        backend_model: record.backend_model,
        supported_agent_params: record.supported_agent_params,
        active: record.active,
    };
}
function json(res, statusCode, payload) {
    res.statusCode = statusCode;
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify(payload));
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
function isAgentDiscoveryRecord(value) {
    if (!value || typeof value !== 'object')
        return false;
    const record = value;
    return typeof record.name === 'string'
        && Array.isArray(record.capabilities)
        && typeof record.backend_provider === 'string'
        && typeof record.backend_model === 'string'
        && Array.isArray(record.supported_agent_params);
}
const server = createServer(async (req, res) => {
    try {
        const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`);
        if (req.method === 'GET' && url.pathname === '/health') {
            json(res, 200, { ok: true, agents: activeRecords().length });
            return;
        }
        if (req.method === 'GET' && url.pathname === '/agents') {
            const verbose = url.searchParams.get('verbose') === '1';
            const agents = activeRecords().map(record => verbose ? record : compactRecord(record));
            await persistState();
            json(res, 200, { agents });
            return;
        }
        if (req.method === 'GET' && url.pathname.startsWith('/agents/')) {
            const name = decodeURIComponent(url.pathname.slice('/agents/'.length));
            const verbose = url.searchParams.get('verbose') === '1';
            const record = activeRecords().find(item => item.name === name);
            if (!record) {
                json(res, 404, { error: `agent '${name}' not found` });
                return;
            }
            await persistState();
            json(res, 200, verbose ? record : compactRecord(record));
            return;
        }
        if (req.method === 'POST' && url.pathname === '/register') {
            const body = await parseBody(req);
            if (!isAgentDiscoveryRecord(body)) {
                json(res, 400, { error: 'invalid agent discovery record' });
                return;
            }
            const now = new Date().toISOString();
            const previous = registry.get(body.name);
            const record = {
                ...body,
                registered_at: previous?.registered_at ?? now,
                last_seen_at: now,
                active: true,
            };
            registry.set(record.name, record);
            await persistState();
            json(res, 200, record);
            return;
        }
        json(res, 404, { error: 'not found' });
    }
    catch (error) {
        json(res, 500, { error: error instanceof Error ? error.message : String(error) });
    }
});
await loadCatalog();
await loadState();
server.listen(port, host, () => {
    process.stdout.write(`${JSON.stringify({
        event: 'discovery_server_ready',
        timestamp: new Date().toISOString(),
        host,
        port,
        catalog_path: catalogPath,
        state_path: statePath,
        ttl_ms: ttlMs,
    })}\n`);
});
