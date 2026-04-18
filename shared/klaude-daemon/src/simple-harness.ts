import { randomUUID } from 'node:crypto'
import { spawn } from 'node:child_process'
import { createWriteStream } from 'node:fs'
import path from 'node:path'
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises'
import { log } from './log.js'
import type { ProgressReporter, ReflectionPayload, ProviderSessionAdapter, RuntimeRequest, RuntimeResult, SessionState } from './types.js'

type SimpleHarnessToolName = 'read_file' | 'write_file' | 'list_dir' | 'pass_show' | 'pass_insert'

type SimpleHarnessToolCall = {
  id: string
  name: SimpleHarnessToolName
  arguments: Record<string, unknown>
}

type AlfredDirectIntent =
  | { kind: 'get_secret'; keyPath: string }
  | { kind: 'store_secret'; keyPath: string; value: string }

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

function successResult(output: string): RuntimeResult {
  return {
    status: 'success',
    output,
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

function errorResultFromError(error: unknown): RuntimeResult {
  const details = formatProviderError(error)
  return {
    status: 'error',
    output: details[0] ?? 'unknown provider error',
    errors: details,
  }
}

function nextSessionState(session: SessionState, providerSessionId?: string): SessionState {
  return {
    ...session,
    providerSessionId: providerSessionId ?? session.providerSessionId,
  }
}

function shouldReflect(request: RuntimeRequest): boolean {
  return request.reflect === true
}

function isAlfredRuntimeContext(): boolean {
  const profile = (process.env.AGENT_PROFILE_NAME ?? '').trim().toLowerCase()
  const name = (process.env.AGENT_NAME ?? '').trim().toLowerCase()
  return profile === 'alfred' || name.startsWith('alfred')
}

export function classifyAlfredDirectIntent(prompt: string): AlfredDirectIntent | undefined {
  const trimmed = prompt.trim()
  const getMatch = /^get key ([^\s]+)\s*$/i.exec(trimmed)
  if (getMatch) {
    return { kind: 'get_secret', keyPath: getMatch[1] }
  }
  const storeMatch = /^store key ([^\s]+)\s+value\s+([\s\S]+)$/i.exec(trimmed)
  if (storeMatch) {
    return { kind: 'store_secret', keyPath: storeMatch[1], value: storeMatch[2].trim() }
  }
  return undefined
}

function resolveOriginalPrompt(request: RuntimeRequest): string {
  return request.raw_prompt?.trim() || request.prompt.trim()
}

function resolveRuntimeHome(homeDirectory?: string): string {
  return homeDirectory ?? process.env.AGENT_HOME_DIR ?? process.cwd()
}

function resolveWorkingDirectory(request: RuntimeRequest, options?: { workingDirectory?: string; homeDirectory?: string }): string {
  return request.working_dir
    ?? options?.workingDirectory
    ?? options?.homeDirectory
    ?? process.env.AGENT_HOME_DIR
    ?? process.cwd()
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
          env: {
            ...process.env,
            ...(options.env ?? {}),
          },
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

function invalidAlfredDirectResult(intent: AlfredDirectIntent, output: string): string | undefined {
  const trimmed = output.trim()
  if (!trimmed) {
    return `${intent.kind} completed without returning a concrete result`
  }
  const normalized = trimmed.toLowerCase()
  if (normalized === 'what can i help you with today?') {
    return `${intent.kind} returned generic assistant text instead of executing the operation`
  }
  if (intent.kind === 'get_secret' && ['stored', 'validated', 'no change'].includes(normalized)) {
    return 'get_secret returned a write-style confirmation instead of the requested value'
  }
  if (intent.kind === 'store_secret' && trimmed === intent.value) {
    return 'store_secret echoed the secret value instead of returning a confirmation'
  }
  return undefined
}

export function enforceAlfredDirectIntentContract(request: RuntimeRequest, result: RuntimeResult): RuntimeResult {
  if (!isAlfredRuntimeContext() || result.status !== 'success') return result
  const intent = classifyAlfredDirectIntent(resolveOriginalPrompt(request))
  if (!intent) return result
  const violation = invalidAlfredDirectResult(intent, result.output)
  if (!violation) return result
  log('alfred_contract_violation', {
    intent: intent.kind,
    key_path: intent.keyPath,
    violation,
    output: summarizeText(result.output, 400) || null,
  })
  return {
    status: 'error',
    output: violation,
    errors: [violation],
  }
}

async function callOpenAiChatCompletion(options: {
  model: string
  apiKey?: string
  baseUrl?: string
  messages: Array<Record<string, unknown>>
  tools?: Array<Record<string, unknown>>
  timeoutMs?: number
}): Promise<Record<string, unknown>> {
  if (!options.apiKey) {
    throw new Error('BACKEND_API_KEY is not configured for simple harness runtime')
  }
  const baseUrl = (options.baseUrl ?? 'https://api.openai.com/v1').replace(/\/$/, '')
  const controller = new AbortController()
  const timeoutHandle = options.timeoutMs
    ? setTimeout(() => controller.abort(), options.timeoutMs)
    : undefined
  try {
    const response = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: `Bearer ${options.apiKey}`,
      },
      body: JSON.stringify({
        model: options.model,
        messages: options.messages,
        tools: options.tools,
        tool_choice: options.tools && options.tools.length > 0 ? 'auto' : undefined,
        temperature: 0,
      }),
      signal: controller.signal,
    })
    const json = await response.json() as Record<string, unknown>
    if (!response.ok) {
      throw new Error(summarizeUnknown(json, 1600) ?? `chat completion failed with status ${response.status}`)
    }
    return json
  } finally {
    if (timeoutHandle) clearTimeout(timeoutHandle)
  }
}

