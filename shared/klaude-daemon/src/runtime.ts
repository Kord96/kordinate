import { randomUUID } from 'node:crypto'
import { spawn, spawnSync } from 'node:child_process'
import { createWriteStream } from 'node:fs'
import path from 'node:path'
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises'
import Anthropic from '@anthropic-ai/sdk'
import { query } from '@anthropic-ai/claude-agent-sdk'
import { Codex } from '@openai/codex-sdk'
import type { ExecutionProfile } from './config.js'
import { log } from './log.js'
import { SimpleHarnessAdapter, classifyAlfredDirectIntent, enforceAlfredDirectIntentContract } from './simple-harness.js'
import type { ProviderSessionAdapter, ReflectionPayload, RuntimeRequest, RuntimeResult, SessionState, ResponseUsageMetadata } from './types.js'

const OPENCLAUDE_NPM_PACKAGE = process.env.OPENCLAUDE_NPM_PACKAGE ?? '@gitlawb/openclaude'
const OPENCLAUDE_BIN = process.env.OPENCLAUDE_BIN ?? 'openclaude'

type OpenClaudeContentBlock = {
  type?: string
  name?: string
  text?: string
  input?: Record<string, unknown> | string
}

type OpenClaudeStructuredMessage = {
  type?: string
  subtype?: string
  result?: string
  message?: {
    content?: OpenClaudeContentBlock[]
  }
  tool_name?: string
  tool_use_id?: string
  elapsed_time_seconds?: number
}

type OpenClaudeStructuredParseState = {
  buffer: string
  resultText: string
  rawLines: string[]
  writeLine: (line: string) => void
}

type CodexThreadEvent = {
  type?: string
  item?: {
    type?: string
    id?: string
    text?: string
    command?: string
    aggregated_output?: string
    server?: string
    tool?: string
    arguments?: unknown
    status?: string
    changes?: Array<{ path?: string; kind?: string }>
    error?: { message?: string }
  }
  usage?: {
    input_tokens?: number
    cached_input_tokens?: number
    output_tokens?: number
  }
  error?: {
    message?: string
  }
  message?: string
}

type CodexUsageSnapshot = {
  input_tokens: number
  cached_input_tokens: number
  output_tokens: number
}

function parseReflectionPayload(text: string): ReflectionPayload | undefined {
  try {
    const parsed = JSON.parse(text) as { project?: unknown; general?: unknown }
    if (typeof parsed.project === 'string' && typeof parsed.general === 'string') {
      return { project: parsed.project, general: parsed.general }
    }
  } catch {
    // ignore
  }
  return undefined
}

function buildDefaultReflectionPrompt(taskOutput: string, overridePrompt?: string): string {
  const base = overridePrompt ?? [
    'Based on the completed task, return strict JSON only with exactly these keys:',
    '{"project":"...","general":"..."}',
    'project: lessons specific to the current project/repo/context.',
    'general: lessons that transfer to any project.',
    'Use strings only. If there is no strong lesson for a key, return an empty string.',
  ].join('\n')
  return `${base}\n\nTask output:\n${taskOutput}`
}

function appendErrors(result: RuntimeResult, errors?: string[]): RuntimeResult {
  if (!errors || errors.length === 0) return result
  return {
    ...result,
    errors: [...(result.errors ?? []), ...errors],
  }
}

function withReflection(result: RuntimeResult, reflection?: ReflectionPayload): RuntimeResult {
  if (!reflection) return result
  return {
    ...result,
    reflection,
  }
}

function finalizeRuntimeResult(result: RuntimeResult, reflectionResult?: { reflection?: ReflectionPayload; errors?: string[] }): RuntimeResult {
  if (!reflectionResult) return result
  return appendErrors(withReflection(result, reflectionResult.reflection), reflectionResult.errors)
}

function errorResult(message: string): RuntimeResult {
  return {
    status: 'error',
    output: message,
    errors: [message],
  }
}

function appendDiagnosticPart(parts: string[], label: string, value: unknown): void {
  if (typeof value !== 'string') return
  const trimmed = value.trim()
  if (!trimmed) return
  parts.push(`${label}: ${trimmed}`)
}

