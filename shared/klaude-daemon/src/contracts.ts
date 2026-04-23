import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { AgentContract, PromptPlan, RequestMessage, RuntimeProfile } from './types.js'

const DEFAULT_REFLECTION_PROMPT = [
  'Based on the completed task, return strict JSON only with exactly these keys:',
  '{"project":"...","general":"..."}',
  'project: lessons specific to the current project/repo/context.',
  'general: lessons that transfer to any project.',
  'Use strings only. If there is no strong lesson for a key, return an empty string.',
].join('\n')

const moduleDir = dirname(fileURLToPath(import.meta.url))
const bundleTextCache = new Map<string, string>()

type BundleLayer = {
  label: string
  dir: string
  selection?: string
}

type AugurPromptContext = {
  bundle_prefix?: string
  mode_guide?: string
}

function parseJsonEnv<T>(name: string): T {
  const raw = process.env[name]
  if (!raw || !raw.trim()) {
    throw new Error(`${name} required`)
  }
  return JSON.parse(raw) as T
}

function readCached(path: string): string | undefined {
  if (bundleTextCache.has(path)) return bundleTextCache.get(path)
  if (!existsSync(path)) return undefined
  const text = readFileSync(path, 'utf8')
  bundleTextCache.set(path, text)
  return text
}

function agentRootCandidates(agentName: string): string[] {
  const candidates = [
    process.env.AUGUR_HOME,
    process.env.AGENT_HOME_DIR && agentName === 'augur' ? join(process.env.AGENT_HOME_DIR, '.augur', 'current') : undefined,
    join('/app/agents', agentName),
    join(moduleDir, '..', '..', '..', 'agents', agentName),
  ]
  return candidates.filter((value): value is string => typeof value === 'string' && value.length > 0)
}

function resolveRepoBundleFile(agentName: string, dir: string, selection?: string): string | undefined {
  if (!selection) return undefined
  const exts = ['', '.md', '.json', '.yaml', '.yml']
  for (const root of agentRootCandidates(agentName)) {
    const bundleDirs = [join(root, '.generated', 'bundles', dir), join(root, 'bundles', dir)]
    for (const bundleDir of bundleDirs) {
      if (!existsSync(bundleDir)) continue
      for (const ext of exts) {
        const candidate = join(bundleDir, `${selection}${ext}`)
        if (existsSync(candidate)) return candidate
      }
    }
  }
  return undefined
}

function applyBundleModeSelection(selection: string | undefined, bundleMode: 'selective' | 'holistic', dir: string): string | undefined {
  if (!selection) return selection
  if (dir !== 'memory' && dir !== 'runtime') return selection
  return selection
    .replace('analyze-selective-', `analyze-${bundleMode}-`)
    .replace('analyze-holistic-', `analyze-${bundleMode}-`)
}

function loadRepoBundlePrefix(contract: AgentContract, bundleMode: 'selective' | 'holistic'): string {
  const layers: BundleLayer[] = [
    { label: 'Skill Bundle', dir: 'skill', selection: contract.bundleRefs?.skill },
    { label: 'Memory Bundle', dir: 'memory', selection: applyBundleModeSelection(contract.bundleRefs?.memory, bundleMode, 'memory') },
    { label: 'Runtime Bundle', dir: 'runtime', selection: applyBundleModeSelection(contract.bundleRefs?.runtime, bundleMode, 'runtime') },
  ]
  const parts = layers.flatMap(layer => {
    const path = resolveRepoBundleFile(contract.specialization, layer.dir, layer.selection)
    const text = path ? readCached(path)?.trim() : undefined
    return text ? [`## ${layer.label}\n\n${text}`] : []
  })
  return parts.length > 0 ? `${parts.join('\n\n')}\n\n` : ''
}

function resolveBundleMode(message: RequestMessage): 'selective' | 'holistic' {
  const analysisMode = typeof message.agent_params?.analysis_mode === 'string'
    ? message.agent_params.analysis_mode.trim().toLowerCase()
    : ''
  const raw = String(message.agent_params?.bundle_mode ?? 'auto').toLowerCase()
  if (
    raw.includes('holistic')
    || raw.includes('full-bundle')
    || raw === 'full'
    || raw === 'opus-full'
  ) {
    return 'holistic'
  }
  if (raw && raw !== 'auto' && raw !== 'default') {
    return 'selective'
  }
  if (analysisMode === 'incremental') {
    return 'selective'
  }
  if (analysisMode === 'full') {
    return 'holistic'
  }
  return 'selective'
}

