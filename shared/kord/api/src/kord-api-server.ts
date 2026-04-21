import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { request as httpsRequest } from 'node:https'
import { createServer } from 'node:http'
import { Kafka, Partitioners } from 'kafkajs'
import { loadAugurAnalysisDetails, loadAugurBase, loadAugurProjectSummary, loadAugurReflections, resolveAugurProjectNames, listAugurAnalysisSummaries } from './augur-base.js'
import { createDiscoveryRegistry, isAgentDiscoveryRecord } from './discovery-registry.js'
import { log } from './log.js'
import type { AgentMessage, ProgressMessage, RequestMessage, RequestTranscriptEvent, ResponseMessage } from './types.js'
import { applyFailureToRequestRecord, applyResponseToRequestRecord, createRequestRecord, type RequestRecord } from './request-model.js'
import { buildFinalTranscriptEvent, buildTranscriptEventFromGateway, buildTranscriptEventFromProgress, coalesceTranscriptEvent, summarizeValue } from './request-transcript.js'
import { canonicalizeWorkingDir } from './working-dir.js'

const host = process.env.KORD_API_HOST ?? '0.0.0.0'
const port = Number.parseInt(process.env.KORD_API_PORT ?? '9091', 10)
const statePath = process.env.DISCOVERY_STATE_PATH ?? '.daemon-state/discovery-agents.json'
const catalogPath = process.env.DISCOVERY_CATALOG_PATH ?? '/app/agents/charon/skills/platform/manifests/base/discovery-catalog.json'
const ttlMs = Number.parseInt(process.env.DISCOVERY_TTL_MS ?? '120000', 10)
const kafkaBrokers = (process.env.KAFKA_BROKERS ?? 'localhost:9092').split(',')
const replyTopic = process.env.KORD_API_REPLY_TOPIC ?? 'kord-api-replies'
const progressTopic = process.env.KORD_API_PROGRESS_TOPIC ?? process.env.PROGRESS_TOPIC ?? 'kord-progress'
const defaultTimeoutMs = Number.parseInt(process.env.KORD_API_DEFAULT_TIMEOUT_MS ?? '1800000', 10)
const kubernetesHost = process.env.KUBERNETES_SERVICE_HOST ?? 'kubernetes.default.svc'
const kubernetesPort = Number.parseInt(process.env.KUBERNETES_SERVICE_PORT_HTTPS ?? '443', 10)
const kubernetesNamespacePath = process.env.KUBERNETES_NAMESPACE_PATH ?? '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
const kubernetesTokenPath = process.env.KUBERNETES_TOKEN_PATH ?? '/var/run/secrets/kubernetes.io/serviceaccount/token'
const kubernetesCaPath = process.env.KUBERNETES_CA_PATH ?? '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
const agentSpecPath = process.env.AGENT_SPEC_PATH ?? '/app/agents/charon/skills/platform/agent-spec.yaml'
const augurProjectsRoot = process.env.AUGUR_MEMORY_PROJECTS_ROOT ?? '/kord/agents/augur-local-codex/memory/projects'
const allowedApiKeys = new Set(
  [
    ...(process.env.KORD_API_KEYS ?? '').split(','),
    process.env.KORD_API_KEY ?? '',
  ].map(value => value.trim()).filter(Boolean),
)

const registry = createDiscoveryRegistry({ statePath, catalogPath, ttlMs })
const kafka = new Kafka({
  clientId: 'kord-api',
  brokers: kafkaBrokers,
})
const producer = kafka.producer({ createPartitioner: Partitioners.LegacyPartitioner })
const consumer = kafka.consumer({ groupId: 'kord-api' })
const pending = new Map<string, {
  agent: string
  resolve: (value: ResponseMessage) => void
  reject: (error: Error) => void
  timer: NodeJS.Timeout
  timeout_ms: number
  queue_started_at: number
  execution_started_at?: number
}>()
const requestStreams = new Map<string, Set<import('node:http').ServerResponse>>()
const requestTranscriptStreams = new Map<string, Set<import('node:http').ServerResponse>>()
const requests = new Map<string, RequestRecord>()
let ready = false
let kubernetesNamespacePromise: Promise<string> | undefined
let kubernetesTokenPromise: Promise<string> | undefined
let kubernetesCaPromise: Promise<Buffer> | undefined

function resolveTimeoutMs(record: { name: string; default_timeout_ms?: number }, body: {
  prompt: string
  timeout_ms?: number
}): number {
  if (typeof body.timeout_ms === 'number') return body.timeout_ms
  if (typeof record.default_timeout_ms === 'number' && Number.isFinite(record.default_timeout_ms) && record.default_timeout_ms > 0) {
    return record.default_timeout_ms
  }
  return defaultTimeoutMs
}

function json(res: import('node:http').ServerResponse, statusCode: number, payload: unknown): void {
  res.statusCode = statusCode
  res.setHeader('content-type', 'application/json')
  res.end(JSON.stringify(payload))
}

function writeSseEvent(res: import('node:http').ServerResponse, event: string, data: unknown): void {
  res.write(`event: ${event}\n`)
  res.write(`data: ${JSON.stringify(data)}\n\n`)
}

function extractApiKey(req: import('node:http').IncomingMessage): string | undefined {
  const direct = req.headers['x-api-key']
  if (typeof direct === 'string' && direct.trim()) return direct.trim()
  const auth = req.headers.authorization
  if (!auth) return undefined
  const match = auth.match(/^Bearer\s+(.+)$/i)
  return match?.[1]?.trim()
}