export function formatProviderError(error: unknown): string[] {
  if (!(error instanceof Error)) {
    return [String(error)]
  }

  const parts: string[] = []
  const seen = new Set<string>()
  const pushUnique = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || seen.has(trimmed)) return
    seen.add(trimmed)
    parts.push(trimmed)
  }

  pushUnique(error.message)

  const maybeWithProps = error as Error & {
    stderr?: string
    stdout?: string
    debugLogPath?: string
    debugLogTail?: string
    structuredLogPath?: string
    structuredLogTail?: string
    code?: string | number
    exitCode?: number
    signal?: string
    cause?: unknown
  }

  appendDiagnosticPart(parts, 'stderr', maybeWithProps.stderr)
  appendDiagnosticPart(parts, 'stdout', maybeWithProps.stdout)
  appendDiagnosticPart(parts, 'debug_log_path', maybeWithProps.debugLogPath)
  appendDiagnosticPart(parts, 'debug_log_tail', maybeWithProps.debugLogTail)
  appendDiagnosticPart(parts, 'structured_log_path', maybeWithProps.structuredLogPath)
  appendDiagnosticPart(parts, 'structured_log_tail', maybeWithProps.structuredLogTail)

  if (typeof maybeWithProps.code === 'string' || typeof maybeWithProps.code === 'number') {
    pushUnique(`code: ${String(maybeWithProps.code)}`)
  }
  if (typeof maybeWithProps.exitCode === 'number') {
    pushUnique(`exit_code: ${String(maybeWithProps.exitCode)}`)
  }
  if (typeof maybeWithProps.signal === 'string' && maybeWithProps.signal.trim()) {
    pushUnique(`signal: ${maybeWithProps.signal.trim()}`)
  }

  if (maybeWithProps.cause instanceof Error) {
    for (const detail of formatProviderError(maybeWithProps.cause)) {
      if (detail !== error.message) pushUnique(`cause: ${detail}`)
    }
  } else if (typeof maybeWithProps.cause === 'string' && maybeWithProps.cause.trim()) {
    pushUnique(`cause: ${maybeWithProps.cause.trim()}`)
  }

  return parts.length > 0 ? parts : ['unknown provider error']
}

export const __testOnly = {
  classifyAlfredDirectIntent,
  enforceAlfredDirectIntentContract,
}

function errorResultFromError(error: unknown): RuntimeResult {
  const details = formatProviderError(error)
  return {
    status: 'error',
    output: details[0] ?? 'unknown provider error',
    errors: details,
  }
}

function successResult(output: string): RuntimeResult {
  return {
    status: 'success',
    output,
  }
}

function withMetadata(result: RuntimeResult, metadata?: Partial<NonNullable<RuntimeResult['metadata']>>): RuntimeResult {
  if (!metadata) return result
  return {
    ...result,
    metadata: {
      ...((result.metadata ?? {}) as Record<string, unknown>),
      ...metadata,
    } as RuntimeResult['metadata'],
  }
}

function summarizeText(text: string, maxLength = 400): string {
  const normalized = text.replace(/\s+/g, ' ').trim()
  if (normalized.length <= maxLength) return normalized
  return `${normalized.slice(0, maxLength - 3)}...`
}

function summarizeUnknown(value: unknown, maxLength = 1200): string | undefined {
  if (typeof value === 'string') return summarizeText(value, maxLength)
  if (value === null || value === undefined) return undefined
  try {
    return summarizeText(JSON.stringify(value), maxLength)
  } catch {
    return summarizeText(String(value), maxLength)
  }
}

function extractBashCommand(input: unknown): string | undefined {
  if (!input || typeof input !== 'object') return undefined
  const candidate = input as Record<string, unknown>
  for (const key of ['command', 'cmd', 'script']) {
    if (typeof candidate[key] === 'string' && candidate[key].trim()) {
      return candidate[key].trim()
    }
  }
  return undefined
}

function processOpenClaudeStructuredMessage(
  message: OpenClaudeStructuredMessage,
  options: { model: string; sessionId: string }
): void {
  if (message.type === 'assistant' && Array.isArray(message.message?.content)) {
    for (const block of message.message.content) {
      if (block.type === 'tool_use') {
        const toolInputSummary = summarizeUnknown(block.input)
        const bashCommand = extractBashCommand(block.input)
        log('harness_tool_use', {
          runtime: 'openclaude-harness',
          model: options.model,
          session_id: options.sessionId,
          tool_name: block.name ?? 'unknown',
          tool_input: toolInputSummary ?? null,
          bash_command: bashCommand ?? null,
        })
      }
    }
    return
  }

  if (message.type === 'tool_progress') {
    log('harness_tool_progress', {
      runtime: 'openclaude-harness',
      model: options.model,
      session_id: options.sessionId,
      tool_name: message.tool_name ?? 'unknown',
      tool_use_id: message.tool_use_id ?? null,
      elapsed_time_seconds: message.elapsed_time_seconds ?? null,
    })
  }
}

