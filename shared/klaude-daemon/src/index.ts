import { createServer } from 'node:http'
import { Kafka } from 'kafkajs'
import { loadDaemonConfig } from './config.js'
import { buildPromptFromProfile, loadAgentProfile } from './agent-profile.js'
import { buildDiscoveryRecord, publishDiscoveryRegistration } from './discovery.js'
import { log } from './log.js'
import { buildReflectionEvent, buildResponseMessage, getOrCreateSession, isRequestMessage, updateSessionAfterRequest } from './protocol.js'
import { createProviderAdapter } from './runtime.js'
import { SessionStore } from './session-store.js'
import type { AgentDiscoveryRecord, AgentMessage, RequestMessage, ResponseMessage, ResponseTimingMetadata, SessionState } from './types.js'

const agentName = process.env.AGENT_NAME
if (!agentName) {
  throw new Error('AGENT_NAME required')
}
const AGENT_NAME = agentName
const AGENT_PROFILE = process.env.AGENT_PROFILE ?? AGENT_NAME
const agentProfile = loadAgentProfile(AGENT_PROFILE)

const daemonConfig = loadDaemonConfig()
const kafka = new Kafka({
  clientId: `klaude-daemon-${AGENT_NAME}`,
  brokers: daemonConfig.kafkaBrokers,
})

const consumer = kafka.consumer({ groupId: `klaude-daemon.${AGENT_NAME}` })
const producer = kafka.producer()
const runtime = createProviderAdapter(daemonConfig.executionProfile)
const sessionStore = new SessionStore(daemonConfig.sessionMapPath)
const sessions = await sessionStore.load()
const healthPort = Number.parseInt(process.env.DAEMON_HEALTH_PORT ?? '9090', 10)
const healthUrl = daemonConfig.healthUrl ?? `http://127.0.0.1:${healthPort}/health`
let daemonReady = false
let discoveryHeartbeat: NodeJS.Timeout | undefined

const healthServer = createServer((_req, res) => {
  res.statusCode = daemonReady ? 200 : 503
  res.setHeader('content-type', 'application/json')
  res.end(JSON.stringify({ ok: daemonReady, agent: AGENT_NAME }))
})

function sessionForMessage(message: RequestMessage): SessionState {
  const session = getOrCreateSession(sessions, message)
  const updated = updateSessionAfterRequest(session, message)
  sessions.set(updated.key, updated)
  return updated
}

async function persistSessions(): Promise<void> {
  await sessionStore.save(sessions)
}

async function publishResponse(message: RequestMessage, response: Omit<ResponseMessage, 'type' | 'sender' | 'correlation_id'>): Promise<void> {
  const payload = buildResponseMessage(AGENT_NAME, message, response)

  log('response_publish_start', {
    agent: AGENT_NAME,
    reply_topic: message.sender,
    correlation_id: message.correlation_id,
    status: response.status,
  })
  await producer.send({
    topic: message.sender,
    messages: [{ key: message.correlation_id, value: JSON.stringify(payload satisfies AgentMessage) }],
  })
  log('response_publish_complete', {
    agent: AGENT_NAME,
    reply_topic: message.sender,
    correlation_id: message.correlation_id,
    status: response.status,
  })
}

async function publishReflection(message: RequestMessage, reflection: NonNullable<ResponseMessage['reflection']>): Promise<void> {
  const payload = buildReflectionEvent(AGENT_NAME, message, reflection)

  await producer.send({
    topic: daemonConfig.reflectionsTopic,
    messages: [{ key: message.correlation_id, value: JSON.stringify(payload) }],
  })
}

function nowIso(): string {
  return new Date().toISOString()
}

function redactExecutionProfile(profile: typeof daemonConfig.executionProfile) {
  return {
    ...profile,
    apiKey: profile.apiKey ? '[redacted]' : undefined,
  }
}

function buildTimingMetadata(input: {
  receivedAt: number
  startedAt: number
  executeStartAt: number
  executeEndAt: number
  persistStartAt: number
  persistEndAt: number
}): ResponseTimingMetadata {
  return {
    received_at: new Date(input.receivedAt).toISOString(),
    started_at: new Date(input.startedAt).toISOString(),
    completed_at: nowIso(),
    total_ms: Date.now() - input.receivedAt,
    session_prepare_ms: input.executeStartAt - input.startedAt,
    execute_prompt_ms: input.executeEndAt - input.executeStartAt,
    persist_sessions_ms: input.persistEndAt - input.persistStartAt,
    publish_response_ms: 0,
  }
}