function simpleHarnessTools(): Array<Record<string, unknown>> {
  return [
    {
      type: 'function',
      function: {
        name: 'read_file',
        description: 'Read the contents of a UTF-8 text file',
        parameters: {
          type: 'object',
          properties: { path: { type: 'string' } },
          required: ['path'],
          additionalProperties: false,
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'write_file',
        description: 'Write UTF-8 text to a file path',
        parameters: {
          type: 'object',
          properties: {
            path: { type: 'string' },
            content: { type: 'string' },
          },
          required: ['path', 'content'],
          additionalProperties: false,
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'list_dir',
        description: 'List files and directories for one path',
        parameters: {
          type: 'object',
          properties: { path: { type: 'string' } },
          required: ['path'],
          additionalProperties: false,
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'pass_show',
        description: 'Read a secret from the shared pass store',
        parameters: {
          type: 'object',
          properties: { key_path: { type: 'string' } },
          required: ['key_path'],
          additionalProperties: false,
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'pass_insert',
        description: 'Store a secret in the shared pass store and overwrite if it already exists',
        parameters: {
          type: 'object',
          properties: {
            key_path: { type: 'string' },
            value: { type: 'string' },
          },
          required: ['key_path', 'value'],
          additionalProperties: false,
        },
      },
    },
  ]
}

async function executeSimpleHarnessToolCall(call: SimpleHarnessToolCall, cwd: string): Promise<string> {
  switch (call.name) {
    case 'read_file': {
      const target = String(call.arguments.path ?? '')
      return await readFile(path.isAbsolute(target) ? target : path.join(cwd, target), 'utf8')
    }
    case 'write_file': {
      const target = String(call.arguments.path ?? '')
      const content = String(call.arguments.content ?? '')
      const absolute = path.isAbsolute(target) ? target : path.join(cwd, target)
      await mkdir(path.dirname(absolute), { recursive: true })
      await writeFile(absolute, content, 'utf8')
      return 'written'
    }
    case 'list_dir': {
      const target = String(call.arguments.path ?? '')
      const absolute = path.isAbsolute(target) ? target : path.join(cwd, target)
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
    }
    case 'pass_show':
      return await passShow(String(call.arguments.key_path ?? ''), cwd)
    case 'pass_insert':
      await passInsert(String(call.arguments.key_path ?? ''), String(call.arguments.value ?? ''), cwd)
      return 'stored'
  }
}

async function runDirectIntent(
  request: RuntimeRequest,
  options: { sessionId: string; homeDirectory?: string; workingDirectory?: string }
): Promise<{ output: string; structuredLogPath: string; structuredLogTail: string }> {
  const runtimeHome = resolveRuntimeHome(options.homeDirectory)
  const debugDir = path.join(runtimeHome, '.daemon-logs')
  await mkdir(debugDir, { recursive: true })
  const structuredLogPath = path.join(debugDir, `simple-harness-${options.sessionId}-${Date.now()}-stream.jsonl`)
  const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
  const writeEvent = async (event: Record<string, unknown>) => {
    structuredLogStream.write(`${JSON.stringify(event)}\n`)
    await reportProgress(request.progress, {
      source: 'provider',
      kind: typeof event.type === 'string' ? event.type : 'unknown',
      runtime: 'simple-harness',
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: event,
    })
  }

  const originalPrompt = resolveOriginalPrompt(request)
  const intent = classifyAlfredDirectIntent(originalPrompt)
  const cwd = resolveWorkingDirectory(request, options)
  if (!intent) {
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    throw new Error('unsupported direct Alfred intent')
  }

  try {
    await reportProgress(request.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.start',
      runtime: 'simple-harness',
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { cwd, intent: intent.kind },
    })
    await writeEvent({
      type: 'system',
      subtype: 'init',
      runtime: 'simple-harness',
      cwd,
      session_id: options.sessionId,
      intent: intent.kind,
    })

    if (intent.kind === 'get_secret') {
      await writeEvent({
        type: 'assistant',
        message: {
          role: 'assistant',
          content: [{ type: 'tool_use', name: 'pass_show', input: { key_path: intent.keyPath } }],
        },
      })
      const output = await passShow(intent.keyPath, cwd)
      await writeEvent({
        type: 'user',
        message: {
          role: 'user',
          content: [{ type: 'tool_result', tool_name: 'pass_show', key_path: intent.keyPath, output }],
        },
      })
      await writeEvent({ type: 'result', subtype: 'success', result: output })
      await reportProgress(request.progress, {
        source: 'agent-daemon',
        kind: 'runtime.stream.complete',
        runtime: 'simple-harness',
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
        payload: { result_preview: summarizeText(output, 200) },
      })
      await new Promise<void>(resolve => structuredLogStream.end(resolve))
      const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
      return { output, structuredLogPath, structuredLogTail }
    }

    await writeEvent({
      type: 'assistant',
      message: {
        role: 'assistant',
        content: [{ type: 'tool_use', name: 'pass_insert', input: { key_path: intent.keyPath } }],
      },
    })
    await passInsert(intent.keyPath, intent.value, cwd)
    await writeEvent({
      type: 'user',
      message: {
        role: 'user',
        content: [{ type: 'tool_result', tool_name: 'pass_insert', key_path: intent.keyPath, output: 'stored' }],
      },
    })
    const verified = await passShow(intent.keyPath, cwd)
    await writeEvent({
      type: 'assistant',
      message: {
        role: 'assistant',
        content: [{ type: 'tool_use', name: 'pass_show', input: { key_path: intent.keyPath } }],
      },
    })
    await writeEvent({
      type: 'user',
      message: {
        role: 'user',
        content: [{ type: 'tool_result', tool_name: 'pass_show', key_path: intent.keyPath, output: verified }],
      },
    })
    await writeEvent({ type: 'result', subtype: 'success', result: 'stored' })
    await reportProgress(request.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.complete',
      runtime: 'simple-harness',
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { result_preview: 'stored' },
    })
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
    return { output: 'stored', structuredLogPath, structuredLogTail }
  } catch (error) {
    await writeEvent({
      type: 'result',
      subtype: 'error',
      error: error instanceof Error ? error.message : String(error),
    })
    await reportProgress(request.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.error',
      runtime: 'simple-harness',
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { error: error instanceof Error ? error.message : String(error) },
    })
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    let structuredLogTail = ''
    try {
      structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
    } catch {
      // ignore
    }
    throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
      structuredLogPath,
      structuredLogTail,
    })
  }
}