function consumeOpenClaudeStructuredChunk(
  state: OpenClaudeStructuredParseState,
  chunkText: string,
  options: { model: string; sessionId: string }
): void {
  state.buffer += chunkText
  while (true) {
    const newlineIndex = state.buffer.indexOf('\n')
    if (newlineIndex === -1) break
    const line = state.buffer.slice(0, newlineIndex).trim()
    state.buffer = state.buffer.slice(newlineIndex + 1)
    if (!line) continue

    state.rawLines.push(line)
    if (state.rawLines.length > 200) state.rawLines.shift()
    state.writeLine(line)

    let parsed: OpenClaudeStructuredMessage | undefined
    try {
      parsed = JSON.parse(line) as OpenClaudeStructuredMessage
    } catch {
      continue
    }

    processOpenClaudeStructuredMessage(parsed, options)
    if (parsed.type === 'result' && typeof parsed.result === 'string') {
      state.resultText = parsed.result
    }
  }
}

function finalizeOpenClaudeStructuredStream(
  state: OpenClaudeStructuredParseState,
  options: { model: string; sessionId: string }
): void {
  if (!state.buffer.trim()) return
  consumeOpenClaudeStructuredChunk(state, '\n', options)
}

function processCodexStructuredEvent(
  event: CodexThreadEvent,
  options: { model: string; sessionId: string }
): void {
  const base = {
    runtime: 'codex-sdk',
    model: options.model,
    session_id: options.sessionId,
  } as const

  if ((event.type === 'item.started' || event.type === 'item.updated' || event.type === 'item.completed') && event.item) {
    const item = event.item
    log('codex_item_event', {
      ...base,
      event_type: event.type,
      item_type: item.type ?? 'unknown',
      item_id: item.id ?? null,
      status: item.status ?? null,
      command: typeof item.command === 'string' ? item.command : null,
      text: typeof item.text === 'string' ? summarizeText(item.text, 400) : null,
      tool_server: typeof item.server === 'string' ? item.server : null,
      tool_name: typeof item.tool === 'string' ? item.tool : null,
      tool_arguments: summarizeUnknown(item.arguments) ?? null,
      aggregated_output: typeof item.aggregated_output === 'string' ? summarizeText(item.aggregated_output, 1200) : null,
      error_message: typeof item.error?.message === 'string' ? item.error.message : null,
      file_changes: Array.isArray(item.changes) ? summarizeUnknown(item.changes, 1200) ?? null : null,
    })
    return
  }

  if (event.type === 'turn.completed') {
    log('codex_turn_completed', {
      ...base,
      usage: summarizeUnknown(event.usage) ?? null,
    })
    return
  }

  if (event.type === 'turn.failed' || event.type === 'error') {
    log('codex_turn_error', {
      ...base,
      error: summarizeUnknown(event.error ?? event.message) ?? null,
    })
  }
}

