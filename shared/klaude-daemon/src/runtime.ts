import { randomUUID } from 'node:crypto'
import { spawn, spawnSync } from 'node:child_process'
import { createWriteStream } from 'node:fs'
import path from 'node:path'
import { chmod, mkdir, readFile, readdir, rename, rm, stat, symlink, writeFile } from 'node:fs/promises'
import Anthropic from '@anthropic-ai/sdk'
import { query } from '@anthropic-ai/claude-agent-sdk'
import { GoogleGenAI, Type } from '@google/genai'
import { Codex } from '@openai/codex-sdk'
import type { ExecutionProfile } from './config.js'
import { log } from './log.js'
import { SimpleHarnessAdapter, classifyAlfredDirectIntent, enforceAlfredDirectIntentContract } from './simple-harness.js'
import type { ProgressReporter, ProviderSessionAdapter, ReflectionPayload, RuntimeRequest, RuntimeResult, SessionState, ResponseUsageMetadata } from './types.js'

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

type GeminiSdkToolName = 'bash' | 'read_file' | 'write_file' | 'list_dir' | 'read_run_file' | 'list_run_artifacts' | 'pass_show' | 'pass_insert'

type GeminiSdkToolCall = {
  id: string
  name: GeminiSdkToolName
  arguments: Record<string, unknown>
}

type RunArtifactContext = {
  runDir: string
  files: Map<string, string>
  factFiles: Set<string>
}

type RunArtifactSnapshot = {
  absolutePath: string
  existed: boolean
  size: number
  content?: Buffer
}

function renderFsToolError(prefix: string, error: unknown): string {
  const code = typeof (error as { code?: unknown }).code === 'string'
    ? String((error as { code?: string }).code ?? '')
    : ''
  const detail = error instanceof Error ? error.message : String(error)
  return code ? `${prefix}\n${code}: ${detail}` : `${prefix}\n${detail}`
}

