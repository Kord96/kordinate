import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
export function createDiscoveryRegistry(input) {
    const statePath = input?.statePath ?? '.daemon-state/discovery-agents.json';
    const catalogPath = input?.catalogPath ?? '/app/agents/charon/skills/platform/manifests/base/discovery-catalog.json';
    const ttlMs = input?.ttlMs ?? 120000;
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
    function list() {
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
        const records = [...merged.values()].map(record => record.active ? record : { ...record, active: false });
        records.sort((a, b) => a.name.localeCompare(b.name));
        return records;
    }
    function compact(record) {
        return {
            name: record.name,
            capabilities: record.capabilities,
            backend_provider: record.backend_provider,
            backend_model: record.backend_model,
            supported_agent_params: record.supported_agent_params,
            active: record.active,
        };
    }
    function get(name) {
        return list().find(item => item.name === name);
    }
    async function register(record) {
        const now = new Date().toISOString();
        const previous = registry.get(record.name);
        const normalized = {
            ...record,
            registered_at: previous?.registered_at ?? now,
            last_seen_at: now,
            active: true,
        };
        registry.set(normalized.name, normalized);
        await persistState();
        return normalized;
    }
    return {
        load: async () => {
            await loadCatalog();
            await loadState();
        },
        list,
        get,
        register,
        compact,
    };
}
export function isAgentDiscoveryRecord(value) {
    if (!value || typeof value !== 'object')
        return false;
    const record = value;
    return typeof record.name === 'string'
        && Array.isArray(record.capabilities)
        && typeof record.backend_provider === 'string'
        && typeof record.backend_model === 'string'
        && Array.isArray(record.supported_agent_params);
}