async function runCodexStructuredTurn(
  threadFactory: () => { id: string | null; runStreamed(input: string): Promise<{ events: AsyncGenerator<CodexThreadEvent> }> },
  prompt: string,
  options: { model: string; sessionId: string; workingDirectory?: string }
): Promise<{ output: string; providerSessionId?: string; structuredLogPath: string; structuredLogTail: string; usage?: ResponseUsageMetadata }> {
  const runtimeHome = resolveOpenClaudeHome(options.workingDirectory)
  const debugDir = path.join(runtimeHome, '.daemon-logs')
  await mkdir(debugDir, { recursive: true })
  const structuredLogPath = path.join(debugDir, `codex-${options.sessionId}-${Date.now()}-stream.jsonl`)
  const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
  const thread = threadFactory()
  let finalResponse = ''
  let usage: CodexUsageSnapshot | undefined

  log('codex_stream_start', {
    runtime: 'codex-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
  })

  try {
    const { events } = await thread.runStreamed(prompt)
    for await (const event of events) {
      structuredLogStream.write(`${JSON.stringify(event)}\n`)
      processCodexStructuredEvent(event, options)
      if (
        (event.type === 'item.completed' || event.type === 'item.updated')
        && event.item?.type === 'agent_message'
        && typeof event.item.text === 'string'
      ) {
        finalResponse = event.item.text
      }
      if (event.type === 'turn.completed' && event.usage) {
        usage = {
          input_tokens: Number(event.usage.input_tokens ?? 0),
          cached_input_tokens: Number(event.usage.cached_input_tokens ?? 0),
          output_tokens: Number(event.usage.output_tokens ?? 0),
        }
      }
    }
  } catch (error) {
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    let structuredLogTail = ''
    try {
      structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
    } catch {
      // ignore
    }
    log('codex_stream_error', {
      runtime: 'codex-sdk',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      error: error instanceof Error ? error.message : String(error),
    })
    throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
      structuredLogPath,
      structuredLogTail,
    })
  } finally {
    if (!structuredLogStream.closed) {
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
    }
  }

  let structuredLogTail = ''
  try {
    structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
  } catch {
    // ignore
  }

  log('codex_stream_complete', {
    runtime: 'codex-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
  })

  return {
    output: finalResponse.trim(),
    providerSessionId: thread.id ?? undefined,
    structuredLogPath,
    structuredLogTail,
    usage,
  }
}

function processClaudeStructuredMessage(
  message: Record<string, unknown>,
  options: { model: string; sessionId: string }
): void {
  const type = typeof message.type === 'string' ? message.type : 'unknown'
  log('claude_message', {
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    message_type: type,
    subtype: typeof message.subtype === 'string' ? message.subtype : null,
    parent_tool_use_id: typeof message.parent_tool_use_id === 'string' ? message.parent_tool_use_id : null,
    content: summarizeUnknown(message, 1200) ?? null,
  })
}

async function runClaudeStructuredQuery(
  streamFactory: () => AsyncIterable<Record<string, unknown>>,
  options: { model: string; sessionId: string; workingDirectory?: string }
): Promise<{ messages: Record<string, unknown>[]; structuredLogPath: string; structuredLogTail: string }> {
  const runtimeHome = resolveOpenClaudeHome(options.workingDirectory)
  const debugDir = path.join(runtimeHome, '.daemon-logs')
  await mkdir(debugDir, { recursive: true })
  const structuredLogPath = path.join(debugDir, `claude-${options.sessionId}-${Date.now()}-stream.jsonl`)
  const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
  const messages: Record<string, unknown>[] = []

  log('claude_stream_start', {
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
  })

  try {
    for await (const message of streamFactory()) {
      messages.push(message)
      structuredLogStream.write(`${JSON.stringify(message)}\n`)
      processClaudeStructuredMessage(message, options)
    }
  } catch (error) {
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    let structuredLogTail = ''
    try {
      structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
    } catch {
      // ignore
    }
    log('claude_stream_error', {
      runtime: 'claude-agent-sdk',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      error: error instanceof Error ? error.message : String(error),
    })
    throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
      structuredLogPath,
      structuredLogTail,
    })
  } finally {
    if (!structuredLogStream.closed) {
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
    }
  }

  let structuredLogTail = ''
  try {
    structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
  } catch {
    // ignore
  }

  log('claude_stream_complete', {
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
  })

  return { messages, structuredLogPath, structuredLogTail }
}

function shouldReflect(request: RuntimeRequest): boolean {
  return request.reflect === true
}

function nextSessionState(session: SessionState, providerSessionId?: string): SessionState {
  return {
    ...session,
    providerSessionId: providerSessionId ?? session.providerSessionId,
  }
}

function isMissingClaudeSessionError(error: unknown): boolean {
  if (!(error instanceof Error)) return false
  const message = error.message.toLowerCase()
  return message.includes('no conversation found with session id')
}