async function runToolLoop(
  request: RuntimeRequest,
  options: { model: string; apiKey?: string; baseUrl?: string; sessionId: string; homeDirectory?: string; workingDirectory?: string }
): Promise<{ output: string; structuredLogPath: string; structuredLogTail: string }> {
  const runtimeHome = resolveRuntimeHome(options.homeDirectory)
  const debugDir = path.join(runtimeHome, '.daemon-logs')
  await mkdir(debugDir, { recursive: true })
  const structuredLogPath = path.join(debugDir, `simple-harness-${options.sessionId}-${Date.now()}-stream.jsonl`)
  const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' })
  const writeEvent = async (event: Record<string, unknown>) => {
    structuredLogStream.write(`${JSON.stringify(event)}\n`)
    await reportProgress(request.progress, {
      source: 'provider',
      kind: typeof event.type === 'string' ? event.type : 'unknown',
      runtime: 'simple-harness',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: event,
    })
  }
  const cwd = resolveWorkingDirectory(request, options)
  const messages: Array<Record<string, unknown>> = [
    {
      role: 'system',
      content: 'You are a constrained operator. Use the provided tools to read files, write files, and read or store secrets through pass. Respond tersely and only after performing the necessary action.',
    },
    {
      role: 'user',
      content: request.prompt,
    },
  ]
  const tools = simpleHarnessTools()

  try {
    await reportProgress(request.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.start',
      runtime: 'simple-harness',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { cwd },
    })
    await writeEvent({ type: 'system', subtype: 'init', runtime: 'simple-harness', cwd, session_id: options.sessionId, model: options.model })
    for (let step = 0; step < 8; step += 1) {
      const response = await callOpenAiChatCompletion({
        model: options.model,
        apiKey: options.apiKey,
        baseUrl: options.baseUrl,
        messages,
        tools,
        timeoutMs: request.timeout_ms,
      })
      await writeEvent({ type: 'assistant', message: response })
      const choice = Array.isArray(response.choices) ? response.choices[0] as Record<string, unknown> | undefined : undefined
      const message = choice && typeof choice === 'object' ? choice.message as Record<string, unknown> | undefined : undefined
      const toolCalls = Array.isArray(message?.tool_calls) ? message.tool_calls as Array<Record<string, unknown>> : []
      if (toolCalls.length === 0) {
        const content = typeof message?.content === 'string'
          ? message.content
          : Array.isArray(message?.content)
            ? message.content.map(item => typeof item === 'string' ? item : summarizeUnknown(item, 400) ?? '').join('\n').trim()
            : ''
        await writeEvent({ type: 'result', subtype: 'success', result: content })
        await reportProgress(request.progress, {
          source: 'agent-daemon',
          kind: 'runtime.stream.complete',
          runtime: 'simple-harness',
          model: options.model,
          session_id: options.sessionId,
          structured_log_path: structuredLogPath,
          payload: { result_preview: summarizeText(content, 200) },
        })
        await new Promise<void>(resolve => structuredLogStream.end(resolve))
        const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
        return { output: content.trim(), structuredLogPath, structuredLogTail }
      }

      messages.push({
        role: 'assistant',
        content: message?.content ?? '',
        tool_calls: toolCalls,
      })

      for (const toolCallRaw of toolCalls) {
        const fn = toolCallRaw.function as Record<string, unknown> | undefined
        const name = String(fn?.name ?? '') as SimpleHarnessToolName
        const id = String(toolCallRaw.id ?? randomUUID())
        let args: Record<string, unknown> = {}
        try {
          args = JSON.parse(String(fn?.arguments ?? '{}')) as Record<string, unknown>
        } catch {
          args = {}
        }
        await writeEvent({ type: 'tool_use', id, name, arguments: args })
        const output = await executeSimpleHarnessToolCall({ id, name, arguments: args }, cwd)
        await writeEvent({ type: 'tool_result', id, name, output: summarizeText(output, 1200) })
        messages.push({
          role: 'tool',
          tool_call_id: id,
          content: output,
        })
      }
    }
    throw new Error('simple harness exceeded maximum steps')
  } catch (error) {
    await writeEvent({ type: 'result', subtype: 'error', error: error instanceof Error ? error.message : String(error) })
    await reportProgress(request.progress, {
      source: 'agent-daemon',
      kind: 'runtime.stream.error',
      runtime: 'simple-harness',
      model: options.model,
      session_id: options.sessionId,
      structured_log_path: structuredLogPath,
      payload: { error: error instanceof Error ? error.message : String(error) },
    })
    await new Promise<void>(resolve => structuredLogStream.end(resolve))
    let structuredLogTail = ''
    try {
      structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000)
    } catch {
      // ignore
    }
    throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
      structuredLogPath,
      structuredLogTail,
    })
  }
}

