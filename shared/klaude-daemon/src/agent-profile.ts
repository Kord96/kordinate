import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { AgentProfile, PromptPlan, RequestMessage } from './types.js'
import { loadIdentityMetadata } from './identity.js'

const DEFAULT_REFLECTION_PROMPT = [
  'Based on the completed task, return strict JSON only with exactly these keys:',
  '{"project":"...","general":"..."}',
  'project: lessons specific to the current project/repo/context.',
  'general: lessons that transfer to any project.',
  'Use strings only. If there is no strong lesson for a key, return an empty string.',
].join('\n')

const moduleDir = dirname(fileURLToPath(import.meta.url))
const bundleTextCache = new Map<string, string>()

interface RuntimeBundleManifest {
  skill_bundle?: string
  memory_bundle?: string
  detector_plan?: string
  composition_order?: string[]
}

interface RepoBundleLayer {
  label: string
  dir: string
  selection?: string
}

function readCached(path: string): string | undefined {
  if (bundleTextCache.has(path)) return bundleTextCache.get(path)
  if (!existsSync(path)) return undefined
  const text = readFileSync(path, 'utf8')
  bundleTextCache.set(path, text)
  return text
}

function agentRootCandidates(agentName: string): string[] {
  return [
    join('/app/agents', agentName),
    join(moduleDir, '..', '..', '..', 'agents', agentName),
  ]
}

function resolveRepoBundleFile(agentName: string, dir: string, selection?: string): string | undefined {
  const exts = ['', '.md', '.json', '.yaml', '.yml']
  for (const root of agentRootCandidates(agentName)) {
    const bundleDirs = [join(root, '.generated', 'bundles', dir), join(root, 'bundles', dir)]
    for (const bundleDir of bundleDirs) {
      if (!existsSync(bundleDir)) continue
      if (selection) {
        for (const ext of exts) {
          const candidate = join(bundleDir, `${selection}${ext}`)
          if (existsSync(candidate)) return candidate
        }
        continue
      }
      const defaults = ['default-v1.md', 'default-v1.json', 'default-v1.yaml', 'default-v1.yml', 'core-v1.md', 'core-v1.json']
      for (const candidateName of defaults) {
        const candidate = join(bundleDir, candidateName)
        if (existsSync(candidate)) return candidate
      }
    }
  }
  return undefined
}

function loadRepoBundlePrefix(agentName: string): string {
  const layers: RepoBundleLayer[] = [
    { label: 'Skill Bundle', dir: 'skill', selection: process.env.AGENT_SKILL_BUNDLE },
    { label: 'Memory Bundle', dir: 'memory', selection: process.env.AGENT_MEMORY_BUNDLE },
    { label: 'Runtime Bundle', dir: 'runtime', selection: process.env.AGENT_RUNTIME_BUNDLE },
  ]
  const parts = layers.flatMap(layer => {
    const path = resolveRepoBundleFile(agentName, layer.dir, layer.selection)
    const text = path ? readCached(path)?.trim() : undefined
    return text ? [`## ${layer.label}\n\n${text}`] : []
  })
  return parts.length > 0 ? `${parts.join('\n\n')}\n\n` : ''
}

function loadSeededBundlePrefix(agentName: string): string {
  return loadRepoBundlePrefix(agentName)
}

function augurRootCandidates(): string[] {
  return [
    '/app/agents/augur',
    join(moduleDir, '..', '..', '..', 'agents', 'augur'),
  ]
}

function resolveAugurPath(...segments: string[]): string {
  for (const root of augurRootCandidates()) {
    const candidate = join(root, ...segments)
    if (existsSync(candidate)) return candidate
  }
  return join('/app/agents/augur', ...segments)
}

function resolveBundleMode(message: RequestMessage): 'selective' | 'holistic' {
  const raw = String(
    message.agent_params?.bundle_mode
    ?? process.env.AGENT_MEMORY_BUNDLE
    ?? process.env.AGENT_RUNTIME_BUNDLE
    ?? 'selective',
  ).toLowerCase()
  return raw.includes('holistic') ? 'holistic' : 'selective'
}

function loadRuntimeManifest(mode: 'selective' | 'holistic'): { root: string; manifest: RuntimeBundleManifest } | undefined {
  const filename = `analyze-${mode}-v1.json`
  for (const root of augurRootCandidates()) {
    const candidates = [
      join(root, '.generated', 'bundles', 'runtime', filename),
      join(root, 'bundles', 'runtime', filename),
    ]
    for (const path of candidates) {
      const text = readCached(path)
      if (!text) continue
      try {
        return { root, manifest: JSON.parse(text) as RuntimeBundleManifest }
      } catch {
        continue
      }
    }
  }
  return undefined
}