function requireAuth(req: import('node:http').IncomingMessage, res: import('node:http').ServerResponse): boolean {
  if (allowedApiKeys.size === 0) {
    json(res, 503, { error: 'kord api auth is not configured' })
    return false
  }
  const apiKey = extractApiKey(req)
  if (!apiKey || !allowedApiKeys.has(apiKey)) {
    json(res, 401, { error: 'unauthorized' })
    return false
  }
  return true
}

async function parseBody(req: import('node:http').IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = []
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk))
  }
  if (chunks.length === 0) return undefined
  return JSON.parse(Buffer.concat(chunks).toString('utf8'))
}

async function getKubernetesNamespace(): Promise<string> {
  kubernetesNamespacePromise ??= readFile(kubernetesNamespacePath, 'utf8').then(value => value.trim())
  return kubernetesNamespacePromise
}

async function getKubernetesToken(): Promise<string> {
  kubernetesTokenPromise ??= readFile(kubernetesTokenPath, 'utf8').then(value => value.trim())
  return kubernetesTokenPromise
}

async function getKubernetesCa(): Promise<Buffer> {
  kubernetesCaPromise ??= readFile(kubernetesCaPath)
  return kubernetesCaPromise
}

async function kubernetesGet(path: string): Promise<{ statusCode: number, body: string }> {
  const [token, ca] = await Promise.all([getKubernetesToken(), getKubernetesCa()])
  return new Promise((resolve, reject) => {
    const req = httpsRequest({
      host: kubernetesHost,
      port: kubernetesPort,
      path,
      method: 'GET',
      ca,
      headers: {
        authorization: `Bearer ${token}`,
        accept: 'application/json',
      },
    }, res => {
      const chunks: Buffer[] = []
      res.on('data', chunk => chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)))
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode ?? 500,
          body: Buffer.concat(chunks).toString('utf8'),
        })
      })
    })
    req.on('error', reject)
    req.end()
  })
}

async function kubernetesGetJson(path: string): Promise<unknown> {
  const response = await kubernetesGet(path)
  if (response.statusCode < 200 || response.statusCode >= 300) {
    throw new Error(`kubernetes api request failed: ${response.statusCode} ${response.body}`)
  }
  return JSON.parse(response.body)
}

