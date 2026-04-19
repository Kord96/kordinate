import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import type { AgentDiscoveryRecord, AgentVariantSummary, LogicalAgentRecord } from './types.js'

export interface DiscoveryRegistry {
  load: () => Promise<void>
  list: () => AgentDiscoveryRecord[]
  listLogical: () => LogicalAgentRecord[]
  get: (name: string) => AgentDiscoveryRecord | undefined
  getLogical: (name: string) => LogicalAgentRecord | undefined
  register: (record: AgentDiscoveryRecord) => Promise<AgentDiscoveryRecord>
  compact: (record: AgentDiscoveryRecord) => AgentDiscoveryRecord
  compactLogical: (record: LogicalAgentRecord) => LogicalAgentRecord
  resolveTarget: (name: string, options?: { variant?: string; backend_model?: string }) => AgentDiscoveryRecord | undefined
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
  const legacyNameMap: Record<string, string> = {
    'augur-gemini-pro': 'augur-gemini-31-pro',
    'sauron-sonnet': 'sauron-gpt53-codex',
  }

  function canonicalizeName(name: string): string {
    return legacyNameMap[name] ?? name
  }

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

  function logicalNameFor(record: AgentDiscoveryRecord): string {
    return record.specialization?.trim() || record.name
  }

  function preferredVariantRank(record: AgentDiscoveryRecord): number {
    const logicalName = logicalNameFor(record)
    const preferredByLogical: Record<string, string[]> = {
      alfred: ['alfred-gpt-oss-20b'],
      augur: ['augur-opus', 'augur-gpt54', 'augur-gemini-31-pro', 'augur-deepseek-v3p2', 'augur-glm5'],
      charon: ['charon-gpt53-codex'],
      generic: ['generic-opus'],
      sauron: ['sauron-gpt53-codex'],
    }
    const preferred = preferredByLogical[logicalName] ?? []
    const exactIndex = preferred.indexOf(record.name)
    if (exactIndex >= 0) return exactIndex
    const modelIndex = preferred.findIndex(name => name.endsWith(`-${record.backend_model.replaceAll('.', '').replaceAll('/', '-')}`))
    if (modelIndex >= 0) return modelIndex + preferred.length
    return preferred.length + 100
  }

  function compareVariants(a: AgentDiscoveryRecord, b: AgentDiscoveryRecord): number {
    if (a.active !== b.active) return a.active ? -1 : 1
    const rankDiff = preferredVariantRank(a) - preferredVariantRank(b)
    if (rankDiff !== 0) return rankDiff
    return a.name.localeCompare(b.name)
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

  function toVariantSummary(record: AgentDiscoveryRecord): AgentVariantSummary {
    return {
      name: record.name,
      backend_provider: record.backend_provider,
      backend_model: record.backend_model,
      active: record.active,
      runtime: record.runtime,
    }
  }

  function listLogical(): LogicalAgentRecord[] {
    const grouped = new Map<string, AgentDiscoveryRecord[]>()
    for (const record of list()) {
      const logicalName = logicalNameFor(record)
      const existing = grouped.get(logicalName) ?? []
      existing.push(record)
      grouped.set(logicalName, existing)
    }

    const logicalAgents: LogicalAgentRecord[] = []
    for (const [name, variants] of grouped.entries()) {
      variants.sort(compareVariants)
      const defaultVariant = variants[0]
      const capabilities = [...new Set(variants.flatMap(record => record.capabilities))]
      const supportedAgentParams = [...new Set(variants.flatMap(record => record.supported_agent_params))]
      logicalAgents.push({
        name,
        capabilities,
        backend_provider: defaultVariant?.backend_provider,
        backend_model: defaultVariant?.backend_model,
        supported_agent_params: supportedAgentParams,
        active: variants.some(record => record.active),
        default_variant: defaultVariant?.name,
        variants: variants.map(toVariantSummary),
      })
    }
    logicalAgents.sort((a, b) => a.name.localeCompare(b.name))
    return logicalAgents
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

  function compactLogical(record: LogicalAgentRecord): LogicalAgentRecord {
    return {
      name: record.name,
      capabilities: record.capabilities,
      backend_provider: record.backend_provider,
      backend_model: record.backend_model,
      supported_agent_params: record.supported_agent_params,
      active: record.active,
      default_variant: record.default_variant,
      variants: record.variants,
    }
  }

  function get(name: string): AgentDiscoveryRecord | undefined {
    const canonicalName = canonicalizeName(name)
    return list().find(item => item.name === canonicalName)
  }

  function getLogical(name: string): LogicalAgentRecord | undefined {
    const canonicalName = canonicalizeName(name)
    return listLogical().find(item => item.name === canonicalName)
  }

  function resolveTarget(name: string, options?: { variant?: string; backend_model?: string }): AgentDiscoveryRecord | undefined {
    const canonicalName = canonicalizeName(name)
    const exact = get(canonicalName)
    const requestedVariant = options?.variant?.trim()
    const requestedModel = options?.backend_model?.trim()

    if (requestedVariant) {
      const variant = get(canonicalizeName(requestedVariant))
      if (!variant) return undefined
      if (exact) {
        return exact.name === variant.name ? variant : undefined
      }
      return logicalNameFor(variant) === canonicalName ? variant : undefined
    }

    if (exact && !requestedModel) {
      return exact
    }

    const logical = getLogical(canonicalName)
    if (!logical) {
      return requestedModel && exact?.backend_model === requestedModel ? exact : exact
    }

    const variants = list()
      .filter(record => logicalNameFor(record) === logical.name)
      .sort(compareVariants)

    if (requestedModel) {
      return variants.find(record => record.backend_model === requestedModel)
    }

    return variants[0]
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
    listLogical,
    get,
    getLogical,
    register,
    compact,
    compactLogical,
    resolveTarget,
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