async function maybeReflectWithClaudeAgentSdk(model: string, session: SessionState, taskOutput: string, reflectionPrompt?: string): Promise<{ session: SessionState; reflection?: ReflectionPayload; errors?: string[] }> {
  const sessionId = session.providerSessionId ?? randomUUID()
  try {
    let text = ''
    let nextSessionId = sessionId
    const q = query({
      prompt: buildDefaultReflectionPrompt(taskOutput, reflectionPrompt),
      options: {
        cwd: process.cwd(),
        resume: session.providerSessionId,
        model,
        permissionMode: 'bypassPermissions',
        env: process.env,
      },
    })

    for await (const message of q) {
      if (message.type === 'assistant' && Array.isArray(message.message?.content)) {
        for (const block of message.message.content) {
          if (block.type === 'text') text += block.text
        }
      }
      if ('session_id' in message && typeof message.session_id === 'string') {
        nextSessionId = message.session_id
      }
      if (message.type === 'result' && message.subtype === 'success' && typeof message.result === 'string') {
        text = text || message.result
      }
    }

    const reflection = parseReflectionPayload(text.trim())
    if (!reflection) {
      return { session: nextSessionState(session, nextSessionId), errors: ['Failed to parse reflection payload'] }
    }
    return { session: nextSessionState(session, nextSessionId), reflection }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    return { session: nextSessionState(session, sessionId), errors: [message] }
  }
}

async function maybeReflectWithCodex(threadFactory: () => { run(input: string): Promise<{ finalResponse: string } | string> }, taskOutput: string, reflectionPrompt?: string): Promise<{ reflection?: ReflectionPayload; errors?: string[] }> {
  try {
    const result = await threadFactory().run(buildDefaultReflectionPrompt(taskOutput, reflectionPrompt))
    const text = typeof result === 'string' ? result : result.finalResponse
    const reflection = parseReflectionPayload(text)
    if (!reflection) {
      return { errors: ['Failed to parse reflection payload'] }
    }
    return { reflection }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    return { errors: [message] }
  }
}

export function getOpenClaudeBinaryConfig(env: NodeJS.ProcessEnv = process.env): { command: string; packageName: string } {
  return {
    command: env.OPENCLAUDE_BIN || 'openclaude',
    packageName: env.OPENCLAUDE_NPM_PACKAGE || '@gitlawb/openclaude',
  }
}

function commandExists(command: string): boolean {
  const result = spawnSync(command, ['--version'], { stdio: 'ignore' })
  return result.status === 0
}

function installOpenClaudeFromNpm(packageName: string): void {
  const install = spawnSync('npm', ['install', '-g', packageName], { encoding: 'utf8' })
  if (install.status === 0) return
  const stderr = (install.stderr || '').trim()
  const stdout = (install.stdout || '').trim()
  throw new Error(stderr || stdout || `failed to install ${packageName} with npm`)
}

function ensureOpenClaudeCommand(): string {
  const config = getOpenClaudeBinaryConfig()
  if (commandExists(config.command)) return config.command
  if (config.command !== OPENCLAUDE_BIN) {
    throw new Error(`OPENCLAUDE_BIN '${config.command}' is not executable`)
  }
  installOpenClaudeFromNpm(config.packageName)
  if (commandExists(config.command)) return config.command
  throw new Error(`installed ${config.packageName}, but '${config.command}' is still not executable`)
}

function resolveOpenClaudeHome(workingDirectory?: string): string {
  return workingDirectory
    ?? process.env.AGENT_HOME_DIR
    ?? process.env.HOME
    ?? process.cwd()
}