function coercePositiveInt(value: string | null, fallback: number): number {
  if (!value) return fallback
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

function getLogTargetLabelSelector(agent: string): string {
  return agent === 'kord-api'
    ? 'app=kord-api'
    : `app=kord-agent,agent=${agent}`
}

async function getLatestPodNameForAgent(agent: string): Promise<string> {
  const namespace = await getKubernetesNamespace()
  const selector = encodeURIComponent(getLogTargetLabelSelector(agent))
  const payload = await kubernetesGetJson(`/api/v1/namespaces/${encodeURIComponent(namespace)}/pods?labelSelector=${selector}`)
  if (!payload || typeof payload !== 'object' || !Array.isArray((payload as { items?: unknown[] }).items)) {
    throw new Error(`invalid kubernetes pod list for agent '${agent}'`)
  }
  const items = (payload as { items: Array<Record<string, unknown>> }).items
  const runningPods = items.filter(item => {
    const phase = (item.status as { phase?: string } | undefined)?.phase
    return phase === 'Running'
  })
  const pods = runningPods.length > 0 ? runningPods : items
  if (pods.length === 0) {
    throw new Error(`no pods found for agent '${agent}'`)
  }
  pods.sort((left, right) => {
    const leftTime = Date.parse((left.metadata as { creationTimestamp?: string } | undefined)?.creationTimestamp ?? '')
    const rightTime = Date.parse((right.metadata as { creationTimestamp?: string } | undefined)?.creationTimestamp ?? '')
    return rightTime - leftTime
  })
  const podName = (pods[0].metadata as { name?: string } | undefined)?.name
  if (!podName) {
    throw new Error(`pod metadata missing name for agent '${agent}'`)
  }
  return podName
}

async function getAgentLogs(agent: string, options: {
  tail_lines: number
  since_seconds: number
  container?: string
}): Promise<Record<string, unknown>> {
  const namespace = await getKubernetesNamespace()
  const podName = await getLatestPodNameForAgent(agent)
  const query = new URLSearchParams()
  query.set('tailLines', String(options.tail_lines))
  query.set('sinceSeconds', String(options.since_seconds))
  if (options.container) query.set('container', options.container)
  const response = await kubernetesGet(`/api/v1/namespaces/${encodeURIComponent(namespace)}/pods/${encodeURIComponent(podName)}/log?${query.toString()}`)
  if (response.statusCode < 200 || response.statusCode >= 300) {
    throw new Error(`kubernetes pod log request failed: ${response.statusCode} ${response.body}`)
  }
  return {
    agent,
    pod: podName,
    container: options.container ?? null,
    since_seconds: options.since_seconds,
    tail_lines: options.tail_lines,
    logs: response.body,
  }
}

function filterLogLines(text: string, filters: string[]): string {
  if (filters.length === 0) return text
  const lines = text.split('\n')
  return lines.filter(line => filters.some(filter => filter && line.includes(filter))).join('\n')
}

type AgentBundleSelection = {
  flavor: string
  memory_bundle?: string
  skill_bundle?: string
  runtime_bundle?: string
}

let parsedAgentBundlesPromise: Promise<Map<string, AgentBundleSelection>> | undefined

async function parseAgentBundleSelections(): Promise<Map<string, AgentBundleSelection>> {
  parsedAgentBundlesPromise ??= readFile(agentSpecPath, 'utf8').then(text => {
    const selections = new Map<string, AgentBundleSelection>()
    const lines = text.split('\n')
    let currentName: string | undefined
    let currentFlavor: string | undefined
    let memoryBundle: string | undefined
    let skillBundle: string | undefined
    let runtimeBundle: string | undefined
    let inCreation = false

    function commitCurrent(): void {
      if (!currentName || !currentFlavor) return
      selections.set(currentName, {
        flavor: currentFlavor,
        memory_bundle: memoryBundle,
        skill_bundle: skillBundle,
        runtime_bundle: runtimeBundle,
      })
    }

    for (const line of lines) {
      const nameMatch = line.match(/^  - name:\s+(.+)\s*$/)
      if (nameMatch) {
        commitCurrent()
        currentName = nameMatch[1].trim()
        currentFlavor = undefined
        memoryBundle = undefined
        skillBundle = undefined
        runtimeBundle = undefined
        inCreation = false
        continue
      }
      if (!currentName) continue
      const flavorMatch = line.match(/^    flavor:\s+(.+)\s*$/)
      if (flavorMatch) {
        currentFlavor = flavorMatch[1].trim()
        continue
      }
      if (/^    creation:\s*$/.test(line)) {
        inCreation = true
        continue
      }
      if (/^    [a-z]/.test(line) && !/^    creation:\s*$/.test(line)) {
        inCreation = false
      }
      if (!inCreation) continue
      const memoryMatch = line.match(/^      memory_bundle:\s+(.+)\s*$/)
      if (memoryMatch) {
        memoryBundle = memoryMatch[1].trim()
        continue
      }
      const skillMatch = line.match(/^      skill_bundle:\s+(.+)\s*$/)
      if (skillMatch) {
        skillBundle = skillMatch[1].trim()
        continue
      }
      const runtimeMatch = line.match(/^      runtime_bundle:\s+(.+)\s*$/)
      if (runtimeMatch) {
        runtimeBundle = runtimeMatch[1].trim()
      }
    }
    commitCurrent()
    return selections
  })
  return parsedAgentBundlesPromise
}

async function readBundleFile(baseDir: string, category: 'memory' | 'skill' | 'runtime', bundleName?: string): Promise<{ name: string | null, path: string | null, content: string | null }> {
  if (!bundleName) {
    return { name: null, path: null, content: null }
  }
  const candidates = category === 'runtime'
    ? ['md', 'json']
    : ['md']
  for (const ext of candidates) {
    const relativePath = join('agents', baseDir, 'bundles', category, `${bundleName}.${ext}`)
    try {
      const content = await readFile(join('/app', relativePath), 'utf8')
      return {
        name: bundleName,
        path: `/app/${relativePath}`,
        content,
      }
    } catch {
      continue
    }
  }
  return {
    name: bundleName,
    path: null,
    content: null,
  }
}

async function getAgentBundles(agentName: string): Promise<Record<string, unknown> | null> {
  const selections = await parseAgentBundleSelections()
  const selection = selections.get(agentName)
  if (!selection) return null
  const [memory, skill, runtime] = await Promise.all([
    readBundleFile(selection.flavor, 'memory', selection.memory_bundle),
    readBundleFile(selection.flavor, 'skill', selection.skill_bundle),
    readBundleFile(selection.flavor, 'runtime', selection.runtime_bundle),
  ])
  return {
    flavor: selection.flavor,
    memory_bundle: memory,
    skill_bundle: skill,
    runtime_bundle: runtime,
  }
}

async function getE2eLogs(name: string, options: {
  variant?: string
  backend_model?: string
  request_id?: string
  correlation_id?: string
  since_seconds: number
  tail_lines: number
  include_bundles?: boolean
}): Promise<Record<string, unknown>> {
  const record = registry.resolveTarget(name, {
    variant: options.variant,
    backend_model: options.backend_model,
  })
  if (!record) {
    throw new Error(`agent '${name}' could not be resolved`)
  }

  const filters = [
    options.request_id,
    options.correlation_id,
  ].filter((value): value is string => typeof value === 'string' && value.length > 0)

  const [agentLogs, apiLogs] = await Promise.all([
    getAgentLogs(record.name, {
      tail_lines: options.tail_lines,
      since_seconds: options.since_seconds,
    }),
    getAgentLogs('kord-api', {
      tail_lines: options.tail_lines,
      since_seconds: options.since_seconds,
    }),
  ])

  let requestRecord: Record<string, unknown> | undefined
  if (options.request_id) {
    const record = requests.get(options.request_id)
    if (record) {
      requestRecord = record as unknown as Record<string, unknown>
    }
  }

  const bundles = options.include_bundles ? await getAgentBundles(record.name) : undefined

  return {
    requested_agent: name,
    requested_variant: options.variant ?? null,
    requested_backend_model: options.backend_model ?? null,
    resolved_agent: record.name,
    request_id: options.request_id ?? null,
    correlation_id: options.correlation_id ?? null,
    request: requestRecord ?? null,
    kord_api: {
      pod: apiLogs.pod,
      logs: filterLogLines(String(apiLogs.logs ?? ''), filters),
    },
    agent: {
      name: record.name,
      pod: agentLogs.pod,
      logs: filterLogLines(String(agentLogs.logs ?? ''), filters),
    },
    ...(options.include_bundles ? { bundles: bundles ?? null } : {}),
  }
}

function isPromptBody(value: unknown): value is {
  prompt: string
  working_dir?: string
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
  session_id?: string
  async?: boolean
  variant?: string
  backend_model?: string
  verbose?: boolean
  stream?: boolean
  debug?: boolean
} {
  if (!value || typeof value !== 'object') return false
  const body = value as Record<string, unknown>
  return typeof body.prompt === 'string'
    && (body.working_dir === undefined || typeof body.working_dir === 'string')
    && (body.timeout_ms === undefined || typeof body.timeout_ms === 'number')
    && (body.reflect === undefined || typeof body.reflect === 'boolean')
    && (body.reflection_prompt === undefined || typeof body.reflection_prompt === 'string')
    && (body.agent_params === undefined || typeof body.agent_params === 'object')
    && (body.session_id === undefined || typeof body.session_id === 'string')
    && (body.async === undefined || typeof body.async === 'boolean')
    && (body.variant === undefined || typeof body.variant === 'string')
    && (body.backend_model === undefined || typeof body.backend_model === 'string')
    && (body.verbose === undefined || typeof body.verbose === 'boolean')
    && (body.stream === undefined || typeof body.stream === 'boolean')
    && (body.debug === undefined || typeof body.debug === 'boolean')
}

function recordRequestEvent(requestId: string, eventRecord: Record<string, unknown>): void {
  const existing = requests.get(requestId)
  if (!existing) return
  const events = existing.debug?.events ?? []
  events.push(eventRecord)
  existing.debug = { events: events.slice(-200) }
  requests.set(requestId, existing)
  const subscribers = requestStreams.get(requestId)
  if (!subscribers) return
  for (const subscriber of subscribers) {
    writeSseEvent(subscriber, 'request.event', eventRecord)
  }
}

function recordTranscriptEvent(requestId: string, event: RequestTranscriptEvent): void {
  const existing = requests.get(requestId)
  if (!existing) return
  const events = existing.transcript?.events ?? []
  if (coalesceTranscriptEvent(events.at(-1), event)) return
  const nextEvents = [...events, event].slice(-200)
  existing.transcript = { events: nextEvents }
  existing.last_progress_at = event.at
  if (event.type !== 'tool.started' && event.type !== 'tool.finished') {
    existing.last_meaningful_event = event
  }
  requests.set(requestId, existing)

  const subscribers = requestTranscriptStreams.get(requestId)
  if (!subscribers) return
  for (const subscriber of subscribers) {
    writeSseEvent(subscriber, 'transcript.event', event)
  }
}

function pushRequestEvent(requestId: string, event: string, details: Record<string, unknown> = {}): void {
  const eventRecord = {
    event,
    timestamp: new Date().toISOString(),
    source: 'gateway',
    ...details,
  }
  recordRequestEvent(requestId, eventRecord)
  const transcriptEvent = buildTranscriptEventFromGateway(requestId, eventRecord)
  if (transcriptEvent) recordTranscriptEvent(requestId, transcriptEvent)
}

function recordProgressEvent(message: ProgressMessage): void {
  const eventRecord = {
    event: message.event.kind,
    timestamp: message.timestamp,
    source: message.event.source,
    sender: message.sender,
    runtime: message.event.runtime ?? null,
    model: message.event.model ?? null,
    session_id: message.event.session_id ?? null,
    structured_log_path: message.event.structured_log_path ?? null,
    payload: message.event.payload ?? null,
  }
  recordRequestEvent(message.correlation_id, eventRecord)
  noteRequestActivity(message.correlation_id, message.timestamp)
  const transcriptEvent = buildTranscriptEventFromProgress(message)
  if (transcriptEvent) recordTranscriptEvent(message.correlation_id, transcriptEvent)
}

function openRequestEventStream(req: import('node:http').IncomingMessage, res: import('node:http').ServerResponse, requestId: string): void {
  const requestRecord = requests.get(requestId)
  if (!requestRecord) {
    json(res, 404, { error: `request '${requestId}' not found` })
    return
  }
  res.writeHead(200, {
    'content-type': 'text/event-stream',
    'cache-control': 'no-cache, no-transform',
    connection: 'keep-alive',
  })
  const subscribers = requestStreams.get(requestId) ?? new Set<import('node:http').ServerResponse>()
  subscribers.add(res)
  requestStreams.set(requestId, subscribers)
  writeSseEvent(res, 'request.snapshot', {
    request_id: requestId,
    status: requestRecord.status,
    created_at: requestRecord.created_at,
    completed_at: requestRecord.completed_at ?? null,
    events: requestRecord.debug?.events ?? [],
  })
  const heartbeat = setInterval(() => {
    res.write(': keepalive\n\n')
  }, 15000)
  const cleanup = () => {
    clearInterval(heartbeat)
    const current = requestStreams.get(requestId)
    if (!current) return
    current.delete(res)
    if (current.size === 0) requestStreams.delete(requestId)
  }
  req.on('close', cleanup)
  res.on('close', cleanup)
}

function openRequestTranscriptStream(req: import('node:http').IncomingMessage, res: import('node:http').ServerResponse, requestId: string): void {
  const requestRecord = requests.get(requestId)
  if (!requestRecord) {
    json(res, 404, { error: `request '${requestId}' not found` })
    return
  }
  res.writeHead(200, {
    'content-type': 'text/event-stream',
    'cache-control': 'no-cache, no-transform',
    connection: 'keep-alive',
  })
  const subscribers = requestTranscriptStreams.get(requestId) ?? new Set<import('node:http').ServerResponse>()
  subscribers.add(res)
  requestTranscriptStreams.set(requestId, subscribers)
  writeSseEvent(res, 'transcript.snapshot', {
    request_id: requestId,
    status: requestRecord.status,
    created_at: requestRecord.created_at,
    completed_at: requestRecord.completed_at ?? null,
    events: requestRecord.transcript?.events ?? [],
  })
  const heartbeat = setInterval(() => {
    res.write(': keepalive\n\n')
  }, 15000)
  const cleanup = () => {
    clearInterval(heartbeat)
    const current = requestTranscriptStreams.get(requestId)
    if (!current) return
    current.delete(res)
    if (current.size === 0) requestTranscriptStreams.delete(requestId)
  }
  req.on('close', cleanup)
  res.on('close', cleanup)
}

function buildPendingTimeoutError(correlationId: string): Error {
  return new Error(`timed out waiting for ${correlationId}`)
}

function armPendingTimer(waiter: {
  agent: string
  resolve: (value: ResponseMessage) => void
  reject: (error: Error) => void
  timer: NodeJS.Timeout
  timeout_ms: number
  queue_started_at: number
  execution_started_at?: number
}, correlationId: string, timeoutMs: number): void {
  if (!(timeoutMs > 0) || !Number.isFinite(timeoutMs)) {
    waiter.timer = setTimeout(() => undefined, 0)
    clearTimeout(waiter.timer)
    return
  }
  waiter.timer = setTimeout(() => {
    pending.delete(correlationId)
    log('prompt_timeout', {
      agent: waiter.agent,
      correlation_id: correlationId,
      timeout_ms: timeoutMs,
      phase: waiter.execution_started_at ? 'execution' : 'queue',
    })
    pushRequestEvent(correlationId, 'prompt_timeout', {
      timeout_ms: timeoutMs,
      phase: waiter.execution_started_at ? 'execution' : 'queue',
    })
    waiter.reject(buildPendingTimeoutError(correlationId))
  }, timeoutMs)
}

function noteRequestActivity(correlationId: string, startedAt?: string): void {
  const waiter = pending.get(correlationId)
  if (!waiter) return
  clearTimeout(waiter.timer)
  const activityAt = startedAt ? Date.parse(startedAt) || Date.now() : Date.now()
  const firstExecutionStart = !waiter.execution_started_at
  waiter.execution_started_at ??= activityAt
  armPendingTimer(waiter, correlationId, waiter.timeout_ms)
  if (firstExecutionStart) {
    pushRequestEvent(correlationId, 'request_picked_up', {
      queue_ms: Math.max(0, waiter.execution_started_at - waiter.queue_started_at),
    })
  }
}

function deferReply(correlationId: string, agent: string, timeoutMs: number): Promise<ResponseMessage> {
  return new Promise((resolve, reject) => {
    const waiter = {
      agent,
      resolve,
      reject,
      timer: setTimeout(() => undefined, 0),
      timeout_ms: timeoutMs,
      queue_started_at: Date.now(),
      execution_started_at: undefined as number | undefined,
    }
    clearTimeout(waiter.timer)
    armPendingTimer(waiter, correlationId, timeoutMs)
    pending.set(correlationId, waiter)
  })
}

async function sendPrompt(agent: string, body: {
  prompt: string
  working_dir?: string
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
  session_id?: string
}, requestId?: string, options?: {
  disable_timeout?: boolean
}): Promise<{ correlationId: string, reply: Promise<ResponseMessage> }> {
  const correlationId = requestId ?? `${agent}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
  const timeoutMs = resolveTimeoutMs({ name: agent }, body)
  const runtimeTimeoutMs = options?.disable_timeout ? undefined : timeoutMs
  const workingDir = canonicalizeWorkingDir(body.working_dir)
  const request: RequestMessage = {
    type: 'request',
    sender: replyTopic,
    correlation_id: correlationId,
    prompt: body.prompt,
    working_dir: workingDir,
    timeout_ms: runtimeTimeoutMs,
    reflect: body.reflect,
    reflection_prompt: body.reflection_prompt,
    agent_params: body.agent_params,
    session_id: body.session_id,
  }
  const reply = deferReply(correlationId, agent, options?.disable_timeout ? 0 : timeoutMs)
  log('prompt_publish_start', {
    agent,
    correlation_id: correlationId,
    timeout_ms: options?.disable_timeout ? null : timeoutMs,
    session_id: body.session_id ?? null,
  })
  await producer.send({
    topic: agent,
    messages: [{
      key: body.session_id ?? correlationId,
      value: JSON.stringify(request satisfies AgentMessage),
    }],
  })
  log('prompt_publish_complete', {
    agent,
    correlation_id: correlationId,
    topic: agent,
  })
  return { correlationId, reply }
}

function completeRequest(requestId: string, response: ResponseMessage): void {
  const existing = requests.get(requestId)
  if (!existing) return
  log('request_complete', {
    request_id: requestId,
    agent: existing.agent,
    correlation_id: response.correlation_id,
    status: response.status,
  })
  const alreadyTimedOut = existing.status === 'timed_out'
  const nextRecord = applyResponseToRequestRecord(existing, response, new Date().toISOString())
  requests.set(requestId, nextRecord)
  pushRequestEvent(requestId, 'request_complete', {
    correlation_id: response.correlation_id,
    status: response.status,
  })
  recordTranscriptEvent(requestId, buildFinalTranscriptEvent(requestId, existing.agent, alreadyTimedOut ? 'timed_out' : response.status, response.output))
}

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? '/', `http://${req.headers.host ?? 'localhost'}`)

    if (req.method === 'GET' && url.pathname === '/health') {
      json(res, ready ? 200 : 503, { ok: ready, agents: registry.list().length })
      return
    }

    if (req.method === 'POST' && url.pathname === '/register') {
      const body = await parseBody(req)
      if (!isAgentDiscoveryRecord(body)) {
        json(res, 400, { error: 'invalid agent discovery record' })
        return
      }
      const record = await registry.register(body)
      json(res, 200, record)
      return
    }

    if (!requireAuth(req, res)) {
      return
    }

    if (req.method === 'GET' && url.pathname === '/agents') {
      const verbose = url.searchParams.get('verbose') === '1'
      const view = url.searchParams.get('view')
      const variants = view === 'variants' || url.searchParams.get('variants') === '1'
      const agents = variants
        ? registry.list().map(record => verbose ? record : registry.compact(record))
        : registry.listLogical().map(record => verbose ? record : registry.compactLogical(record))
      json(res, 200, { agents })
      return
    }

    if (req.method === 'GET' && url.pathname.startsWith('/agents/') && url.pathname.endsWith('/logs')) {
      const suffix = url.pathname.slice('/agents/'.length)
      const name = decodeURIComponent(suffix.slice(0, -'/logs'.length))
      const variant = url.searchParams.get('variant') ?? undefined
      const backendModel = url.searchParams.get('backend_model') ?? undefined
      const record = registry.resolveTarget(name, {
        variant,
        backend_model: backendModel,
      })
      if (!record) {
        json(res, 404, {
          error: `agent '${name}' could not be resolved`,
          requested_variant: variant ?? null,
          requested_backend_model: backendModel ?? null,
        })
        return
      }
      const tailLines = coercePositiveInt(url.searchParams.get('tail_lines'), 200)
      const sinceSeconds = coercePositiveInt(url.searchParams.get('since_seconds'), 900)
      const container = url.searchParams.get('container') ?? undefined
      const payload = await getAgentLogs(record.name, {
        tail_lines: tailLines,
        since_seconds: sinceSeconds,
        container,
      })
      json(res, 200, {
        requested_agent: name,
        requested_variant: variant ?? null,
        requested_backend_model: backendModel ?? null,
        resolved_agent: record.name,
        ...payload,
      })
      return
    }

    if (req.method === 'GET' && url.pathname === '/logs/e2e') {
      const agent = url.searchParams.get('agent')
      if (!agent) {
        json(res, 400, { error: 'agent is required' })
        return
      }
      const payload = await getE2eLogs(agent, {
        variant: url.searchParams.get('variant') ?? undefined,
        backend_model: url.searchParams.get('backend_model') ?? undefined,
        request_id: url.searchParams.get('request_id') ?? undefined,
        correlation_id: url.searchParams.get('correlation_id') ?? undefined,
        tail_lines: coercePositiveInt(url.searchParams.get('tail_lines'), 200),
        since_seconds: coercePositiveInt(url.searchParams.get('since_seconds'), 900),
        include_bundles: url.searchParams.get('include_bundles') === '1',
      })
      json(res, 200, payload)
      return
    }

    if (req.method === 'GET' && url.pathname === '/augur/projects') {
      const projectNames = await resolveAugurProjectNames(augurProjectsRoot)
      const summaries: NonNullable<Awaited<ReturnType<typeof loadAugurProjectSummary>>>[] = []
      for (const project of projectNames) {
        try {
          const summary = await loadAugurProjectSummary(augurProjectsRoot, project)
          if (summary) summaries.push(summary)
        } catch (error) {
          log('augur_project_skipped', {
            project,
            reason: error instanceof Error ? error.message : String(error),
          })
        }
      }
      json(res, 200, { projects: summaries })
      return
    }

    if (req.method === 'GET' && url.pathname.startsWith('/augur/projects/')) {
      const parts = url.pathname.split('/').filter(Boolean).map(part => decodeURIComponent(part))
      if (parts.length === 4 && parts[0] === 'augur' && parts[1] === 'projects' && parts[3] === 'analyses') {
        const analyses = await listAugurAnalysisSummaries(augurProjectsRoot, parts[2])
        json(res, 200, { project: parts[2], analyses })
        return
      }
      if (parts.length === 5 && parts[0] === 'augur' && parts[1] === 'projects' && parts[3] === 'analyses') {
        const payload = await loadAugurAnalysisDetails(augurProjectsRoot, parts[2], parts[4])
        if (!payload) {
          json(res, 404, { error: 'analysis not found' })
          return
        }
        json(res, 200, payload)
        return
      }
      if (parts.length === 6 && parts[0] === 'augur' && parts[1] === 'projects' && parts[3] === 'analyses' && parts[5] === 'base') {
        const payload = await loadAugurBase(augurProjectsRoot, parts[2], parts[4])
        if (!payload) {
          json(res, 404, { error: 'analysis not found' })
          return
        }
        json(res, 200, payload)
        return
      }
      if (parts.length === 6 && parts[0] === 'augur' && parts[1] === 'projects' && parts[3] === 'analyses' && parts[5] === 'reflections') {
        const reflections = await loadAugurReflections(augurProjectsRoot, parts[2], parts[4])
        if (reflections === null) {
          json(res, 404, { error: 'analysis not found' })
          return
        }
        json(res, 200, { project: parts[2], analysis_id: parts[4], reflections })
        return
      }
      json(res, 404, { error: 'not found' })
      return
    }

    if (req.method === 'GET' && url.pathname.startsWith('/agents/')) {
      const name = decodeURIComponent(url.pathname.slice('/agents/'.length))
      const verbose = url.searchParams.get('verbose') === '1'
      const view = url.searchParams.get('view')
      const variants = view === 'variants' || url.searchParams.get('variants') === '1'
      const variantRecord = registry.get(name)
      const logicalRecord = registry.getLogical(name)
      if (variants) {
        if (!variantRecord) {
          json(res, 404, { error: `agent variant '${name}' not found` })
          return
        }
        json(res, 200, verbose ? variantRecord : registry.compact(variantRecord))
        return
      }
      if (!logicalRecord && !variantRecord) {
        json(res, 404, { error: `agent '${name}' not found` })
        return
      }
      if (logicalRecord) {
        json(res, 200, verbose ? logicalRecord : registry.compactLogical(logicalRecord))
        return
      }
      json(res, 200, verbose ? variantRecord : registry.compact(variantRecord!))
      return
    }

    if (req.method === 'GET' && url.pathname.startsWith('/requests/')) {
      const requestPath = url.pathname.slice('/requests/'.length)
      const eventSuffix = '/events'
      if (requestPath.endsWith(eventSuffix)) {
        const requestId = decodeURIComponent(requestPath.slice(0, -eventSuffix.length))
        const requestRecord = requests.get(requestId)
        if (!requestRecord) {
          json(res, 404, { error: `request '${requestId}' not found` })
          return
        }
        if (url.searchParams.get('follow') === '1') {
          openRequestEventStream(req, res, requestId)
          return
        }
        json(res, 200, {
          request_id: requestId,
          status: requestRecord.status,
          created_at: requestRecord.created_at,
          completed_at: requestRecord.completed_at ?? null,
          events: requestRecord.debug?.events ?? [],
        })
        return
      }
      const streamSuffix = '/stream'
      if (requestPath.endsWith(streamSuffix)) {
        const requestId = decodeURIComponent(requestPath.slice(0, -streamSuffix.length))
        const requestRecord = requests.get(requestId)
        if (!requestRecord) {
          json(res, 404, { error: `request '${requestId}' not found` })
          return
        }
        if (url.searchParams.get('follow') === '1') {
          openRequestTranscriptStream(req, res, requestId)
          return
        }
        json(res, 200, {
          request_id: requestId,
          status: requestRecord.status,
          created_at: requestRecord.created_at,
          completed_at: requestRecord.completed_at ?? null,
          events: requestRecord.transcript?.events ?? [],
        })
        return
      }
      const requestId = decodeURIComponent(requestPath)
      const verbose = url.searchParams.get('verbose') === '1'
      const requestRecord = requests.get(requestId)
      if (!requestRecord) {
        json(res, 404, { error: `request '${requestId}' not found` })
        return
      }
      const summary = {
        request_id: requestRecord.request_id,
        agent: requestRecord.agent,
        status: requestRecord.status,
        created_at: requestRecord.created_at,
        completed_at: requestRecord.completed_at ?? null,
        timeout_ms: requestRecord.timeout_ms ?? null,
        timed_out_at: requestRecord.timed_out_at ?? null,
        late_reply_received: requestRecord.late_reply_received ?? false,
        last_progress_at: requestRecord.last_progress_at ?? null,
        last_meaningful_event: requestRecord.last_meaningful_event ?? null,
        final_output_preview: summarizeValue(requestRecord.response?.output ?? requestRecord.late_response?.output, 400) ?? null,
        stream_url: `/requests/${requestId}/stream`,
        events_url: `/requests/${requestId}/events`,
      }
      if (!verbose) {
        json(res, 200, summary)
        return
      }
      json(res, 200, {
        ...summary,
        response: requestRecord.response ?? null,
        late_response: requestRecord.late_response ?? null,
        error: requestRecord.error ?? null,
        debug: requestRecord.debug,
        transcript: requestRecord.transcript ?? { events: [] },
      })
      return
    }

    if (req.method === 'POST' && url.pathname.startsWith('/agents/')) {
      const suffix = url.pathname.slice('/agents/'.length)
      if (!suffix.endsWith('/prompt')) {
        json(res, 404, { error: 'not found' })
        return
      }
      const name = decodeURIComponent(suffix.slice(0, -'/prompt'.length))
      const body = await parseBody(req)
      if (!isPromptBody(body)) {
        json(res, 400, { error: 'invalid prompt body' })
        return
      }
      const record = registry.resolveTarget(name, {
        variant: body.variant,
        backend_model: body.backend_model,
      })
      if (!record) {
        json(res, 404, {
          error: `agent '${name}' could not be resolved`,
          requested_variant: body.variant ?? null,
          requested_backend_model: body.backend_model ?? null,
        })
        return
      }
      const startedAt = Date.now()
      const requestId = `${record.name}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
      log('prompt_request_received', {
        request_id: requestId,
        agent: record.name,
        requested_agent: name,
        requested_variant: body.variant ?? null,
        requested_backend_model: body.backend_model ?? null,
        async: body.async === true,
        timeout_ms: resolveTimeoutMs(record, body),
        has_working_dir: typeof body.working_dir === 'string' && body.working_dir.length > 0,
        session_id: body.session_id ?? null,
      })
      requests.set(requestId, createRequestRecord({
        request_id: requestId,
        agent: record.name,
        created_at: new Date(startedAt).toISOString(),
        timeout_ms: resolveTimeoutMs(record, body),
      }))
      pushRequestEvent(requestId, 'request_received', {
        requested_agent: name,
        resolved_agent: record.name,
        requested_variant: body.variant ?? null,
        requested_backend_model: body.backend_model ?? null,
        async: body.async === true,
        timeout_ms: resolveTimeoutMs(record, body),
        has_working_dir: typeof body.working_dir === 'string' && body.working_dir.length > 0,
        session_id: body.session_id ?? null,
      })
      const { reply } = await sendPrompt(record.name, body, requestId, {
        disable_timeout: body.async === true,
      })
      pushRequestEvent(requestId, 'prompt_published', {
        topic: record.name,
      })
      if (body.async) {
        void reply.then(
          response => completeRequest(requestId, response),
          error => {
            log('request_async_failed', {
              request_id: requestId,
              agent: record.name,
              error: error instanceof Error ? error.message : String(error),
            })
            const existing = requests.get(requestId)
            if (!existing) return
            const message = error instanceof Error ? error.message : String(error)
            const isTimeout = message.includes('timed out waiting for')
            requests.set(requestId, applyFailureToRequestRecord(existing, {
              message,
              completed_at: new Date().toISOString(),
              is_timeout: isTimeout,
            }))
            pushRequestEvent(requestId, isTimeout ? 'prompt_timeout' : 'request_error', {
              ...(isTimeout ? { timeout_ms: existing.timeout_ms ?? null } : {}),
              error: message,
            })
          },
        )
        const payload: Record<string, unknown> = {
          request_id: requestId,
          status: 'pending',
          agent: record.name,
          resolved_agent: record.name,
          status_url: `/requests/${requestId}`,
          events_url: `/requests/${requestId}/events`,
          events_stream_url: `/requests/${requestId}/events?follow=1`,
          stream_url: `/requests/${requestId}/stream`,
          stream_follow_url: `/requests/${requestId}/stream?follow=1`,
        }
        if (body.verbose) payload.debug = requests.get(requestId)?.debug
        json(res, 202, payload)
        return
      }
      try {
        const syncReply = await reply
        const completedAt = Date.now()
        log('request_sync_reply_received', {
          request_id: requestId,
          agent: record.name,
          correlation_id: syncReply.correlation_id,
          status: syncReply.status,
          total_ms: completedAt - startedAt,
        })
        const metadata = {
          ...(syncReply.metadata ?? {}),
          gateway_timing: {
            started_at: new Date(startedAt).toISOString(),
            completed_at: new Date(completedAt).toISOString(),
            total_ms: completedAt - startedAt,
          },
        }
        const enrichedReply = { ...syncReply, metadata }
        completeRequest(requestId, enrichedReply)
        const payload: Record<string, unknown> = { ...enrichedReply }
        if (body.verbose || body.stream || body.debug) {
          payload.request_id = requestId
          payload.stream_url = `/requests/${requestId}/stream`
          payload.stream_follow_url = `/requests/${requestId}/stream?follow=1`
          payload.status_url = `/requests/${requestId}`
          payload.debug = requests.get(requestId)?.debug
          payload.transcript = requests.get(requestId)?.transcript
        }
        json(res, 200, payload)
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error)
        const isTimeout = message.includes('timed out waiting for')
        const response: ResponseMessage = {
          type: 'response',
          sender: record.name,
          correlation_id: requestId,
          status: isTimeout ? 'timeout' : 'error',
          output: message,
          errors: [message],
        }
        const existing = requests.get(requestId)
        const baseRecord = existing ?? createRequestRecord({
          request_id: requestId,
          agent: record.name,
          created_at: new Date(startedAt).toISOString(),
          timeout_ms: resolveTimeoutMs(record, body),
        })
        const failedRecord = applyFailureToRequestRecord(baseRecord, {
          message,
          completed_at: new Date().toISOString(),
          is_timeout: isTimeout,
        })
        requests.set(requestId, {
          ...failedRecord,
          response,
        })
        pushRequestEvent(requestId, isTimeout ? 'prompt_timeout' : 'request_error', {
          ...(isTimeout ? { timeout_ms: existing?.timeout_ms ?? resolveTimeoutMs(record, body) } : {}),
          error: message,
        })
        const payload: Record<string, unknown> = { ...response }
        if (body.verbose || body.stream || body.debug) {
          payload.request_id = requestId
          payload.stream_url = `/requests/${requestId}/stream`
          payload.stream_follow_url = `/requests/${requestId}/stream?follow=1`
          payload.status_url = `/requests/${requestId}`
          payload.debug = requests.get(requestId)?.debug
          payload.transcript = requests.get(requestId)?.transcript
        }
        json(res, isTimeout ? 504 : 500, payload)
      }
      return
    }

    json(res, 404, { error: 'not found' })
  } catch (error) {
    json(res, 500, { error: error instanceof Error ? error.message : String(error) })
  }
})

async function main(): Promise<void> {
  await registry.load()
  await producer.connect()
  await consumer.connect()
  await consumer.subscribe({ topic: replyTopic, fromBeginning: false })
  if (progressTopic !== replyTopic) {
    await consumer.subscribe({ topic: progressTopic, fromBeginning: false })
  }
  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      const raw = message.value?.toString() ?? ''
      let parsed: unknown
      try {
        parsed = JSON.parse(raw)
      } catch {
        log('reply_parse_failed', { topic, raw_length: raw.length })
        return
      }
      if (!parsed || typeof parsed !== 'object') {
        log('reply_ignored', { topic, raw_length: raw.length })
        return
      }
      if ((parsed as ProgressMessage).type === 'progress') {
        recordProgressEvent(parsed as ProgressMessage)
        return
      }
      if ((parsed as ResponseMessage).type !== 'response') {
        log('reply_ignored', { topic, raw_length: raw.length })
        return
      }
      const response = parsed as ResponseMessage
      const waiter = pending.get(response.correlation_id)
      if (!waiter) {
        log('reply_without_waiter', {
          sender: response.sender,
          correlation_id: response.correlation_id,
          status: response.status,
        })
        return
      }
      log('reply_consumed', {
        agent: waiter.agent,
        sender: response.sender,
        correlation_id: response.correlation_id,
        status: response.status,
      })
      pushRequestEvent(response.correlation_id, 'reply_consumed', {
        sender: response.sender,
        status: response.status,
      })
      clearTimeout(waiter.timer)
      pending.delete(response.correlation_id)
      waiter.resolve(response)
    },
  })
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject)
    server.listen(port, host, () => resolve())
  })
  ready = true
  log('kord_api_ready', {
    host,
    port,
    reply_topic: replyTopic,
    progress_topic: progressTopic,
    state_path: statePath,
    catalog_path: catalogPath,
    ttl_ms: ttlMs,
  })
}

main().catch(error => {
  log('kord_api_fatal', { error: error instanceof Error ? error.message : String(error) })
  process.exit(1)
})