async function reportProgress(progress: ProgressReporter | undefined, event: {
  source: 'agent-daemon' | 'provider' | 'gateway'
  kind: string
  runtime?: string
  model?: string
  session_id?: string
  structured_log_path?: string
  payload?: Record<string, unknown>
}): Promise<void> {
  if (!progress) return
  await progress(event)
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

function promptTelemetry(prompt: string, request?: RuntimeRequest, extra?: Record<string, unknown>): Record<string, unknown> {
  const promptMode = request?.promptPlan?.cacheKey
    ? prompt === request.promptPlan.dynamicPrompt
      ? 'dynamic-only'
      : 'full-with-prefix'
    : 'uncached'
  return {
    prompt_preview: summarizeText(prompt, 200),
    prompt_cache_key: request?.promptPlan?.cacheKey ?? null,
    prompt_mode: promptMode,
    ...(extra ?? {}),
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

function resolveSystemCommand(commandName: string): string | undefined {
  const resolved = spawnSync('bash', ['-lc', `command -v ${commandName}`], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
  })
  if (resolved.status !== 0) return undefined
  const candidate = resolved.stdout.trim()
  return candidate || undefined
}

async function ensureOpenClaudeCommandGuards(
  runtimeHome: string,
  request?: RuntimeRequest,
): Promise<string | undefined> {
  const forbiddenTargets = [
    request?.agent?.validator_script,
    request?.agent?.root_dir ? path.join(request.agent.root_dir, 'scripts', 'finalize_analysis.py') : undefined,
  ]
    .filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
    .map(value => value.trim())

  if (forbiddenTargets.length === 0) return undefined

  const realPython3 = resolveSystemCommand('python3')
  if (!realPython3) return undefined

  const guardDir = path.join(runtimeHome, '.daemon-tool-guards')
  await mkdir(guardDir, { recursive: true })

  const shellQuotedTargets = forbiddenTargets
    .map(target => `'${target.replace(/'/g, `'\"'\"'`)}'`)
    .join(' ')

  const wrapperScript = `#!/usr/bin/env bash
set -euo pipefail
REAL_PYTHON='${realPython3.replace(/'/g, `'\"'\"'`)}'
FORBIDDEN_TARGETS=(${shellQuotedTargets})
for arg in "$@"; do
  for forbidden in "\${FORBIDDEN_TARGETS[@]}"; do
    if [[ "$arg" == "$forbidden" ]]; then
      echo "Daemon-managed script unavailable in-session: $arg" >&2
      exit 126
    fi
  done
done
exec "$REAL_PYTHON" "$@"
`

  for (const commandName of ['python3', 'python']) {
    const wrapperPath = path.join(guardDir, commandName)
    await writeFile(wrapperPath, wrapperScript, 'utf8')
    await chmod(wrapperPath, 0o755)
  }

  return guardDir
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
  options: { model: string; sessionId: string; onMessage?: (message: Record<string, unknown>) => void | Promise<void> }
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
    void options.onMessage?.(parsed as unknown as Record<string, unknown>)
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
  options: { model: string; sessionId: string; homeDirectory?: string; progress?: ProgressReporter; request?: RuntimeRequest }
): Promise<{ output: string; providerSessionId?: string; structuredLogPath: string; structuredLogTail: string; usage?: ResponseUsageMetadata }> {
  const runtimeHome = resolveRuntimeHome(options.homeDirectory)
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
  await reportProgress(options.progress, {
    source: 'agent-daemon',
    kind: 'runtime.stream.start',
    runtime: 'codex-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
    payload: promptTelemetry(prompt, options.request),
  })

  try {
    const { events } = await thread.runStreamed(prompt)
    for await (const event of events) {
      structuredLogStream.write(`${JSON.stringify(event)}\n`)
      processCodexStructuredEvent(event, options)
      await reportProgress(options.progress, {
        source: 'provider',
        kind: event.type ?? 'unknown',
        runtime: 'codex-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
        payload: event as unknown as Record<string, unknown>,
      })
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
    await reportProgress(options.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.error',
      runtime: 'codex-sdk',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { error: error instanceof Error ? error.message : String(error) },
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
  await reportProgress(options.progress, {
    source: 'agent-daemon',
    kind: 'runtime.stream.complete',
    runtime: 'codex-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
    payload: usage ? { usage } : undefined,
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
  const sanitized = sanitizeClaudeStructuredMessage(message)
  const type = typeof message.type === 'string' ? message.type : 'unknown'
  log('claude_message', {
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    message_type: type,
    subtype: typeof sanitized.subtype === 'string' ? sanitized.subtype : null,
    parent_tool_use_id: typeof sanitized.parent_tool_use_id === 'string' ? sanitized.parent_tool_use_id : null,
    content: summarizeUnknown(sanitized, 1200) ?? null,
  })
}

function sanitizeClaudeStructuredMessage(message: Record<string, unknown>): Record<string, unknown> {
  if (!(message.type === 'system' && message.subtype === 'init')) return message
  if (!Object.prototype.hasOwnProperty.call(message, 'slash_commands')) return message
  const { slash_commands: _ignored, ...rest } = message
  return rest
}

async function runClaudeStructuredQuery(
  streamFactory: () => AsyncIterable<Record<string, unknown>>,
  options: { model: string; sessionId: string; homeDirectory?: string; progress?: ProgressReporter; request?: RuntimeRequest }
): Promise<{ messages: Record<string, unknown>[]; structuredLogPath: string; structuredLogTail: string }> {
  const runtimeHome = resolveRuntimeHome(options.homeDirectory)
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
  await reportProgress(options.progress, {
    source: 'agent-daemon',
    kind: 'runtime.stream.start',
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
    payload: promptTelemetry(options.request?.prompt ?? '', options.request),
  })

  try {
    for await (const message of streamFactory()) {
      const sanitized = sanitizeClaudeStructuredMessage(message)
      messages.push(sanitized)
      structuredLogStream.write(`${JSON.stringify(sanitized)}\n`)
      processClaudeStructuredMessage(sanitized, options)
      await reportProgress(options.progress, {
        source: 'provider',
        kind: typeof sanitized.type === 'string' ? sanitized.type : 'unknown',
        runtime: 'claude-agent-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
        payload: sanitized,
      })
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
    await reportProgress(options.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.error',
      runtime: 'claude-agent-sdk',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { error: error instanceof Error ? error.message : String(error) },
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
  await reportProgress(options.progress, {
    source: 'agent-daemon',
    kind: 'runtime.stream.complete',
    runtime: 'claude-agent-sdk',
    model: options.model,
    session_id: options.sessionId,
    structured_log_path: structuredLogPath,
    payload: { message_count: messages.length },
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

function isMissingOpenClaudeSessionError(error: unknown): boolean {
  if (!(error instanceof Error)) return false
  const message = error.message.toLowerCase()
  return message.includes('no conversation found with session id')
    || message.includes('session not found')
    || message.includes('could not find session')
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

function resolveRuntimeHome(homeDirectory?: string): string {
  return homeDirectory
    ?? process.env.AGENT_HOME_DIR
    ?? process.env.HOME
    ?? process.cwd()
}

async function ensureClaudeSkillRegistryFallback(runtimeHome: string): Promise<void> {
  const skillsRoot = path.join(runtimeHome, '.claude', 'skills')
  await mkdir(skillsRoot, { recursive: true })
  try {
    const existing = await readdir(skillsRoot)
    if (existing.length > 0) return
  } catch {
    // continue with fallback seeding
  }

  const specialization = (() => {
    const raw = process.env.AGENT_CONTRACT_JSON
    if (!raw) return process.env.AGENT_PROFILE ?? ''
    try {
      const parsed = JSON.parse(raw) as { specialization?: unknown }
      return typeof parsed.specialization === 'string' ? parsed.specialization : (process.env.AGENT_PROFILE ?? '')
    } catch {
      return process.env.AGENT_PROFILE ?? ''
    }
  })()

  const skillSources = [
    path.join(process.env.KORDINATE_HOME ?? '/app', 'shared', 'skills'),
    specialization
      ? path.join(process.env.KORDINATE_HOME ?? '/app', 'agents', specialization, 'skills')
      : '',
  ].filter(Boolean)

  for (const sourceRoot of skillSources) {
    let entries: string[] = []
    try {
      entries = await readdir(sourceRoot)
    } catch {
      continue
    }
    for (const entry of entries) {
      const sourcePath = path.join(sourceRoot, entry)
      try {
        const sourceStat = await stat(sourcePath)
        if (!sourceStat.isDirectory()) continue
      } catch {
        continue
      }
      const targetPath = path.join(skillsRoot, entry)
      try {
        await rm(targetPath, { recursive: true, force: true })
      } catch {
        // ignore
      }
      try {
        await symlink(sourcePath, targetPath, 'dir')
      } catch {
        // ignore
      }
    }
  }
}

function resolveTaskWorkingDirectory(request: RuntimeRequest, profile: { workingDirectory?: string; homeDirectory?: string }): string {
  return request.working_dir
    ?? profile.workingDirectory
    ?? profile.homeDirectory
    ?? process.cwd()
}

async function loadRunArtifactContext(runDir?: string): Promise<RunArtifactContext | undefined> {
  if (!runDir?.trim()) return undefined
  const normalizedRunDir = path.resolve(runDir.trim())
  const files = new Map<string, string>()
  const register = (relativePath: string | undefined): void => {
    if (!relativePath) return
    const trimmed = relativePath.trim().replace(/^\.?\//, '')
    if (!trimmed) return
    files.set(trimmed, path.join(normalizedRunDir, trimmed))
  }

  register('blast.json')
  register('atlas.json')
  register('narratives.yaml')
  register('meta.json')
  register('facts/index.json')
  register('facts/startup.json')

  try {
    const raw = await readFile(path.join(normalizedRunDir, 'facts', 'index.json'), 'utf8')
    const parsed = JSON.parse(raw) as {
      index?: {
        domains?: Array<{ file?: unknown }>
      }
    }
    for (const domain of parsed.index?.domains ?? []) {
      if (typeof domain?.file === 'string') register(domain.file)
    }
  } catch {
    // ignore missing or malformed facts index; callers can still use guaranteed files
  }

  try {
    const raw = await readFile(path.join(normalizedRunDir, 'facts', 'startup.json'), 'utf8')
    const parsed = JSON.parse(raw) as {
      startup_files?: unknown[]
      large_domains?: Array<{ file?: unknown }>
      domain_counts?: Array<{ file?: unknown }>
    }
    for (const item of parsed.startup_files ?? []) {
      if (typeof item === 'string') register(item)
    }
    for (const item of parsed.large_domains ?? []) {
      if (item && typeof item === 'object' && typeof item.file === 'string') register(item.file)
    }
    for (const item of parsed.domain_counts ?? []) {
      if (item && typeof item === 'object' && typeof item.file === 'string') register(item.file)
    }
  } catch {
    // ignore missing or malformed startup file
  }

  return {
    runDir: normalizedRunDir,
    files,
    factFiles: new Set(Array.from(files.keys()).filter(key => key.startsWith('facts/'))),
  }
}

function normalizeRunArtifactReference(input: string, artifactContext?: RunArtifactContext): string {
  if (!artifactContext) return input
  const trimmed = input.trim().replace(/^\.?\//, '')
  if (!trimmed) return input
  const direct = artifactContext.files.get(trimmed)
  if (direct) return direct

  if (trimmed === 'facts' || trimmed.startsWith('facts/')) {
    return path.join(artifactContext.runDir, trimmed)
  }
  if (['blast.json', 'atlas.json', 'narratives.yaml', 'meta.json'].includes(trimmed)) {
    return path.join(artifactContext.runDir, trimmed)
  }
  return input
}

function undeclaredFactReferences(command: string, artifactContext?: RunArtifactContext): string[] {
  if (!artifactContext) return []
  const matches = Array.from(command.matchAll(/(^|[\s"'`])((?:\.\/)?facts\/[A-Za-z0-9._-]+\.json)\b/g))
    .map(match => String(match[2] ?? '').replace(/^\.?\//, ''))
  const unique = Array.from(new Set(matches))
  return unique.filter(reference => !artifactContext.factFiles.has(reference))
}

function rewriteCommandRunArtifactPaths(command: string, artifactContext?: RunArtifactContext): string {
  if (!artifactContext) return command
  let rewritten = command
  const entries = Array.from(artifactContext.files.entries())
    .sort((a, b) => b[0].length - a[0].length)
  for (const [relativePath, absolutePath] of entries) {
    const escapedRelative = relativePath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`(^|[^A-Za-z0-9_./-])(?:\\.\\/)?${escapedRelative}(?=$|[^A-Za-z0-9_./-])`, 'g')
    rewritten = rewritten.replace(pattern, (_match, prefix: string) => `${prefix}${absolutePath}`)
  }
  return rewritten
}