async function runOpenClaudePrint(prompt: string, options: {
  model: string
  sessionId: string
  baseUrl?: string
  apiKey?: string
  workingDirectory?: string
  timeoutMs?: number
}): Promise<string> {
  const env: Record<string, string> = {}
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined) env[key] = value
  }
  const runtimeHome = resolveOpenClaudeHome(options.workingDirectory)
  const timeoutMs = Number.isFinite(options.timeoutMs)
    ? Math.max(1, options.timeoutMs as number)
    : undefined
  const debugDir = path.join(runtimeHome, '.daemon-logs')
  await mkdir(debugDir, { recursive: true })
  const debugLogPath = path.join(debugDir, `openclaude-${options.sessionId}-${Date.now()}.log`)
  const structuredLogPath = path.join(debugDir, `openclaude-${options.sessionId}-${Date.now()}-stream.jsonl`)
  if (options.baseUrl) env.OPENAI_BASE_URL = options.baseUrl
  if (options.apiKey) env.OPENAI_API_KEY = options.apiKey
  env.OPENAI_MODEL = options.model
  env.CLAUDE_CODE_USE_OPENAI = '1'
  env.HOME = runtimeHome

  const args = [
    '--print',
    '--bare',
    '--verbose',
    '--output-format', 'stream-json',
    '--debug',
    '--debug-file', debugLogPath,
    '--dangerously-skip-permissions',
  ]
  args.push(
    '--no-session-persistence',
    '--session-id', options.sessionId,
    '--model', options.model,
    prompt,
  )
  const command = ensureOpenClaudeCommand()

  return await new Promise<string>((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: runtimeHome,
      env,
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    let stdout = ''
    let stderr = ''
    const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
    const structuredState: OpenClaudeStructuredParseState = {
      buffer: '',
      resultText: '',
      rawLines: [],
      writeLine: line => { structuredLogStream.write(`${line}\n`) },
    }
    let settled = false
    let timedOut = false
    const timeoutHandle = timeoutMs
      ? setTimeout(() => {
          timedOut = true
          log('harness_timeout', {
            runtime: 'openclaude-harness',
            model: options.model,
            session_id: options.sessionId,
            pid: child.pid ?? null,
            timeout_ms: timeoutMs,
            debug_log_path: debugLogPath,
            structured_log_path: structuredLogPath,
          })
          child.kill('SIGKILL')
        }, timeoutMs)
      : undefined

    log('harness_spawn', {
      runtime: 'openclaude-harness',
      model: options.model,
      session_id: options.sessionId,
      pid: child.pid ?? null,
      cwd: runtimeHome,
      debug_log_path: debugLogPath,
      structured_log_path: structuredLogPath,
      timeout_ms: timeoutMs ?? null,
    })

    child.stdout.on('data', chunk => {
      const chunkText = chunk.toString()
      stdout += chunkText
      consumeOpenClaudeStructuredChunk(structuredState, chunkText, options)
    })
    child.stderr.on('data', chunk => { stderr += chunk.toString() })
    child.on('error', async error => {
      if (settled) return
      settled = true
      if (timeoutHandle) clearTimeout(timeoutHandle)
      finalizeOpenClaudeStructuredStream(structuredState, options)
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
      let debugLogTail = ''
      let structuredLogTail = ''
      try {
        debugLogTail = (await readFile(debugLogPath, 'utf8')).slice(-4000)
      } catch {
        // ignore
      }
      try {
        structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
      } catch {
        // ignore
      }
      log('harness_exit', {
        runtime: 'openclaude-harness',
        model: options.model,
        session_id: options.sessionId,
        pid: child.pid ?? null,
        exit_code: null,
        timed_out: timedOut,
        debug_log_path: debugLogPath,
        structured_log_path: structuredLogPath,
        error: error.message,
      })
      reject(Object.assign(error, {
        stderr,
        stdout: structuredState.resultText || stdout,
        debugLogPath,
        debugLogTail,
        structuredLogPath,
        structuredLogTail,
      }))
    })
    child.on('close', async (code, signal) => {
      if (settled) return
      settled = true
      if (timeoutHandle) clearTimeout(timeoutHandle)
      finalizeOpenClaudeStructuredStream(structuredState, options)
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
      let debugLogTail = ''
      let structuredLogTail = ''
      try {
        debugLogTail = (await readFile(debugLogPath, 'utf8')).slice(-4000)
      } catch {
        // ignore
      }
      try {
        structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
      } catch {
        // ignore
      }
      log('harness_exit', {
        runtime: 'openclaude-harness',
        model: options.model,
        session_id: options.sessionId,
        pid: child.pid ?? null,
        exit_code: code ?? null,
        signal: signal ?? null,
        timed_out: timedOut,
        debug_log_path: debugLogPath,
        structured_log_path: structuredLogPath,
      })
      if (code !== 0) {
        const error = Object.assign(new Error(
          timedOut
            ? `openclaude timed out after ${timeoutMs}ms`
            : (stderr.trim() || `openclaude exited with code ${code}`)
        ), {
          stderr,
          stdout: structuredState.resultText || stdout,
          exitCode: code ?? undefined,
          signal: signal ?? undefined,
          debugLogPath,
          debugLogTail,
          structuredLogPath,
          structuredLogTail,
        })
        reject(error)
        return
      }
      const resultText = structuredState.resultText || stdout.trim()
      resolve(resultText)
    })
  })
}

async function maybeReflectWithOpenClaude(taskOutput: string, options: { model: string; sessionId: string; baseUrl?: string; apiKey?: string; workingDirectory?: string }, reflectionPrompt?: string): Promise<{ reflection?: ReflectionPayload; errors?: string[] }> {
  try {
    const text = await runOpenClaudePrint(buildDefaultReflectionPrompt(taskOutput, reflectionPrompt), options)
    const reflection = parseReflectionPayload(text)
    if (!reflection) {
      return { errors: ['Failed to parse reflection payload'] }
    }
    return { reflection }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    return { errors: [message] }
  }
}