async function maybeReflectWithSimpleHarness(
  taskOutput: string,
  options: { model: string; apiKey?: string; baseUrl?: string },
  reflectionPrompt?: string,
): Promise<{ reflection?: ReflectionPayload; errors?: string[] }> {
  try {
    const response = await callOpenAiChatCompletion({
      model: options.model,
      apiKey: options.apiKey,
      baseUrl: options.baseUrl,
      messages: [
        { role: 'system', content: 'Return strict JSON only.' },
        { role: 'user', content: buildDefaultReflectionPrompt(taskOutput, reflectionPrompt) },
      ],
      timeoutMs: 15000,
    })
    const choice = Array.isArray(response.choices) ? response.choices[0] as Record<string, unknown> | undefined : undefined
    const message = choice && typeof choice === 'object' ? choice.message as Record<string, unknown> | undefined : undefined
    const text = typeof message?.content === 'string' ? message.content : ''
    const reflection = parseReflectionPayload(text)
    if (!reflection) return { errors: ['Failed to parse reflection payload'] }
    return { reflection }
  } catch (error) {
    return { errors: [error instanceof Error ? error.message : String(error)] }
  }
}

export class SimpleHarnessAdapter implements ProviderSessionAdapter {
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
    return nextSessionState(session, session.providerSessionId ?? randomUUID())
  }

  async executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }> {
    const sessionId = session.providerSessionId ?? randomUUID()
    const nextSession = nextSessionState(session, sessionId)
    const originalPrompt = resolveOriginalPrompt(request)

    try {
      const execution = classifyAlfredDirectIntent(originalPrompt)
        ? await runDirectIntent({ ...request, raw_prompt: originalPrompt }, {
            sessionId,
            homeDirectory: this.homeDirectory,
            workingDirectory: this.workingDirectory,
          })
        : await runToolLoop(request, {
            model: this.model,
            apiKey: this.apiKey,
            baseUrl: this.baseUrl,
            sessionId,
            homeDirectory: this.homeDirectory,
            workingDirectory: this.workingDirectory,
          })

      const baseResult = enforceAlfredDirectIntentContract({ ...request, raw_prompt: originalPrompt }, successResult(execution.output))
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithSimpleHarness(baseResult.output, {
        model: this.model,
        apiKey: this.apiKey,
        baseUrl: this.baseUrl,
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
    // No-op for simple harness.
  }
}
