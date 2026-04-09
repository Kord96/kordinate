import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import type { AgentDiscoveryRecord } from './types.js'

export interface DiscoveryRegistry {
  load: () => Promise<void>
  list: () => AgentDiscoveryRecord[]
  get: (name: string) => AgentDiscoveryRecord | undefined
  register: (record: AgentDiscoveryRecord) => Promise<AgentDiscoveryRecord>
  compact: (record: AgentDiscoveryRecord) => AgentDiscoveryRecord
}

export function createDiscoveryRegistry(input?: {
  statePath?: string
  catalogPath?: string
  ttlMs?: number
}): DiscoveryRegistry {
  const statePath = input?.statePath ?? '.daemon-state/discovery-agents.json'
  const catalogPath = input?.catalogPath ?? '/app/agents/charon/skills/platform/manifests/base/discovery-catalog.json'
  const ttlMs = input?.ttlMs ?? 120000
  const registry = new Map<string, AgentDiscoveryRecord>()
  const catalog = new Map<string, AgentDiscoveryRecord>()

  function sanitizeRecord(record: AgentDiscoveryRecord): AgentDiscoveryRecord {
    return {
      ...record,
      active: record.active ?? false,
    }
  }

  async function loadState(): Promise<void> {
    try {
      const raw = await readFile(statePath, 'utf8')
      const parsed = JSON.parse(raw) as AgentDiscoveryRecord[]
      const now = Date.now()
      for (const record of parsed) {
        if (record.last_seen_at && now - Date.parse(record.last_seen_at) <= ttlMs) {
          registry.set(record.name, record)
        }
      }
    } catch {
      // ignore missing state
    }
  }

  async function loadCatalog(): Promise<void> {
    try {
      const raw = await readFile(catalogPath, 'utf8')
      const parsed = JSON.parse(raw) as AgentDiscoveryRecord[]
      for (const record of parsed) {
        catalog.set(record.name, sanitizeRecord(record))
      }
    } catch {
      // ignore missing catalog
    }
  }

  async function persistState(): Promise<void> {
    await mkdir(dirname(statePath), { recursive: true })
    const payload = JSON.stringify([...registry.values()], null, 2) + '\n'
    await writeFile(statePath, payload, 'utf8')
  }

  function list(): AgentDiscoveryRecord[] {
    const now = Date.now()
    const merged = new Map<string, AgentDiscoveryRecord>(catalog)
    for (const [name, record] of registry.entries()) {
      if (record.last_seen_at && now - Date.parse(record.last_seen_at) > ttlMs) {
        registry.delete(name)
        continue
      }
      const base = merged.get(name)
      merged.set(name, {
        ...(base ?? {}),
        ...record,
        active: true,
      })
    }
    const records = [...merged.values()].map(record => record.active ? record : { ...record, active: false })
    records.sort((a, b) => a.name.localeCompare(b.name))
    return records
  }

  function compact(record: AgentDiscoveryRecord): AgentDiscoveryRecord {
    return {
      name: record.name,
      capabilities: record.capabilities,
      backend_provider: record.backend_provider,
      backend_model: record.backend_model,
      supported_agent_params: record.supported_agent_params,
      active: record.active,
    }
  }

  function get(name: string): AgentDiscoveryRecord | undefined {
    return list().find(item => item.name === name)
  }

  async function register(record: AgentDiscoveryRecord): Promise<AgentDiscoveryRecord> {
    const now = new Date().toISOString()
    const previous = registry.get(record.name)
    const normalized: AgentDiscoveryRecord = {
      ...record,
      registered_at: previous?.registered_at ?? now,
      last_seen_at: now,
      active: true,
    }
    registry.set(normalized.name, normalized)
    await persistState()
    return normalized
  }

  return {
    load: async () => {
      await loadCatalog()
      await loadState()
    },
    list,
    get,
    register,
    compact,
  }
}

export function isAgentDiscoveryRecord(value: unknown): value is AgentDiscoveryRecord {
  if (!value || typeof value !== 'object') return false
  const record = value as Partial<AgentDiscoveryRecord>
  return typeof record.name === 'string'
    && Array.isArray(record.capabilities)
    && typeof record.backend_provider === 'string'
    && typeof record.backend_model === 'string'
    && Array.isArray(record.supported_agent_params)
}