export class ClaudeAgentSdkAdapter implements ProviderSessionAdapter {
  private readonly model: string
  private readonly apiKey?: string
  private readonly workingDirectory?: string

  constructor(model: string, options: { apiKey?: string; workingDirectory?: string }) {
    this.model = model
    this.apiKey = options.apiKey
    this.workingDirectory = options.workingDirectory
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return nextSessionState(session, session.providerSessionId ?? randomUUID())
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    if (!this.apiKey) {
      return { session, result: errorResult('BACKEND_API_KEY is not configured for Claude runtime') }
    }

    const sessionId = session.providerSessionId ?? randomUUID()
    const env = {
      ...process.env,
      ANTHROPIC_API_KEY: this.apiKey,
    }

    try {
      const executeOnce = async (resumeSessionId?: string): Promise<{ text: string; nextSessionId: string }> => {
        let text = ''
        let nextSessionId = sessionId
        const { messages } = await runClaudeStructuredQuery(
          () => query({
            prompt: request.prompt,
            options: {
              cwd: request.working_dir ?? this.workingDirectory ?? process.cwd(),
              resume: resumeSessionId,
              model: this.model,
              permissionMode: 'bypassPermissions',
              env,
            },
          }) as unknown as AsyncIterable<Record<string, unknown>>,
          {
            model: this.model,
            sessionId,
            workingDirectory: request.working_dir ?? this.workingDirectory,
          }
        )

        for (const message of messages) {
          const messageRecord = message as {
            type?: string
            message?: { content?: Array<{ type?: string; text?: string }> }
            session_id?: string
            subtype?: string
            result?: string
          }
          const content = messageRecord.message?.content
          if (messageRecord.type === 'assistant' && Array.isArray(content)) {
            for (const block of content) {
              if (block.type === 'text') text += block.text
            }
          }
          if (typeof messageRecord.session_id === 'string') {
            nextSessionId = messageRecord.session_id
          }
          if (messageRecord.type === 'result' && messageRecord.subtype === 'success' && typeof messageRecord.result === 'string') {
            text = text || messageRecord.result
          }
        }

        return { text, nextSessionId }
      }

      let run: { text: string; nextSessionId: string }
      try {
        run = await executeOnce(session.providerSessionId)
      } catch (error) {
        if (!session.providerSessionId || !isMissingClaudeSessionError(error)) throw error
        log('claude_session_resume_failed', {
          model: this.model,
          stale_session_id: session.providerSessionId,
          reason: error instanceof Error ? error.message : String(error),
        })
        run = await executeOnce(undefined)
      }

      const baseResult = enforceAlfredDirectIntentContract(request, successResult(run.text.trim()))
      const nextSession = nextSessionState(session, run.nextSessionId)
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithClaudeAgentSdk(this.model, nextSession, baseResult.output, request.reflection_prompt)
      return {
        session: reflectionResult.session,
        result: finalizeRuntimeResult(baseResult, reflectionResult),
      }
    } catch (error) {
      return { session: nextSessionState(session, sessionId), result: errorResultFromError(error) }
    }
  }

  async interruptActiveExecution(_session: SessionState): Promise<void> {
    // Query.interrupt wiring can be added once the daemon keeps active Query instances per sender.
  }
}

export class CodexSdkAdapter implements ProviderSessionAdapter {
  private readonly codex: Codex
  private readonly model: string
  private readonly skipGitRepoCheck: boolean
  private readonly workingDirectory?: string