function shellSingleQuote(value: string): string {
  return `'${value.replace(/'/g, `'\"'\"'`)}'`
}

function shellCandidates(): string[] {
  const candidates = [
    process.env.SHELL,
    '/bin/bash',
    '/usr/bin/bash',
    '/bin/sh',
    '/usr/bin/sh',
  ]
  return Array.from(new Set(
    candidates.filter((value): value is string => typeof value === 'string' && value.trim().length > 0),
  ))
}

function shellCommandArgs(shellPath: string, command: string): string[] {
  const shellName = path.basename(shellPath)
  return shellName === 'sh' ? ['-c', command] : ['-lc', command]
}

function withGitSafeDirectoryEnv(baseEnv: Record<string, string | undefined>, repoPath?: string): Record<string, string> {
  const normalized = Object.fromEntries(
    Object.entries(baseEnv).filter((entry): entry is [string, string] => typeof entry[1] === 'string'),
  )
  if (!repoPath?.trim()) return normalized
  if (normalized.GIT_CONFIG_COUNT !== undefined) return normalized
  return {
    ...normalized,
    GIT_CONFIG_COUNT: '1',
    GIT_CONFIG_KEY_0: 'safe.directory',
    GIT_CONFIG_VALUE_0: repoPath,
  }
}

function isPathInsideRoot(targetPath: string, rootPath?: string): boolean {
  if (!rootPath?.trim()) return true
  const normalizedRoot = path.resolve(rootPath)
  const normalizedTarget = path.resolve(targetPath)
  return normalizedTarget === normalizedRoot || normalizedTarget.startsWith(`${normalizedRoot}${path.sep}`)
}

async function runBashCommand(options: {
  command: string
  cwd?: string
  env?: Record<string, string>
  timeoutMs?: number
}): Promise<{ stdout: string; stderr: string }> {
  let lastError: unknown
  for (const shellPath of shellCandidates()) {
    try {
      return await new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
        const child = spawn(shellPath, shellCommandArgs(shellPath, options.command), {
          cwd: options.cwd,
          env: withGitSafeDirectoryEnv({
            ...process.env,
            ...(options.env ?? {}),
          }, options.cwd),
          stdio: ['ignore', 'pipe', 'pipe'],
        })
        let stdout = ''
        let stderr = ''
        const timeoutHandle = options.timeoutMs
          ? setTimeout(() => child.kill('SIGKILL'), options.timeoutMs)
          : undefined

        child.stdout.on('data', chunk => { stdout += chunk.toString() })
        child.stderr.on('data', chunk => { stderr += chunk.toString() })
        child.on('error', error => {
          if (timeoutHandle) clearTimeout(timeoutHandle)
          reject(Object.assign(error, { stdout, stderr, shellPath }))
        })
        child.on('close', code => {
          if (timeoutHandle) clearTimeout(timeoutHandle)
          if (code === 0) {
            resolve({ stdout, stderr })
            return
          }
          reject(Object.assign(new Error(stderr.trim() || stdout.trim() || `command failed with exit ${code}`), {
            stdout,
            stderr,
            exitCode: code ?? undefined,
            shellPath,
          }))
        })
      })
    } catch (error) {
      lastError = error
      const code = typeof error === 'object' && error && 'code' in error ? String((error as { code?: unknown }).code ?? '') : ''
      if (code === 'ENOENT') continue
      throw error
    }
  }
  throw lastError instanceof Error ? lastError : new Error('no usable shell found for bash command execution')
}

function protectedRunArtifactPaths(artifactContext?: RunArtifactContext): Array<{ relativePath: string; absolutePath: string }> {
  if (!artifactContext) return []
  return Array.from(artifactContext.files.entries())
    .filter(([relativePath]) => (
      relativePath === 'atlas.json'
      || relativePath === 'narratives.yaml'
      || relativePath.startsWith('stories/')
    ))
    .map(([relativePath, absolutePath]) => ({ relativePath, absolutePath }))
}

async function snapshotProtectedRunArtifacts(artifactContext?: RunArtifactContext): Promise<Map<string, RunArtifactSnapshot>> {
  const snapshots = new Map<string, RunArtifactSnapshot>()
  for (const { absolutePath } of protectedRunArtifactPaths(artifactContext)) {
    try {
      const info = await stat(absolutePath)
      const content = info.isFile() ? await readFile(absolutePath) : undefined
      snapshots.set(absolutePath, {
        absolutePath,
        existed: true,
        size: info.size,
        content,
      })
    } catch {
      snapshots.set(absolutePath, {
        absolutePath,
        existed: false,
        size: 0,
      })
    }
  }
  return snapshots
}

async function restoreProtectedRunArtifacts(snapshots: Map<string, RunArtifactSnapshot>): Promise<void> {
  for (const snapshot of snapshots.values()) {
    if (!snapshot.existed) continue
    await mkdir(path.dirname(snapshot.absolutePath), { recursive: true })
    if (snapshot.content) {
      await writeFile(snapshot.absolutePath, snapshot.content)
    } else {
      await writeFile(snapshot.absolutePath, Buffer.alloc(0))
    }
  }
}