async function handleRequest(message: RequestMessage): Promise<{ status: ResponseMessage['status']; errors?: ResponseMessage['errors'] }> {
  const receivedAt = Date.now()
  const startedAt = Date.now()
  const session = sessionForMessage(message)

  const executeStartAt = Date.now()
  const readySession = await runtime.startOrResumeWarmSession(session)
  const { session: nextSession, result } = await runtime.executePrompt(readySession, {
    prompt: buildPromptFromProfile(agentProfile, message),
    working_dir: message.working_dir,
    timeout_ms: message.timeout_ms,
    reflect: message.reflect,
    reflection_prompt: message.reflection_prompt,
    agent_params: message.agent_params,
  })
  const executeEndAt = Date.now()

  sessions.set(nextSession.key, nextSession)
  const persistStartAt = Date.now()
  await persistSessions()
  const persistEndAt = Date.now()

  const response = {
    status: result.status,
    output: result.output,
    reflection: result.reflection,
    errors: result.errors,
    metadata: {
      timing: buildTimingMetadata({
        receivedAt,
        startedAt,
        executeStartAt,
        executeEndAt,
        persistStartAt,
        persistEndAt,
      }),
    },
  } satisfies Omit<ResponseMessage, 'type' | 'sender' | 'correlation_id'>

  await publishResponse(message, response)

  if (result.reflection) {
    await publishReflection(message, result.reflection)
  }

  return {
    status: result.status,
    errors: result.errors,
  }
}

async function publishDiscoveryRecord(record: AgentDiscoveryRecord): Promise<void> {
  if (!daemonConfig.discoveryServerUrl) return
  await publishDiscoveryRegistration(daemonConfig.discoveryServerUrl, record)
}

function startDiscoveryHeartbeat(record: AgentDiscoveryRecord): void {
  if (!daemonConfig.discoveryServerUrl) return
  const publish = async (): Promise<void> => {
    try {
      await publishDiscoveryRecord(record)
    } catch (error) {
      log('discovery_registration_failed', {
        agent: AGENT_NAME,
        error: error instanceof Error ? error.message : String(error),
      })
    }
  }

  void publish()
  discoveryHeartbeat = setInterval(() => {
    void publish()
  }, daemonConfig.discoveryPublishIntervalMs)
}

async function main(): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    healthServer.once('error', reject)
    healthServer.listen(healthPort, '0.0.0.0', () => resolve())
  })

  log('daemon_start', {
    agent: AGENT_NAME,
    agent_profile_name: AGENT_PROFILE,
    agent_profile: agentProfile,
    execution_profile: redactExecutionProfile(daemonConfig.executionProfile),
    brokers: daemonConfig.kafkaBrokers,
    reflections_topic: daemonConfig.reflectionsTopic,
    discovery_server_url: daemonConfig.discoveryServerUrl ?? null,
    session_map_path: daemonConfig.sessionMapPath,
  })

  await producer.connect()
  await consumer.connect()
  await consumer.subscribe({ topic: AGENT_NAME, fromBeginning: false })

  const discoveryRecord = buildDiscoveryRecord({
    agent: AGENT_NAME,
    specialization: AGENT_PROFILE,
    agentProfile,
    config: daemonConfig,
    healthUrl,
  })
  startDiscoveryHeartbeat(discoveryRecord)

  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      const raw = message.value?.toString() ?? ''
      let parsed: unknown
      try {
        parsed = JSON.parse(raw)
      } catch (error) {
        log('message_parse_failed', { topic, error: (error as Error).message })
        return
      }

      if (!isRequestMessage(parsed)) {
        log('message_ignored', { topic, reason: 'not_request' })
        return
      }

      try {
        const summary = await handleRequest(parsed)
        log('request_handled', {
          topic,
          sender: parsed.sender,
          correlation_id: parsed.correlation_id,
          status: summary.status,
          errors: summary.errors,
        })
      } catch (error) {
        const messageText = (error as Error).message
        log('request_failed', {
          topic,
          sender: parsed.sender,
          correlation_id: parsed.correlation_id,
          error: messageText,
        })
        await publishResponse(parsed, {
          status: 'error',
          output: messageText,
          errors: [messageText],
          metadata: {
            timing: {
              received_at: nowIso(),
              started_at: nowIso(),
              completed_at: nowIso(),
              total_ms: 0,
              session_prepare_ms: 0,
              execute_prompt_ms: 0,
              persist_sessions_ms: 0,
              publish_response_ms: 0,
            },
          },
        })
      }
    },
  })

  daemonReady = true
  log('daemon_ready', { agent: AGENT_NAME, health_port: healthPort })
}

main().catch(error => {
  if (discoveryHeartbeat) clearInterval(discoveryHeartbeat)
  log('daemon_fatal', { error: (error as Error).message })
  process.exit(1)
})