function loadPromptContext(contract: AgentContract, message: RequestMessage): AugurPromptContext | undefined {
  const scriptPath = contract.workflow?.promptContextScript
  if (!scriptPath) return undefined
  const mode = typeof message.agent_params?.analysis_mode === 'string'
    ? message.agent_params.analysis_mode.trim()
    : ''
  try {
    const payload = execFileSync('python3', [
      scriptPath,
      '--bundle-mode', resolveBundleMode(message),
      '--analysis-mode', mode,
    ], {
      encoding: 'utf8',
    }).trim()
    return JSON.parse(payload) as AugurPromptContext
  } catch {
    return undefined
  }
}

function renderStartupGuidance(agentParams?: Record<string, unknown>): string {
  const guidance = agentParams?.startup_guidance
  if (!guidance || typeof guidance !== 'object' || Array.isArray(guidance)) return ''
  const guidanceRecord = guidance as Record<string, unknown>

  const directive = typeof guidanceRecord.directive === 'string' ? guidanceRecord.directive.trim() : ''
  const starterFiles = Array.isArray(guidanceRecord.starter_files)
    ? guidanceRecord.starter_files.filter((value: unknown): value is string => typeof value === 'string' && value.trim().length > 0)
    : []

  const parts: string[] = []
  if (directive) parts.push(`Directive: ${directive}`)
  if (starterFiles.length > 0) {
    parts.push('Starter artifacts:')
    parts.push(...starterFiles.map(path => `- \`${path}\``))
  }
  return parts.length > 0 ? `## Startup Guidance\n\n${parts.join('\n')}\n\n` : ''
}

function renderRuntimeContext(agentContract: AgentContract, message: RequestMessage, runtimeProfile: RuntimeProfile): string {
  const workspace = message.workspace
  const resources = message.resources
  const requestedBundleMode = typeof message.agent_params?.bundle_mode === 'string'
    ? resolveBundleMode(message)
    : undefined
  const toolGuidance = runtimeProfile.toolGuidance ?? []
  const runArtifactGuidance = runtimeProfile.runArtifactGuidance ?? []
  if (workspace && typeof workspace.working_dir === 'string' && typeof workspace.output_dir === 'string') {
    const lines: string[] = []
    lines.push(`- Working directory: \`${workspace.working_dir}\``)
    lines.push(`- Output directory: \`${workspace.output_dir}\``)
    if (typeof workspace.agent_root === 'string' && workspace.agent_root.trim()) {
      lines.push(`- Agent root: \`${workspace.agent_root.trim()}\``)
    }
    if (typeof resources?.concept_catalog_index === 'string' && resources.concept_catalog_index.trim()) {
      lines.push(`- Concept catalog entrypoint: \`${resources.concept_catalog_index.trim()}\``)
    }
    if (typeof resources?.framework_catalog_index === 'string' && resources.framework_catalog_index.trim()) {
      lines.push(`- Framework catalog entrypoint: \`${resources.framework_catalog_index.trim()}\``)
    }
    if (requestedBundleMode) {
      lines.push(`- Bundle mode: \`${requestedBundleMode}\``)
    }
    lines.push('- Start in the working directory and treat it as the authoritative repo root for analysis and edits.')
    lines.push('- Generated artifacts belong in the output directory.')
    lines.push('- Use the provided validator path and catalog entrypoints directly instead of discovering alternate internal paths.')
    lines.push('- Use the prepared run artifacts under the output directory for startup orientation before broad repo reading.')
    lines.push('- Treat `startup.json` and `index.json` under the output directory as the authoritative manifests for prepared deterministic and derived analysis inputs in this run.')
    lines.push('- Use the agent root as the stable base for agent-owned resources and the provided catalog entrypoints for on-demand concept/framework reads.')
    lines.push('- Use deterministic artifacts for startup orientation first, then move into repo code for the main architectural synthesis.')
    lines.push('- Revisit larger supporting fact domains only when they help resolve ambiguity, answer semantic questions, or confirm concepts.')
    lines.push('- Read repo code through fact-selected files, architecture entrypoints, adjacent implementation, or concrete validation gaps.')
    lines.push('- Do not begin with repo-root listings or metadata-file discovery.')
    lines.push('- Follow the runtime-harness tool schema directly instead of assuming specific tool names from prior runs or other runtimes.')
    for (const guidance of toolGuidance) {
      lines.push(`- ${guidance}`)
    }
    for (const guidance of runArtifactGuidance) {
      lines.push(`- ${guidance}`)
    }
    return `## Runtime Context\n${lines.join('\n')}\n\n`
  }

  const runtimeHints: string[] = []
  if (message.working_dir) {
    runtimeHints.push(`Working directory hint: use \`${message.working_dir}\` as the authoritative starting project root and current working directory.`)
  }
  const runDir = typeof message.agent_params?.run_dir === 'string' && message.agent_params.run_dir.trim()
    ? message.agent_params.run_dir.trim()
    : ''
  if (runDir) {
    runtimeHints.push(`Prepared analysis run: use \`${runDir}\` as the authoritative output directory for this request.`)
    runtimeHints.push(`Start with \`${runDir}/blast.json\`, \`${runDir}/startup.json\`, and \`${runDir}/index.json\` for prepared run artifacts.`)
  }
  if (requestedBundleMode) {
    runtimeHints.push(`Bundle mode hint: use \`${requestedBundleMode}\` prompt preload assumptions for this request.`)
  }
  runtimeHints.push(...toolGuidance)
  runtimeHints.push(...runArtifactGuidance)
  return runtimeHints.length > 0
    ? `## Runtime Context\n${runtimeHints.map(line => `- ${line}`).join('\n')}\n\n`
    : ''
}