async function ensureProtectedRunArtifactsIntact(
  snapshots: Map<string, RunArtifactSnapshot>,
): Promise<string[]> {
  const corrupted: string[] = []
  for (const snapshot of snapshots.values()) {
    if (!snapshot.existed || snapshot.size <= 0) continue
    try {
      const info = await stat(snapshot.absolutePath)
      if (info.size === 0) corrupted.push(snapshot.absolutePath)
    } catch {
      corrupted.push(snapshot.absolutePath)
    }
  }
  return corrupted
}

async function writeFileAtomic(absolutePath: string, content: string): Promise<void> {
  await mkdir(path.dirname(absolutePath), { recursive: true })
  const tempPath = `${absolutePath}.${randomUUID()}.tmp`
  await writeFile(tempPath, content, 'utf8')
  await rename(tempPath, absolutePath)
}

function passEnv(): Record<string, string> {
  const env: Record<string, string> = {}
  if (process.env.PASSWORD_STORE_DIR) env.PASSWORD_STORE_DIR = process.env.PASSWORD_STORE_DIR
  if (process.env.GNUPGHOME) env.GNUPGHOME = process.env.GNUPGHOME
  return env
}

async function passShow(keyPath: string, cwd?: string): Promise<string> {
  const { stdout } = await runBashCommand({
    command: `pass show ${shellSingleQuote(keyPath)}`,
    cwd,
    env: passEnv(),
    timeoutMs: 10000,
  })
  return stdout.trimEnd()
}

async function passInsert(keyPath: string, value: string, cwd?: string): Promise<void> {
  await runBashCommand({
    command: `printf '%s\\n' ${shellSingleQuote(value)} | pass insert -m -f ${shellSingleQuote(keyPath)}`,
    cwd,
    env: passEnv(),
    timeoutMs: 10000,
  })
}

function geminiSdkFunctionDeclarations(): Array<Record<string, unknown>> {
  return [
    {
      name: 'bash',
      description: 'Run one bash command in the current working directory.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          command: { type: Type.STRING, description: 'Shell command to execute.' },
        },
        required: ['command'],
      },
    },
    {
      name: 'read_file',
      description: 'Read the contents of a UTF-8 text file.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          path: { type: Type.STRING, description: 'Absolute path or path relative to the working directory.' },
        },
        required: ['path'],
      },
    },
    {
      name: 'write_file',
      description: 'Write UTF-8 text to a file path.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          path: { type: Type.STRING, description: 'Absolute path or path relative to the working directory.' },
          content: { type: Type.STRING, description: 'File content to write.' },
        },
        required: ['path', 'content'],
      },
    },
    {
      name: 'list_dir',
      description: 'List files and directories for one path.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          path: { type: Type.STRING, description: 'Absolute path or path relative to the working directory.' },
        },
        required: ['path'],
      },
    },
    {
      name: 'read_run_file',
      description: 'Read a prepared analysis run artifact by relative path, such as facts/index.json or atlas.json.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          path: { type: Type.STRING, description: 'Run-artifact path relative to the prepared run directory.' },
        },
        required: ['path'],
      },
    },
    {
      name: 'list_run_artifacts',
      description: 'List the prepared run artifacts currently available for this analysis run.',
      parameters: {
        type: Type.OBJECT,
        properties: {},
      },
    },
    {
      name: 'pass_show',
      description: 'Read a secret from the shared pass store.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          key_path: { type: Type.STRING, description: 'Pass key path to read.' },
        },
        required: ['key_path'],
      },
    },
    {
      name: 'pass_insert',
      description: 'Store a secret in the shared pass store and overwrite if it already exists.',
      parameters: {
        type: Type.OBJECT,
        properties: {
          key_path: { type: Type.STRING, description: 'Pass key path to write.' },
          value: { type: Type.STRING, description: 'Secret value to store.' },
        },
        required: ['key_path', 'value'],
      },
    },
  ]
}

