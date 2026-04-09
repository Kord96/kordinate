export type ProviderName = string
export type RuntimeKind = 'codex-sdk' | 'claude-sdk' | 'openclaude-harness'

export interface ExecutionProfile {
  provider: ProviderName
  runtime: RuntimeKind
  model: string
  apiKey?: string
  baseUrl?: string
  skipGitRepoCheck?: boolean
  workingDirectory?: string
}

export interface DaemonConfig {
  executionProfile: ExecutionProfile
  kafkaBrokers: string[]
  reflectionsTopic: string
  discoveryServerUrl?: string
  discoveryPublishIntervalMs: number
  healthUrl?: string
  stateDir: string
  sessionMapPath: string
}

function resolveDefaultRuntime(provider?: string): RuntimeKind {
  if (provider === 'anthropic' || provider === 'claude') {
    return 'claude-sdk'
  }
  return 'codex-sdk'
}

function buildClaudeExecutionProfile(provider: ProviderName): ExecutionProfile {
  return {
    provider,
    runtime: 'claude-sdk',
    model: process.env.DAEMON_MODEL ?? 'claude-sonnet-4-5',
    apiKey: process.env.BACKEND_API_KEY ?? process.env.ANTHROPIC_API_KEY,
    baseUrl: process.env.BACKEND_BASE_URL,
  }
}

function buildOpenClaudeExecutionProfile(provider: ProviderName): ExecutionProfile {
  const genericApiKey = process.env.BACKEND_API_KEY
  const genericBaseUrl = process.env.BACKEND_BASE_URL

  if (provider === 'deepseek') {
    return {
      provider,
      runtime: 'openclaude-harness',
      model: process.env.DAEMON_MODEL ?? 'deepseek-chat',
      apiKey: genericApiKey ?? process.env.DEEPSEEK_API_KEY,
      baseUrl: genericBaseUrl ?? 'https://api.deepseek.com/v1',
      workingDirectory: process.env.CODEX_WORKING_DIRECTORY,
    }
  }

  return {
    provider,
    runtime: 'openclaude-harness',
    model: process.env.DAEMON_MODEL ?? 'gpt-5.4',
    apiKey: genericApiKey ?? process.env.OPENAI_API_KEY,
    baseUrl: genericBaseUrl,
    workingDirectory: process.env.CODEX_WORKING_DIRECTORY,
  }
}

function buildCodexExecutionProfile(provider: ProviderName): ExecutionProfile {
  const genericApiKey = process.env.BACKEND_API_KEY
  const genericBaseUrl = process.env.BACKEND_BASE_URL

  if (provider === 'deepseek') {
    return {
      provider,
      runtime: 'codex-sdk',
      model: process.env.DAEMON_MODEL ?? 'deepseek-chat',
      apiKey: genericApiKey ?? process.env.DEEPSEEK_API_KEY,
      baseUrl: genericBaseUrl ?? 'https://api.deepseek.com/v1',
      skipGitRepoCheck: process.env.CODEX_SKIP_GIT_REPO_CHECK === '1' || process.env.CODEX_SKIP_GIT_REPO_CHECK === 'true',
      workingDirectory: process.env.CODEX_WORKING_DIRECTORY,
    }
  }

  return {
    provider,
    runtime: 'codex-sdk',
    model: process.env.DAEMON_MODEL ?? 'gpt-5.4',
    apiKey: genericApiKey ?? process.env.OPENAI_API_KEY,
    baseUrl: genericBaseUrl,
    skipGitRepoCheck: process.env.CODEX_SKIP_GIT_REPO_CHECK === '1' || process.env.CODEX_SKIP_GIT_REPO_CHECK === 'true',
    workingDirectory: process.env.CODEX_WORKING_DIRECTORY,
  }
}

export function loadDaemonConfig(): DaemonConfig {
  const stateDir = process.env.DAEMON_STATE_DIR ?? '.daemon-state'
  const provider = process.env.DAEMON_PROVIDER ?? 'openai'
  const runtime = (process.env.DAEMON_RUNTIME as RuntimeKind | undefined) ?? resolveDefaultRuntime(provider)

  const executionProfile = runtime === 'claude-sdk'
    ? buildClaudeExecutionProfile(provider)
    : runtime === 'openclaude-harness'
      ? buildOpenClaudeExecutionProfile(provider)
      : buildCodexExecutionProfile(provider)

  return {
    executionProfile,
    kafkaBrokers: (process.env.KAFKA_BROKERS ?? 'localhost:9092').split(','),
    reflectionsTopic: process.env.REFLECTIONS_TOPIC ?? 'reflections',
    discoveryServerUrl: process.env.DISCOVERY_SERVER_URL,
    discoveryPublishIntervalMs: Number.parseInt(process.env.DISCOVERY_PUBLISH_INTERVAL_MS ?? '30000', 10),
    healthUrl: process.env.DAEMON_HEALTH_URL,
    stateDir,
    sessionMapPath: process.env.DAEMON_SESSION_MAP_PATH ?? `${stateDir}/sessions.json`,
  }
}