  constructor(model: string, options: { apiKey?: string; baseUrl?: string; skipGitRepoCheck: boolean; workingDirectory?: string }) {
    const env: Record<string, string> = {}
    for (const [key, value] of Object.entries(process.env)) {
      if (value !== undefined && key !== 'OPENAI_BASE_URL') {
        env[key] = value
      }
    }

    this.codex = new Codex({
      apiKey: options.apiKey,
      baseUrl: options.baseUrl,
      env,
    })
    this.model = model
    this.skipGitRepoCheck = options.skipGitRepoCheck
    this.workingDirectory = options.workingDirectory
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return session
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    try {
      const threadOptions = {
        model: this.model,
        skipGitRepoCheck: this.skipGitRepoCheck,
        workingDirectory: this.workingDirectory,
      }

      const thread = session.providerSessionId
        ? this.codex.resumeThread(session.providerSessionId, threadOptions)
        : this.codex.startThread(threadOptions)

      const sessionId = session.providerSessionId ?? randomUUID()
      const runResult = await runCodexStructuredTurn(
        () => thread,
        request.prompt,
        {
          model: this.model,
          sessionId,
          workingDirectory: this.workingDirectory,
        }
      )
      const output = runResult.output
      const nextSession = nextSessionState(session, runResult.providerSessionId ?? thread.id ?? session.providerSessionId)
      const usageMetadata: ResponseUsageMetadata | undefined = runResult.usage
        ? {
            input_tokens: runResult.usage.input_tokens,
            cached_input_tokens: runResult.usage.cached_input_tokens,
            output_tokens: runResult.usage.output_tokens,
          }
        : undefined
      const baseResult = enforceAlfredDirectIntentContract(request, withMetadata(successResult(output), usageMetadata ? { usage: usageMetadata } : undefined))

      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithCodex(
        () => {
          const reflectionThread = nextSession.providerSessionId
            ? this.codex.resumeThread(nextSession.providerSessionId, threadOptions)
            : this.codex.startThread(threadOptions)
          return reflectionThread
        },
        output,
        request.reflection_prompt,
      )

      return {
        session: nextSession,
        result: finalizeRuntimeResult(baseResult, reflectionResult),
      }
    } catch (error) {
      return { session, result: errorResultFromError(error) }
    }
  }

  async interruptActiveExecution(_session: SessionState): Promise<void> {
    // Codex interruption semantics will be added later.
  }
}

export class OpenClaudeHarnessAdapter implements ProviderSessionAdapter {
  private readonly model: string
  private readonly baseUrl?: string
  private readonly apiKey?: string
  private readonly workingDirectory?: string

  constructor(model: string, options: { baseUrl?: string; apiKey?: string; workingDirectory?: string }) {
    this.model = model
    this.baseUrl = options.baseUrl
    this.apiKey = options.apiKey
    this.workingDirectory = options.workingDirectory
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return nextSessionState(session, session.providerSessionId ?? randomUUID())
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    const sessionId = session.providerSessionId ?? randomUUID()
    const nextSession = nextSessionState(session, sessionId)

    try {
      const output = await runOpenClaudePrint(request.prompt, {
        model: this.model,
        sessionId,
        baseUrl: this.baseUrl,
        apiKey: this.apiKey,
        workingDirectory: this.workingDirectory,
        timeoutMs: request.timeout_ms,
      })

      const baseResult = enforceAlfredDirectIntentContract(request, successResult(output))
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithOpenClaude(output, {
        model: this.model,
        sessionId,
        baseUrl: this.baseUrl,
        apiKey: this.apiKey,
        workingDirectory: this.workingDirectory,
      }, request.reflection_prompt)

      return {
        session: nextSession,
        result: finalizeRuntimeResult(baseResult, reflectionResult),
      }
    } catch (error) {
      return { session: nextSession, result: errorResultFromError(error) }
    }
  }

  async interruptActiveExecution(_session: SessionState): Promise<void> {
    // Harness interruption wiring can be added later.
  }
}

export function createProviderAdapter(executionProfile: ExecutionProfile): ProviderSessionAdapter {
  if (executionProfile.runtime === 'claude-agent-sdk') {
    return new ClaudeAgentSdkAdapter(executionProfile.model, {
      apiKey: executionProfile.apiKey,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  if (executionProfile.runtime === 'openclaude-harness') {
    return new OpenClaudeHarnessAdapter(executionProfile.model, {
      baseUrl: executionProfile.baseUrl,
      apiKey: executionProfile.apiKey,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  if (executionProfile.runtime === 'simple-harness') {
    return new SimpleHarnessAdapter(executionProfile.model, {
      baseUrl: executionProfile.baseUrl,
      apiKey: executionProfile.apiKey,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  return new CodexSdkAdapter(executionProfile.model, {
    apiKey: executionProfile.apiKey,
    baseUrl: executionProfile.baseUrl,
    skipGitRepoCheck: executionProfile.skipGitRepoCheck ?? false,
    workingDirectory: executionProfile.workingDirectory,
  })
}
