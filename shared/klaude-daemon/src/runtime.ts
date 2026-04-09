import { randomUUID } from 'node:crypto'
import { spawn, spawnSync } from 'node:child_process'
import Anthropic from '@anthropic-ai/sdk'
import { query } from '@anthropic-ai/claude-agent-sdk'
import { Codex } from '@openai/codex-sdk'
import type { ExecutionProfile } from './config.js'
import type { ProviderSessionAdapter, ReflectionPayload, RuntimeRequest, RuntimeResult, SessionState } from './types.js'

const OPENCLAUDE_NPM_PACKAGE = process.env.OPENCLAUDE_NPM_PACKAGE ?? '@gitlawb/openclaude'
const OPENCLAUDE_BIN = process.env.OPENCLAUDE_BIN ?? 'openclaude'

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

function successResult(output: string): RuntimeResult {
  return {
    status: 'success',
    output,
  }
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

function shouldSkipPermissionsFlag(): boolean {
  return typeof process.getuid !== 'function' || process.getuid() !== 0
}

async function runOpenClaudePrint(prompt: string, options: { model: string; sessionId: string; baseUrl?: string; apiKey?: string; workingDirectory?: string }): Promise<string> {
  const env: Record<string, string> = {}
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined) env[key] = value
  }
  if (options.baseUrl) env.OPENAI_BASE_URL = options.baseUrl
  if (options.apiKey) env.OPENAI_API_KEY = options.apiKey
  env.OPENAI_MODEL = options.model
  env.CLAUDE_CODE_USE_OPENAI = '1'

  const args = ['--print']
  if (shouldSkipPermissionsFlag()) {
    args.push('--dangerously-skip-permissions')
  }
  args.push(
    '--no-session-persistence',
    '--session-id', options.sessionId,
    '--model', options.model,
    prompt,
  )
  const command = ensureOpenClaudeCommand()

  return await new Promise<string>((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.workingDirectory ?? process.cwd(),
      env,
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    let stdout = ''
    let stderr = ''
    child.stdout.on('data', chunk => { stdout += chunk.toString() })
    child.stderr.on('data', chunk => { stderr += chunk.toString() })
    child.on('error', reject)
    child.on('close', code => {
      if (code !== 0) {
        reject(new Error(stderr.trim() || `openclaude exited with code ${code}`))
        return
      }
      resolve(stdout.trim())
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

export class ClaudeSdkAdapter implements ProviderSessionAdapter {
  private readonly model: string
  private readonly apiKey?: string

  constructor(model: string, apiKey?: string) {
    this.model = model
    this.apiKey = apiKey
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
      let text = ''
      let nextSessionId = sessionId
      const q = query({
        prompt: request.prompt,
        options: {
          cwd: process.cwd(),
          resume: session.providerSessionId,
          model: this.model,
          permissionMode: 'bypassPermissions',
          env,
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

      const baseResult = successResult(text.trim())
      const nextSession = nextSessionState(session, nextSessionId)
      if (!shouldReflect(request)) {
        return { session: nextSession, result: baseResult }
      }

      const reflectionResult = await maybeReflectWithClaudeAgentSdk(this.model, nextSession, baseResult.output, request.reflection_prompt)
      return {
        session: reflectionResult.session,
        result: finalizeRuntimeResult(baseResult, reflectionResult),
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      return { session: nextSessionState(session, sessionId), result: errorResult(message) }
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

      const runResult = await thread.run(request.prompt)
      const output = typeof runResult === 'string'
        ? runResult
        : runResult.finalResponse?.trim() || JSON.stringify(runResult)

      const nextSession = nextSessionState(session, thread.id ?? session.providerSessionId)
      const baseResult = successResult(output)

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
      const message = error instanceof Error ? error.message : String(error)
      return { session, result: errorResult(message) }
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
      })

      const baseResult = successResult(output)
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
      const message = error instanceof Error ? error.message : String(error)
      return { session: nextSession, result: errorResult(message) }
    }
  }

  async interruptActiveExecution(_session: SessionState): Promise<void> {
    // Harness interruption wiring can be added later.
  }
}

export function createProviderAdapter(executionProfile: ExecutionProfile): ProviderSessionAdapter {
  if (executionProfile.runtime === 'claude-sdk') {
    return new ClaudeSdkAdapter(executionProfile.model, executionProfile.apiKey)
  }
  if (executionProfile.runtime === 'openclaude-harness') {
    return new OpenClaudeHarnessAdapter(executionProfile.model, {
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