function loadAugurBundlePrefix(message: RequestMessage): string {
  const resolved = loadRuntimeManifest(resolveBundleMode(message))
  if (!resolved) return ''

  const { root, manifest } = resolved
  const parts: string[] = []

  const addLayer = (label: string, relativePath?: string): void => {
    if (!relativePath) return
    const path = join(root, relativePath)
    const text = readCached(path)?.trim()
    if (!text) return
    parts.push(`## ${label}\n\n${text}`)
  }

  const order = manifest.composition_order ?? ['skill_bundle', 'memory_bundle', 'detector_plan']
  for (const layer of order) {
    if (layer === 'repo_context') continue
    if (layer === 'skill_bundle') addLayer('Skill Bundle', manifest.skill_bundle)
    if (layer === 'memory_bundle') addLayer('Memory Bundle', manifest.memory_bundle)
    if (layer === 'detector_plan') addLayer('Detector Plan', manifest.detector_plan)
  }

  return parts.length > 0 ? `${parts.join('\n\n')}\n\n` : ''
}

function loadAugurModeGuide(message: RequestMessage): string {
  const mode = typeof message.agent_params?.analysis_mode === 'string'
    ? message.agent_params.analysis_mode.trim().toLowerCase()
    : ''
  if (mode !== 'full' && mode !== 'incremental') return ''
  const path = resolveAugurPath('skills', 'analyze', `${mode}-mode.md`)
  const text = readCached(path)?.trim()
  return text ? `## ${mode === 'full' ? 'Full Mode Guide' : 'Incremental Mode Guide'}\n\n${text}\n\n` : ''
}

export function loadAgentProfile(agentName: string): AgentProfile {
  const identity = loadIdentityMetadata(agentName)
  if (agentName === 'augur') {
    return {
      ...identity,
      promptPrefix: 'You are Augur. Favor design-level reasoning and architecture trade-offs.',
      defaultReflectionPrompt: [
        'Return strict JSON with exactly {"project":"...","general":"..."}.',
        'For project, focus on design decisions, bundle strategy, and architecture-specific lessons.',
        'For general, focus on transferable architecture and review lessons.',
      ].join('\n'),
      supportedAgentParams: ['bundle_mode'],
      requiresWorkingDirectory: true,
      validation: {
        required: true,
        validatorScript: resolveAugurPath('skills', 'analyze', 'scripts', 'validate_output.py'),
        maxAttempts: 3,
        finalizeScript: resolveAugurPath('scripts', 'finalize_analysis.py'),
      },
    }
  }

  return {
    ...identity,
    defaultReflectionPrompt: DEFAULT_REFLECTION_PROMPT,
    supportedAgentParams: [],
    requiresWorkingDirectory: false,
    validation: undefined,
  }
}

function hashPromptPrefix(value: string): string {
  return createHash('sha256').update(value).digest('hex')
}

export function buildPromptPlanFromProfile(profile: AgentProfile, message: RequestMessage): PromptPlan {
  const workingDirHint = message.working_dir
    ? `Working directory hint: use \`${message.working_dir}\` as the authoritative starting project root and current working directory. Do not search alternative repo paths unless this exact path is missing or clearly not the target project.`
    : ''
  const runDir = typeof message.agent_params?.run_dir === 'string' && message.agent_params.run_dir.trim()
    ? message.agent_params.run_dir.trim()
    : ''
  const runtimeHints: string[] = []
  if (workingDirHint) runtimeHints.push(workingDirHint)
  if (runDir) {
    runtimeHints.push(`Prepared analysis run: use \`${runDir}\` as the authoritative semantic analysis directory for this request.`)
    runtimeHints.push(`Start with \`${runDir}/blast.json\` and \`${runDir}/facts/\`.`)
    runtimeHints.push('Treat `$RUN` as this prepared directory and prefer its artifacts before broad repo exploration.')
    runtimeHints.push('Do not rediscover or infer alternate analysis roots unless this exact path is missing.')
  }
  const runtimePreamble = runtimeHints.length > 0
    ? `## Runtime Context\n${runtimeHints.map(line => `- ${line}`).join('\n')}\n\n`
    : ''
  const bundlePrefix = profile.supportedAgentParams?.includes('bundle_mode')
    ? loadAugurBundlePrefix(message)
    : loadSeededBundlePrefix(profile.name ?? 'generic')
  const modeGuide = profile.name === 'augur' ? loadAugurModeGuide(message) : ''
  const cacheablePrefix = profile.promptPrefix || bundlePrefix
    ? `${profile.promptPrefix ? `${profile.promptPrefix}\n\n` : ''}${bundlePrefix}`
    : ''
  const dynamicPrompt = `${runtimePreamble}${modeGuide}${message.prompt}`
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

export function buildPromptFromProfile(profile: AgentProfile, message: RequestMessage): string {
  return buildPromptPlanFromProfile(profile, message).fullPrompt
}

export function resolveReflectionPrompt(profile: AgentProfile, message: RequestMessage): string {
  return message.reflection_prompt ?? profile.defaultReflectionPrompt ?? DEFAULT_REFLECTION_PROMPT
}