async function executeGeminiSdkToolCall(
  call: GeminiSdkToolCall,
  cwd: string,
  env?: Record<string, string>,
  artifactContext?: RunArtifactContext,
): Promise<string> {
  switch (call.name) {
    case 'bash': {
      const originalCommand = String(call.arguments.command ?? '')
      const undeclaredFacts = undeclaredFactReferences(originalCommand, artifactContext)
      if (undeclaredFacts.length > 0) {
        throw new Error(`Run artifact(s) not declared in facts/index.json: ${undeclaredFacts.join(', ')}`)
      }
      const command = rewriteCommandRunArtifactPaths(originalCommand, artifactContext)
      const protectedSnapshots = await snapshotProtectedRunArtifacts(artifactContext)
      try {
        const { stdout, stderr } = await runBashCommand({ command, cwd, env, timeoutMs: 10000 })
        const corrupted = await ensureProtectedRunArtifactsIntact(protectedSnapshots)
        if (corrupted.length > 0) {
          await restoreProtectedRunArtifacts(protectedSnapshots)
          return `bash failed\nProtected run artifact write left empty or missing file(s): ${corrupted.join(', ')}`
        }
        return stderr ? `${stdout}${stdout && !stdout.endsWith('\n') ? '\n' : ''}${stderr}`.trimEnd() : stdout.trimEnd()
      } catch (error) {
        await restoreProtectedRunArtifacts(protectedSnapshots)
        const stdout = typeof (error as { stdout?: unknown }).stdout === 'string'
          ? String((error as { stdout?: string }).stdout ?? '')
          : ''
        const stderr = typeof (error as { stderr?: unknown }).stderr === 'string'
          ? String((error as { stderr?: string }).stderr ?? '')
          : ''
        const exitCode = typeof (error as { exitCode?: unknown }).exitCode === 'number'
          ? Number((error as { exitCode?: number }).exitCode)
          : undefined
        const summary = error instanceof Error ? error.message : String(error)
        const rendered = `${stdout}${stdout && stderr && !stdout.endsWith('\n') ? '\n' : ''}${stderr}`.trimEnd()
        const prefix = exitCode !== undefined ? `bash exited ${exitCode}` : 'bash failed'
        return rendered.length > 0 ? `${prefix}\n${rendered}` : `${prefix}\n${summary}`
      }
    }
    case 'read_file': {
      const target = String(call.arguments.path ?? '')
      const normalizedTarget = normalizeRunArtifactReference(target, artifactContext)
      try {
        return await readFile(path.isAbsolute(normalizedTarget) ? normalizedTarget : path.join(cwd, normalizedTarget), 'utf8')
      } catch (error) {
        return renderFsToolError('read_file failed', error)
      }
    }
    case 'write_file': {
      const target = String(call.arguments.path ?? '')
      const content = String(call.arguments.content ?? '')
      const normalizedTarget = normalizeRunArtifactReference(target, artifactContext)
      const absolute = path.isAbsolute(normalizedTarget) ? normalizedTarget : path.join(cwd, normalizedTarget)
      const outputDir = env?.OUTPUT_DIR
      if (!isPathInsideRoot(absolute, outputDir)) {
        throw new Error(`write_file denied outside output_dir: ${absolute}`)
      }
      await writeFileAtomic(absolute, content)
      return 'written'
    }
    case 'list_dir': {
      const target = String(call.arguments.path ?? '')
      const normalizedTarget = normalizeRunArtifactReference(target, artifactContext)
      const absolute = path.isAbsolute(normalizedTarget) ? normalizedTarget : path.join(cwd, normalizedTarget)
      try {
        const entries = await readdir(absolute, { withFileTypes: true })
        const payload = await Promise.all(entries.map(async entry => {
          const full = path.join(absolute, entry.name)
          const info = await stat(full)
          return {
            name: entry.name,
            type: entry.isDirectory() ? 'dir' : entry.isFile() ? 'file' : 'other',
            size: info.size,
          }
        }))
        return JSON.stringify(payload)
      } catch (error) {
        return renderFsToolError('list_dir failed', error)
      }
    }
    case 'read_run_file': {
      const target = String(call.arguments.path ?? '').replace(/^\.?\//, '')
      if (!artifactContext) {
        throw new Error('No prepared run artifact context is available for this request')
      }
      const absolute = artifactContext.files.get(target) ?? path.join(artifactContext.runDir, target)
      try {
        return await readFile(absolute, 'utf8')
      } catch (error) {
        return renderFsToolError(`read_run_file failed for ${target}`, error)
      }
    }
    case 'list_run_artifacts': {
      if (!artifactContext) {
        throw new Error('No prepared run artifact context is available for this request')
      }
      return JSON.stringify({
        run_dir: artifactContext.runDir,
        files: Array.from(artifactContext.files.keys()).sort(),
      }, null, 2)
    }
    case 'pass_show':
      return await passShow(String(call.arguments.key_path ?? ''), cwd)
    case 'pass_insert':
      await passInsert(String(call.arguments.key_path ?? ''), String(call.arguments.value ?? ''), cwd)
      return 'stored'
  }
  throw new Error(`Unsupported Gemini tool call: ${String(call.name)}`)
}

async function loadGeminiSessionHistory(runtimeHome: string, sessionId: string): Promise<Array<Record<string, unknown>>> {
  const dir = path.join(runtimeHome, '.daemon-state', 'gemini-sessions')
  const file = path.join(dir, `${sessionId}.json`)
  try {
    const raw = await readFile(file, 'utf8')
    const parsed = JSON.parse(raw) as unknown
    return Array.isArray(parsed) ? parsed as Array<Record<string, unknown>> : []
  } catch {
    return []
  }
}

async function saveGeminiSessionHistory(runtimeHome: string, sessionId: string, history: Array<Record<string, unknown>>): Promise<void> {
  const dir = path.join(runtimeHome, '.daemon-state', 'gemini-sessions')
  await mkdir(dir, { recursive: true })
  const file = path.join(dir, `${sessionId}.json`)
  await writeFile(file, `${JSON.stringify(history, null, 2)}\n`, 'utf8')
}

type GeminiPromptCacheRecord = {
  name: string
  model: string
  cacheKey: string
  createdAt: string
}

function geminiPromptCacheDir(runtimeHome: string): string {
  return path.join(runtimeHome, '.daemon-state', 'gemini-prompt-caches')
}

async function loadGeminiPromptCache(runtimeHome: string, cacheKey: string): Promise<GeminiPromptCacheRecord | undefined> {
  const file = path.join(geminiPromptCacheDir(runtimeHome), `${cacheKey}.json`)
  try {
    const raw = await readFile(file, 'utf8')
    return JSON.parse(raw) as GeminiPromptCacheRecord
  } catch {
    return undefined
  }
}

async function saveGeminiPromptCache(runtimeHome: string, record: GeminiPromptCacheRecord): Promise<void> {
  const dir = geminiPromptCacheDir(runtimeHome)
  await mkdir(dir, { recursive: true })
  const file = path.join(dir, `${record.cacheKey}.json`)
  await writeFile(file, `${JSON.stringify(record, null, 2)}\n`, 'utf8')
}

async function ensureGeminiCachedContent(input: {
  client: GoogleGenAI
  runtimeHome: string
  model: string
  cacheKey: string
  cacheablePrefix: string
  writeEvent?: (event: Record<string, unknown>) => Promise<void>
}): Promise<string | undefined> {
  const existing = await loadGeminiPromptCache(input.runtimeHome, input.cacheKey)
  if (existing?.name) {
    try {
      await input.client.caches.get({ name: existing.name })
      await input.writeEvent?.({
        type: 'prompt_cache',
        subtype: 'hit',
        cache_key: input.cacheKey,
        cache_name: existing.name,
      })
      return existing.name
    } catch {
      await input.writeEvent?.({
        type: 'prompt_cache',
        subtype: 'stale',
        cache_key: input.cacheKey,
        cache_name: existing.name,
      })
    }
  }

  const created = await input.client.caches.create({
    model: input.model,
    config: {
      displayName: `klaude-${input.model}-${input.cacheKey.slice(0, 12)}`,
      contents: [{
        role: 'user',
        parts: [{ text: input.cacheablePrefix }],
      }] as never,
      ttl: process.env.GEMINI_CONTEXT_CACHE_TTL ?? '86400s',
    },
  })
  const record: GeminiPromptCacheRecord = {
    name: String(created.name ?? ''),
    model: input.model,
    cacheKey: input.cacheKey,
    createdAt: new Date().toISOString(),
  }
  if (record.name) {
    await saveGeminiPromptCache(input.runtimeHome, record)
    await input.writeEvent?.({
      type: 'prompt_cache',
      subtype: 'miss',
      cache_key: input.cacheKey,
      cache_name: record.name,
    })
    return record.name
  }
  return undefined
}

async function runOpenClaudePrint(prompt: string, options: {
  model: string
  sessionId: string
  resumeSessionId?: string
  baseUrl?: string
  apiKey?: string
  homeDirectory?: string
  workingDirectory?: string
  timeoutMs?: number
  progress?: ProgressReporter
  request?: RuntimeRequest
}): Promise<string> {
  const env: Record<string, string> = {}
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined) env[key] = value
  }
  const runtimeHome = resolveRuntimeHome(options.homeDirectory)
  await ensureClaudeSkillRegistryFallback(runtimeHome)
  const cwd = options.workingDirectory ?? runtimeHome
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
  env.KORDINATE_HOME = process.env.KORDINATE_HOME ?? '/app'
  if (typeof options.request?.workspace?.working_dir === 'string' && options.request.workspace.working_dir.trim()) {
    env.WORKING_DIR = options.request.workspace.working_dir.trim()
  }
  if (typeof options.request?.workspace?.output_dir === 'string' && options.request.workspace.output_dir.trim()) {
    env.OUTPUT_DIR = options.request.workspace.output_dir.trim()
  }
  if (typeof options.request?.agent?.root_dir === 'string' && options.request.agent.root_dir.trim()) {
    env.AGENT_ROOT = options.request.agent.root_dir.trim()
  }
  if (typeof options.request?.agent?.validator_script === 'string' && options.request.agent.validator_script.trim()) {
    env.VALIDATOR_SCRIPT = options.request.agent.validator_script.trim()
  }
  if (typeof options.request?.agent?.concept_catalog_index === 'string' && options.request.agent.concept_catalog_index.trim()) {
    env.CONCEPT_CATALOG_INDEX = options.request.agent.concept_catalog_index.trim()
  }
  if (typeof options.request?.agent?.framework_catalog_index === 'string' && options.request.agent.framework_catalog_index.trim()) {
    env.FRAMEWORK_CATALOG_INDEX = options.request.agent.framework_catalog_index.trim()
  }
  const guardDir = await ensureOpenClaudeCommandGuards(runtimeHome, options.request)
  if (guardDir) {
    env.PATH = `${guardDir}:${env.PATH ?? process.env.PATH ?? ''}`
  }
  Object.assign(env, withGitSafeDirectoryEnv({}, cwd))

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
    '--model', options.model,
  )
  if (options.resumeSessionId) {
    args.push('--resume', options.resumeSessionId)
  } else {
    args.push('--session-id', options.sessionId)
  }
  args.push(prompt)
  const command = ensureOpenClaudeCommand()

  return await new Promise<string>((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
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
      task_cwd: cwd,
      debug_log_path: debugLogPath,
      structured_log_path: structuredLogPath,
      timeout_ms: timeoutMs ?? null,
    })
    void reportProgress(options.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.start',
      runtime: 'openclaude-harness',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: promptTelemetry(prompt, options.request, { task_cwd: cwd }),
    })

    child.stdout.on('data', chunk => {
      const chunkText = chunk.toString()
      stdout += chunkText
      consumeOpenClaudeStructuredChunk(structuredState, chunkText, {
        ...options,
        onMessage: message => reportProgress(options.progress, {
          source: 'provider',
          kind: typeof message.type === 'string' ? message.type : 'unknown',
          runtime: 'openclaude-harness',
          model: options.model,
          session_id: options.sessionId,
          structured_log_path: structuredLogPath,
          payload: message,
        }),
      })
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
      void reportProgress(options.progress, {
        source: 'agent-daemon',
        kind: 'runtime.stream.error',
        runtime: 'openclaude-harness',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
        payload: { error: error.message, timed_out: timedOut },
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
        void reportProgress(options.progress, {
          source: 'agent-daemon',
          kind: 'runtime.stream.error',
          runtime: 'openclaude-harness',
          model: options.model,
          session_id: options.sessionId,
          structured_log_path: structuredLogPath,
          payload: { exit_code: code ?? null, signal: signal ?? null, timed_out: timedOut },
        })
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
      void reportProgress(options.progress, {
        source: 'agent-daemon',
        kind: 'runtime.stream.complete',
        runtime: 'openclaude-harness',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
        payload: { result_preview: summarizeText(resultText, 200) },
      })
      resolve(resultText)
    })
  })
}