function hashPromptPrefix(value: string): string {
  return createHash('sha256').update(value).digest('hex')
}

export function loadInjectedAgentContract(expectedAgentName: string): AgentContract {
  const contract = parseJsonEnv<AgentContract>('AGENT_CONTRACT_JSON')
  if (contract.name !== expectedAgentName) {
    throw new Error(`AGENT_CONTRACT_JSON name mismatch: expected ${expectedAgentName}, got ${contract.name}`)
  }
  return contract
}

export function loadInjectedRuntimeProfile(): RuntimeProfile {
  return parseJsonEnv<RuntimeProfile>('RUNTIME_PROFILE_JSON')
}

export function buildPromptPlan(agentContract: AgentContract, runtimeProfile: RuntimeProfile, message: RequestMessage): PromptPlan {
  const runtimePreamble = runtimeProfile.promptPreamble?.trim()
    ? `${runtimeProfile.promptPreamble.trim()}\n\n`
    : ''
  const runtimeContext = renderRuntimeContext(agentContract, message, runtimeProfile)
  const startupGuidance = renderStartupGuidance(message.agent_params)
  const resolvedBundleMode = resolveBundleMode(message)
  const promptContext = loadPromptContext(agentContract, message)
  const bundlePrefix = promptContext?.bundle_prefix ?? loadRepoBundlePrefix(agentContract, resolvedBundleMode)
  const modeGuide = promptContext?.mode_guide ?? ''
  const cacheablePrefix = agentContract.promptPrefix || bundlePrefix
    ? `${agentContract.promptPrefix ? `${agentContract.promptPrefix}\n\n` : ''}${bundlePrefix}`
    : ''
  const dynamicPrompt = `${runtimePreamble}${runtimeContext}${startupGuidance}${modeGuide}${message.prompt}`
  const fullPrompt = cacheablePrefix
    ? `${cacheablePrefix}${dynamicPrompt}`
    : dynamicPrompt

  return {
    fullPrompt,
    dynamicPrompt,
    cacheablePrefix: cacheablePrefix || undefined,
    cacheKey: cacheablePrefix ? hashPromptPrefix(cacheablePrefix) : undefined,
    cacheStrategy: cacheablePrefix ? 'provider' : undefined,
  }
}

export function buildPrompt(agentContract: AgentContract, runtimeProfile: RuntimeProfile, message: RequestMessage): string {
  return buildPromptPlan(agentContract, runtimeProfile, message).fullPrompt
}

export function resolveReflectionPrompt(agentContract: AgentContract, message: RequestMessage): string {
  return message.reflection_prompt ?? agentContract.defaultReflectionPrompt ?? DEFAULT_REFLECTION_PROMPT
}