async function maybeReflectWithOpenClaude(taskOutput: string, options: { model: string; sessionId: string; baseUrl?: string; apiKey?: string; homeDirectory?: string; workingDirectory?: string }, reflectionPrompt?: string): Promise<{ reflection?: ReflectionPayload; errors?: string[] }> {
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
  private readonly homeDirectory?: string
  private readonly workingDirectory?: string

  constructor(model: string, options: { apiKey?: string; homeDirectory?: string; workingDirectory?: string }) {
    this.model = model
    this.apiKey = options.apiKey
    this.homeDirectory = options.homeDirectory
    this.workingDirectory = options.workingDirectory
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return session
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    if (!this.apiKey) {
      return { session, result: errorResult('BACKEND_API_KEY is not configured for Claude runtime') }
    }

    const sessionId = session.providerSessionId ?? randomUUID()
    const runtimeHome = resolveRuntimeHome(this.homeDirectory)
    await ensureClaudeSkillRegistryFallback(runtimeHome)
    const env = {
      ...process.env,
      ANTHROPIC_API_KEY: this.apiKey,
      HOME: runtimeHome,
    }

    try {
      const executeOnce = async (resumeSessionId?: string): Promise<{ text: string; nextSessionId: string }> => {
        let text = ''
        let nextSessionId = sessionId
        const cwd = resolveTaskWorkingDirectory(request, {
          homeDirectory: this.homeDirectory,
          workingDirectory: this.workingDirectory,
        })
        const { messages } = await runClaudeStructuredQuery(
          () => query({
            prompt: request.prompt,
            options: {
              cwd,
              resume: resumeSessionId,
              model: this.model,
              permissionMode: 'bypassPermissions',
              env,
            },
          }) as unknown as AsyncIterable<Record<string, unknown>>,
          {
            model: this.model,
            sessionId,
            homeDirectory: this.homeDirectory,
            progress: request.progress,
            request,
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
      return { session, result: errorResultFromError(error) }
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
  private readonly homeDirectory?: string
  private readonly workingDirectory?: string
  private readonly sandboxMode: 'read-only' | 'workspace-write' | 'danger-full-access'

  constructor(model: string, options: { apiKey?: string; baseUrl?: string; skipGitRepoCheck: boolean; homeDirectory?: string; workingDirectory?: string; sandboxMode?: 'read-only' | 'workspace-write' | 'danger-full-access' }) {
    const env: Record<string, string> = {}
    for (const [key, value] of Object.entries(process.env)) {
      if (value !== undefined && key !== 'OPENAI_BASE_URL') {
        env[key] = value
      }
    }
    const runtimeHome = resolveRuntimeHome(options.homeDirectory ?? options.workingDirectory)
    env.HOME = runtimeHome
    env.AGENT_HOME_DIR = options.homeDirectory ?? env.AGENT_HOME_DIR ?? runtimeHome

    this.codex = new Codex({
      apiKey: options.apiKey,
      baseUrl: options.baseUrl,
      env,
    })
    this.model = model
    this.skipGitRepoCheck = options.skipGitRepoCheck
    this.homeDirectory = options.homeDirectory
    this.workingDirectory = options.workingDirectory
    this.sandboxMode = options.sandboxMode ?? 'workspace-write'
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return session
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    try {
      const cwd = resolveTaskWorkingDirectory(request, {
        homeDirectory: this.homeDirectory,
        workingDirectory: this.workingDirectory,
      })
      const threadOptions = {
        model: this.model,
        sandboxMode: this.sandboxMode,
        approvalPolicy: 'never' as const,
        networkAccessEnabled: true,
        skipGitRepoCheck: this.skipGitRepoCheck,
        workingDirectory: cwd,
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
          homeDirectory: this.homeDirectory ?? this.workingDirectory,
          progress: request.progress,
          request,
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

export class GeminiSdkAdapter implements ProviderSessionAdapter {
  private readonly client: GoogleGenAI
  private readonly model: string
  private readonly apiKey?: string
  private readonly homeDirectory?: string
  private readonly workingDirectory?: string
  private readonly maxSteps: number

  constructor(model: string, options: { apiKey?: string; homeDirectory?: string; workingDirectory?: string; maxSteps?: number }) {
    this.client = new GoogleGenAI({ apiKey: options.apiKey })
    this.model = model
    this.apiKey = options.apiKey
    this.homeDirectory = options.homeDirectory
    this.workingDirectory = options.workingDirectory
    this.maxSteps = options.maxSteps ?? Number.parseInt(process.env.GEMINI_SDK_MAX_STEPS ?? '64', 10)
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return session
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    if (!this.apiKey) {
      return { session, result: errorResult('BACKEND_API_KEY is not configured for Gemini runtime') }
    }

    const sessionId = session.providerSessionId ?? randomUUID()
    const nextSession = nextSessionState(session, sessionId)
    const runtimeHome = resolveRuntimeHome(this.homeDirectory)
    const cwd = resolveTaskWorkingDirectory(request, {
      homeDirectory: this.homeDirectory,
      workingDirectory: this.workingDirectory,
    })
    const runDir = typeof request.agent_params?.run_dir === 'string' && request.agent_params.run_dir.trim()
      ? request.agent_params.run_dir.trim()
      : undefined
    const artifactContext = await loadRunArtifactContext(runDir)
    const toolEnv = {
      AGENT_HOME_DIR: runtimeHome,
      KORDINATE_HOME: process.env.KORDINATE_HOME ?? '/app',
      ...(request.agent?.root_dir ? { AGENT_ROOT: request.agent.root_dir } : {}),
      ...(request.agent?.concept_catalog_index ? { CONCEPT_CATALOG_INDEX: request.agent.concept_catalog_index } : {}),
      ...(request.agent?.framework_catalog_index ? { FRAMEWORK_CATALOG_INDEX: request.agent.framework_catalog_index } : {}),
      ...(request.agent?.validator_script ? { VALIDATOR_SCRIPT: request.agent.validator_script } : {}),
      WORKING_DIR: request.workspace?.working_dir ?? request.working_dir ?? this.workingDirectory ?? this.homeDirectory ?? process.cwd(),
      ...(runDir
        ? {
            OUTPUT_DIR: request.workspace?.output_dir ?? runDir,
            RUN: runDir,
          }
        : {}),
    }
    const debugDir = path.join(runtimeHome, '.daemon-logs')

    try {
      await mkdir(debugDir, { recursive: true })
      const structuredLogPath = path.join(debugDir, `gemini-sdk-${sessionId}-${Date.now()}-stream.jsonl`)
      const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
      const history = await loadGeminiSessionHistory(runtimeHome, sessionId)
      const writeEvent = async (event: Record<string, unknown>) => {
        structuredLogStream.write(`${JSON.stringify(event)}\n`)
        await reportProgress(request.progress, {
          source: 'provider',
          kind: typeof event.type === 'string' ? event.type : 'unknown',
          runtime: 'gemini-sdk',
          model: this.model,
          session_id: sessionId,
          structured_log_path: structuredLogPath,
          payload: event,
        })
      }
      if (request.promptPlan?.cacheablePrefix && request.promptPlan.cacheKey) {
        await writeEvent({
          type: 'prompt_cache',
          subtype: 'bypass',
          cache_key: request.promptPlan.cacheKey,
          message: 'Gemini SDK provider cache bypassed; relying on session history reuse for tool-enabled runs.',
        })
      }
      const usingDynamicOnlyPrompt = Boolean(request.promptPlan?.cacheKey && request.prompt === request.promptPlan.dynamicPrompt)
      const promptText = usingDynamicOnlyPrompt
        ? request.prompt
        : request.promptPlan?.fullPrompt ?? request.prompt
      if (history.length === 0) {
        history.push({
          role: 'user',
          parts: [{ text: promptText }],
        })
      } else {
        history.push({
          role: 'user',
          parts: [{ text: promptText }],
        })
      }

      await reportProgress(request.progress, {
        source: 'agent-daemon',
        kind: 'runtime.stream.start',
        runtime: 'gemini-sdk',
        model: this.model,
        session_id: sessionId,
        structured_log_path: structuredLogPath,
        payload: {
          cwd,
          run_dir: runDir ?? null,
          prompt_preview: summarizeText(promptText, 200),
          prompt_cache_key: request.promptPlan?.cacheKey,
          cached_content: null,
          prompt_mode: usingDynamicOnlyPrompt ? 'dynamic-only' : 'full-with-prefix',
        },
      })

      let finalText = ''
      for (let step = 0; step < this.maxSteps; step += 1) {
        const response = await this.client.models.generateContent({
          model: this.model,
          contents: history as never,
          config: {
            tools: [{ functionDeclarations: geminiSdkFunctionDeclarations() }] as never,
          } as never,
        })
        await writeEvent({
          type: 'raw_response',
          step,
          summary: summarizeUnknown(response, 4000) ?? 'unserializable Gemini response',
        })

        const candidate = Array.isArray((response as { candidates?: unknown[] }).candidates)
          ? (response as { candidates?: Array<{ content?: Record<string, unknown> }> }).candidates?.[0]
          : undefined
        const content = candidate?.content
        if (content) {
          history.push(content)
          await writeEvent({ type: 'assistant', message: content })
        }

        const functionCalls = Array.isArray((response as { functionCalls?: unknown[] }).functionCalls)
          ? (response as { functionCalls?: Array<{ id?: string; name?: string; args?: Record<string, unknown> }> }).functionCalls ?? []
          : []

        if (functionCalls.length === 0) {
          finalText = typeof (response as { text?: unknown }).text === 'string'
            ? String((response as { text?: string }).text ?? '').trim()
            : ''
          if (!content && finalText.length === 0) {
            const responseSummary = summarizeUnknown(response, 4000) ?? 'empty Gemini response'
            await writeEvent({
              type: 'empty_response',
              step,
              summary: responseSummary,
            })
            throw new Error(`Gemini returned no content, tool calls, or text. Response summary: ${responseSummary}`)
          }
          await writeEvent({ type: 'result', subtype: 'success', result: finalText })
          await reportProgress(request.progress, {
            source: 'agent-daemon',
            kind: 'runtime.stream.complete',
            runtime: 'gemini-sdk',
            model: this.model,
            session_id: sessionId,
            structured_log_path: structuredLogPath,
            payload: { result_preview: summarizeText(finalText, 200) },
          })
          break
        }

        for (const functionCall of functionCalls) {
          const call: GeminiSdkToolCall = {
            id: String(functionCall.id ?? randomUUID()),
            name: String(functionCall.name ?? '') as GeminiSdkToolName,
            arguments: functionCall.args ?? {},
          }
          await writeEvent({ type: 'tool_use', id: call.id, name: call.name, arguments: call.arguments })
          const output = await executeGeminiSdkToolCall(call, cwd, toolEnv, artifactContext)
          await writeEvent({ type: 'tool_result', id: call.id, name: call.name, output: summarizeText(output, 1200) })
          history.push({
            role: 'user',
            parts: [{
              functionResponse: {
                id: call.id,
                name: call.name,
                response: { output },
              },
            }],
          })
        }
      }

      await saveGeminiSessionHistory(runtimeHome, sessionId, history)
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
      const baseResult = enforceAlfredDirectIntentContract(request, successResult(finalText))
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }
      return { session: nextSession, result: baseResult }
    } catch (error) {
      const rendered = error instanceof Error ? error.message : String(error)
      await reportProgress(request.progress, {
        source: 'agent-daemon',
        kind: 'runtime.stream.error',
        runtime: 'gemini-sdk',
        model: this.model,
        session_id: sessionId,
        payload: {
          error: rendered,
          prompt_cache_key: request.promptPlan?.cacheKey ?? null,
        },
      })
      log('gemini_sdk_execute_error', {
        runtime: 'gemini-sdk',
        model: this.model,
        session_id: sessionId,
        cwd,
        prompt_cache_key: request.promptPlan?.cacheKey ?? null,
        error: rendered,
      })
      return { session: nextSession, result: errorResultFromError(error) }
    }
  }

  async interruptActiveExecution(_session: SessionState): Promise<void> {
    // No-op for Gemini SDK adapter.
  }
}

export class OpenClaudeHarnessAdapter implements ProviderSessionAdapter {
  private readonly model: string
  private readonly baseUrl?: string
  private readonly apiKey?: string
  private readonly homeDirectory?: string
  private readonly workingDirectory?: string

  constructor(model: string, options: { baseUrl?: string; apiKey?: string; homeDirectory?: string; workingDirectory?: string }) {
    this.model = model
    this.baseUrl = options.baseUrl
    this.apiKey = options.apiKey
    this.homeDirectory = options.homeDirectory
    this.workingDirectory = options.workingDirectory
  }

  async startOrResumeWarmSession(session: SessionState): Promise<SessionState> {
    return session
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    const sessionId = session.providerSessionId ?? randomUUID()

    try {
      const executeOnce = async (resumeSessionId?: string): Promise<{ output: string; nextSessionId: string }> => {
        const cwd = resolveTaskWorkingDirectory(request, {
          homeDirectory: this.homeDirectory,
          workingDirectory: this.workingDirectory,
        })
        const output = await runOpenClaudePrint(request.prompt, {
          model: this.model,
          sessionId,
          resumeSessionId,
          baseUrl: this.baseUrl,
          apiKey: this.apiKey,
          homeDirectory: this.homeDirectory,
          workingDirectory: cwd,
          timeoutMs: request.timeout_ms,
          progress: request.progress,
          request,
        })
        return {
          output,
          nextSessionId: resumeSessionId ?? sessionId,
        }
      }

      let run: { output: string; nextSessionId: string }
      try {
        run = await executeOnce(session.providerSessionId)
      } catch (error) {
        if (!session.providerSessionId || !isMissingOpenClaudeSessionError(error)) throw error
        log('openclaude_session_resume_failed', {
          model: this.model,
          stale_session_id: session.providerSessionId,
          reason: error instanceof Error ? error.message : String(error),
        })
        run = await executeOnce(undefined)
      }

      const nextSession = nextSessionState(session, run.nextSessionId)

      const baseResult = enforceAlfredDirectIntentContract(request, successResult(run.output))
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithOpenClaude(run.output, {
        model: this.model,
        sessionId: run.nextSessionId,
        baseUrl: this.baseUrl,
        apiKey: this.apiKey,
        homeDirectory: this.homeDirectory,
        workingDirectory: this.homeDirectory ?? this.workingDirectory,
      }, request.reflection_prompt)

      return {
        session: nextSession,
        result: finalizeRuntimeResult(baseResult, reflectionResult),
      }
    } catch (error) {
      return { session, result: errorResultFromError(error) }
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
      homeDirectory: executionProfile.homeDirectory,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  if (executionProfile.runtime === 'openclaude-harness') {
    return new OpenClaudeHarnessAdapter(executionProfile.model, {
      baseUrl: executionProfile.baseUrl,
      apiKey: executionProfile.apiKey,
      homeDirectory: executionProfile.homeDirectory,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  if (executionProfile.runtime === 'gemini-sdk') {
    return new GeminiSdkAdapter(executionProfile.model, {
      apiKey: executionProfile.apiKey,
      homeDirectory: executionProfile.homeDirectory,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  if (executionProfile.runtime === 'simple-harness') {
    return new SimpleHarnessAdapter(executionProfile.model, {
      baseUrl: executionProfile.baseUrl,
      apiKey: executionProfile.apiKey,
      homeDirectory: executionProfile.homeDirectory,
      workingDirectory: executionProfile.workingDirectory,
    })
  }
  return new CodexSdkAdapter(executionProfile.model, {
    apiKey: executionProfile.apiKey,
    baseUrl: executionProfile.baseUrl,
    skipGitRepoCheck: executionProfile.skipGitRepoCheck ?? false,
    homeDirectory: executionProfile.homeDirectory,
    workingDirectory: executionProfile.workingDirectory,
    sandboxMode: executionProfile.sandboxMode,
  })
}
