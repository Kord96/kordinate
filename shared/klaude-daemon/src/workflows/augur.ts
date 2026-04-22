import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import { basename, join } from 'node:path'
import { constants as fsConstants } from 'node:fs'
import { access, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import type { AgentContract, RequestMessage, RuntimeResult } from '../types.js'

type DaemonConfigLike = {
  executionProfile: {
    homeDirectory?: string
    provider: string
    model: string
  }
}

type ValidationContext = {
  targetDir?: string
  extraEnv?: Record<string, string>
}

type BeforeRuntimeResult = {
  skipResult?: RuntimeResult
  runtimeMessage?: RequestMessage
}

export type WorkflowContext = {
  agentName: string
  agentContract: AgentContract
  daemonConfig: DaemonConfigLike
  publishProgress: (message: RequestMessage, event: {
    source: 'agent-daemon' | 'provider' | 'gateway'
    kind: string
    payload?: Record<string, unknown>
  }) => Promise<void>
  buildArtifactsMetadata: (targetDir: string, finalizePayload?: Record<string, unknown>) => NonNullable<NonNullable<RuntimeResult['metadata']>['artifacts']>
}

export interface AgentWorkflowHooks {
  beforeRuntime?(message: RequestMessage): Promise<BeforeRuntimeResult | undefined>
  validationContext?(message: RequestMessage): Promise<ValidationContext | undefined>
}

interface AugurBlastManifest {
  mode?: string
  tier?: number
  reasons?: string[]
  current_sha?: string
  current_commit_time?: string
  previous_sha?: string
  previous_commit_time?: string
  base_analysis_dir?: string
  analysis_dir?: string
}

interface AugurAnalysisPlan {
  analysis_mode?: string
  bundle_mode?: string
  base_analysis_dir?: string
  blast?: AugurBlastManifest
}

type AugurPreparedDeterministicArtifacts = {
  project: string
  runDir: string
}

type AugurAnalysisContext = {
  project: string
  mode: 'full' | 'incremental'
  working_dir: string
  run_dir: string
  analysis_dir: string
  project_mem: string
  facts_dir: string
  startup_path: string
  blast_path: string
  concepts_path: string
  latest_path: string
  atlas_path: string
  starter_files: string[]
  startup_directive: string
}

async function pathExists(path: string): Promise<boolean> {
  try {
    await access(path, fsConstants.F_OK)
    return true
  } catch {
    return false
  }
}

async function removePathIfExists(target: string): Promise<void> {
  await rm(target, { recursive: true, force: true })
}

function requestCommandText(message: RequestMessage): string {
  return typeof message.raw_prompt === 'string' && message.raw_prompt.trim()
    ? message.raw_prompt
    : message.prompt
}

function gitArgsForRepo(repoPath: string, ...gitArgs: string[]): string[] {
  return ['-c', `safe.directory=${repoPath}`, '-C', repoPath, ...gitArgs]
}

function correlationSuffix(message: RequestMessage): string {
  const raw = typeof message.correlation_id === 'string' ? message.correlation_id.trim() : ''
  if (!raw) return 'run'
  const safe = raw.replace(/[^a-zA-Z0-9_-]+/g, '-')
  return safe.slice(-12) || 'run'
}

function analysisTimestamp(): string {
  const iso = new Date().toISOString()
  return iso.replace(/\.\d{3}Z$/, 'Z').replace(/:/g, '-')
}

async function runCommand(command: string, args: string[], cwd: string, extraEnv?: Record<string, string>): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      env: {
        ...process.env,
        ...(extraEnv ?? {}),
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', chunk => { stdout += String(chunk) })
    child.stderr.on('data', chunk => { stderr += String(chunk) })
    child.on('close', code => {
      if (code === 0) {
        resolve(stdout.trim())
        return
      }
      reject(new Error(`${command} ${args.join(' ')} failed with code ${code}: ${(stderr || stdout).trim()}`))
    })
  })
}

async function runRequiredCommand(command: string, args: string[], cwd: string, extraEnv?: Record<string, string>): Promise<void> {
  await runCommand(command, args, cwd, extraEnv)
}

function isAugurAnalyzeRequest(context: WorkflowContext, message: RequestMessage): boolean {
  const commandText = requestCommandText(message)
  return context.agentContract.specialization === 'augur'
    && commandText.trim().startsWith('/analyze')
    && typeof message.working_dir === 'string'
    && message.working_dir.length > 0
}

function isAugurDeterministicOnlyRequest(context: WorkflowContext, message: RequestMessage): boolean {
  const commandText = requestCommandText(message)
  return isAugurAnalyzeRequest(context, message) && commandText.includes('--deterministic-only')
}

function isForceFullAugurAnalyzeRequest(context: WorkflowContext, message: RequestMessage): boolean {
  const commandText = requestCommandText(message)
  return isAugurAnalyzeRequest(context, message) && commandText.includes('--full')
}

async function resolveAugurAnalysisPlan(
  context: WorkflowContext,
  message: RequestMessage,
  options?: { forcedAnalysisMode?: 'full' | 'incremental' },
): Promise<AugurAnalysisPlan> {
  const workingDir = message.working_dir
  const agentHome = context.daemonConfig.executionProfile.homeDirectory
  if (!workingDir || !agentHome) {
    throw new Error('working_dir and agent home are required for Augur analysis')
  }
  const project = basename(workingDir)
  const kordHome = process.env.KORDINATE_HOME ?? '/app'
  const args = [
    join(kordHome, 'agents', 'augur', 'scripts', 'resolve_analysis_plan.py'),
    workingDir,
    '--agent-home', agentHome,
    '--project', project,
    '--analysis-mode', options?.forcedAnalysisMode ?? 'auto',
    '--bundle-mode',
    typeof message.agent_params?.bundle_mode === 'string' ? message.agent_params.bundle_mode : 'auto',
  ]
  let payload: string
  try {
    payload = await runCommand('python3', args, agentHome)
  } catch (error) {
    try {
      payload = await runCommand('python3', args, agentHome)
    } catch (retryError) {
      const [repoExists, repoGitExists, repoGitHead] = await Promise.all([
        pathExists(workingDir),
        pathExists(join(workingDir, '.git')),
        runCommand('git', gitArgsForRepo(workingDir, 'rev-parse', 'HEAD'), agentHome).catch(() => ''),
      ])
      const originalMessage = error instanceof Error ? error.message : String(error)
      const retryMessage = retryError instanceof Error ? retryError.message : String(retryError)
      throw new Error(
        [
          retryMessage,
          `resolve_analysis_plan diagnostics: cwd=${agentHome}`,
          `repo_root=${workingDir}`,
          `repo_exists=${repoExists}`,
          `repo_git_exists=${repoGitExists}`,
          `git_head=${repoGitHead || '<unresolved>'}`,
          `first_error=${originalMessage}`,
        ].join('\n'),
      )
    }
  }
  if (!payload) {
    throw new Error('resolve_analysis_plan.py did not return a plan')
  }
  return JSON.parse(payload) as AugurAnalysisPlan
}

async function isAcceptedAugurSemanticAnalysisDir(targetDir: string): Promise<boolean> {
  const metaPath = join(targetDir, 'meta.json')
  const atlasPath = join(targetDir, 'atlas.json')
  const storiesDir = join(targetDir, 'stories')
  const narrativesPath = join(targetDir, 'narratives.yaml')
  if (!(await pathExists(metaPath))) return false
  if (!(await pathExists(atlasPath))) return false
  if (!(await pathExists(storiesDir))) return false
  if (!(await pathExists(narrativesPath))) return false

  try {
    const meta = JSON.parse(await readFile(metaPath, 'utf8')) as { validation?: { passed?: boolean } }
    return meta.validation?.passed === true
  } catch {
    return false
  }
}

async function resolveAcceptedAugurLatestAnalysisDir(agentHome: string, project: string): Promise<string | undefined> {
  const latestPath = join(agentHome, 'memory', 'projects', project, 'analysis', 'latest.json')
  if (!(await pathExists(latestPath))) return undefined
  try {
    const latest = JSON.parse(await readFile(latestPath, 'utf8')) as { analysis_dir?: string }
    const analysisDir = typeof latest.analysis_dir === 'string' && latest.analysis_dir.trim()
      ? latest.analysis_dir.trim()
      : undefined
    if (!analysisDir) return undefined
    if (!(await isAcceptedAugurSemanticAnalysisDir(analysisDir))) return undefined
    return analysisDir
  } catch {
    return undefined
  }
}

async function hashValidatedDirectory(root: string): Promise<string> {
  const hash = createHash('sha256')
  async function walk(dir: string, relativePrefix = ''): Promise<void> {
    const { readdir } = await import('node:fs/promises')
    const entries = (await readdir(dir, { withFileTypes: true }))
      .filter(entry => entry.name !== '.validate-lock')
      .sort((a, b) => a.name.localeCompare(b.name))
    for (const entry of entries) {
      const absolutePath = join(dir, entry.name)
      const relativePath = relativePrefix ? `${relativePrefix}/${entry.name}` : entry.name
      if (entry.isDirectory()) {
        hash.update(`dir:${relativePath}\n`)
        await walk(absolutePath, relativePath)
      } else if (entry.isFile()) {
        hash.update(`file:${relativePath}\n`)
        hash.update(await readFile(absolutePath))
        hash.update('\n')
      }
    }
  }
  await walk(root)
  return hash.digest('hex')
}

async function prepareAugurDeterministicArtifacts(
  context: WorkflowContext,
  message: RequestMessage,
  options?: { clearSemanticOutputs?: boolean; eventKindPrefix?: string; forcedBlastMode?: 'full' | 'incremental' },
): Promise<AugurPreparedDeterministicArtifacts> {
  const workingDir = message.working_dir
  const agentHome = context.daemonConfig.executionProfile.homeDirectory
  if (!workingDir || !agentHome) {
    throw new Error('working_dir and agent home are required for Augur deterministic preparation')
  }

  const project = basename(workingDir)
  const kordHome = process.env.KORDINATE_HOME ?? '/app'
  const currentSha = await runCommand('git', gitArgsForRepo(workingDir, 'rev-parse', 'HEAD'), agentHome)
  const commitTime = currentSha
    ? await runCommand('git', gitArgsForRepo(workingDir, 'show', '-s', '--format=%ct', currentSha), agentHome)
    : undefined
  if (!currentSha || !commitTime) {
    throw new Error('could not resolve git HEAD for Augur deterministic preparation')
  }

  const suffix = correlationSuffix(message)
  const runId = suffix === 'run'
    ? analysisTimestamp()
    : `${analysisTimestamp()}--${suffix}`
  const runDir = join(agentHome, 'memory', 'projects', project, 'analysis', currentSha, runId)
  const factsDir = join(runDir, 'facts')
  const env = {
    KORDINATE_HOME: kordHome,
    AGENT_HOME_DIR: agentHome,
    ROOT: workingDir,
    PROJECT: project,
    RUN: runDir,
  }

  if (options?.clearSemanticOutputs) {
    await removePathIfExists(runDir)
  }
  await mkdir(factsDir, { recursive: true })

  const eventKindPrefix = options?.eventKindPrefix ?? 'augur.deterministic_prepare'
  await context.publishProgress(message, {
    source: 'agent-daemon',
    kind: `${eventKindPrefix}.start`,
    payload: { project, working_dir: workingDir, run_dir: runDir },
  })
  await runRequiredCommand('python3', [
    join(kordHome, 'agents', 'augur', 'scripts', 'prepare_deterministic_run.py'),
    workingDir,
    '--run-dir', runDir,
    '--project', project,
    '--agent-home', agentHome,
    '--analysis-mode', 'full',
    '--current-sha', currentSha,
    '--pretty',
  ], agentHome, env)
  const blastPath = join(runDir, 'blast.json')
  try {
    const blast = JSON.parse(await readFile(blastPath, 'utf8')) as Record<string, unknown>
    if (options?.forcedBlastMode) {
      blast.mode = options.forcedBlastMode
      const existingReasons = Array.isArray(blast.reasons)
        ? blast.reasons.map(reason => String(reason))
        : []
      blast.reasons = Array.from(new Set([...existingReasons, `forced-${options.forcedBlastMode}`]))
    }
    blast.analysis_dir = runDir
    await writeFile(blastPath, `${JSON.stringify(blast, null, 2)}\n`, 'utf8')
  } catch {
    // Leave the original blast file untouched if rewrite fails; validation will surface it later.
  }
  await context.publishProgress(message, {
    source: 'agent-daemon',
    kind: `${eventKindPrefix}.complete`,
    payload: { run_dir: runDir },
  })

  return { project, runDir }
}

async function buildAugurAnalysisContext(
  context: WorkflowContext,
  workingDir: string,
  project: string,
  runDir: string,
  analysisMode: 'full' | 'incremental',
): Promise<AugurAnalysisContext> {
  const scriptPath = context.agentContract.workflow?.analysisContextScript
  if (!scriptPath) {
    throw new Error('augur analysis context script is missing from the injected agent contract')
  }
  const cwd = contextHomeDirectoryFallback()
  const payload = await runCommand('python3', [
    scriptPath,
    '--project', project,
    '--working-dir', workingDir,
    '--run-dir', runDir,
    '--analysis-mode', analysisMode,
  ], cwd)
  return JSON.parse(payload) as AugurAnalysisContext
}

function contextHomeDirectoryFallback(): string {
  return process.env.AGENT_HOME_DIR
    ?? process.env.HOME
    ?? process.cwd()
}

export function createAugurWorkflowHooks(context: WorkflowContext): AgentWorkflowHooks {
  return {
    async beforeRuntime(message) {
      if (isAugurDeterministicOnlyRequest(context, message)) {
        const workingDir = message.working_dir
        const agentHome = context.daemonConfig.executionProfile.homeDirectory
        if (!workingDir || !agentHome) {
          return {
            skipResult: {
              status: 'error',
              output: 'working_dir and agent home are required for Augur deterministic-only',
              errors: ['working_dir and agent home are required for Augur deterministic-only'],
            },
          }
        }
        const prepared = await prepareAugurDeterministicArtifacts(context, message, {
          clearSemanticOutputs: true,
          eventKindPrefix: 'augur.deterministic_only',
        })
        return {
          skipResult: {
            status: 'success',
            output: `Deterministic phase artifacts written to ${prepared.runDir}`,
            metadata: {
              artifacts: {
                root: prepared.runDir,
                files: {},
                schemas: {},
              },
            },
          },
        }
      }

      const plan = await resolveAugurAnalysisPlan(context, message, {
        forcedAnalysisMode: isForceFullAugurAnalyzeRequest(context, message) ? 'full' : undefined,
      })
      const blast = plan.blast ?? {}
      let analysisMode: 'full' | 'incremental' = plan.analysis_mode === 'incremental' ? 'incremental' : 'full'
      if (!isForceFullAugurAnalyzeRequest(context, message)) {
        if (blast.mode === 'skip') {
          const targetDir = typeof blast.base_analysis_dir === 'string' && blast.base_analysis_dir.trim()
            ? blast.base_analysis_dir.trim()
            : undefined
          const agentHome = context.daemonConfig.executionProfile.homeDirectory
          const workingDir = message.working_dir
          const project = workingDir ? basename(workingDir) : undefined
          const acceptedLatestDir = agentHome && project
            ? await resolveAcceptedAugurLatestAnalysisDir(agentHome, project)
            : undefined
          if (!targetDir || !(await pathExists(targetDir)) || !acceptedLatestDir || acceptedLatestDir !== targetDir) {
            throw new Error('blast reported skip but no accepted latest semantic analysis directory was available')
          }

          await context.publishProgress(message, {
            source: 'agent-daemon',
            kind: 'augur.semantic.skip',
            payload: {
              mode: blast.mode,
              tier: blast.tier ?? null,
              reasons: blast.reasons ?? [],
              target_dir: targetDir,
              previous_sha: blast.previous_sha ?? null,
              current_sha: blast.current_sha ?? null,
            },
          })

          const token = await hashValidatedDirectory(targetDir)
          return {
            skipResult: {
              status: 'success',
              output: `No architectural changes detected. Reusing accepted analysis at ${targetDir}\n\nValidation token: ${token}`,
              metadata: {
                artifacts: context.buildArtifactsMetadata(targetDir),
                validation: {
                  required: true,
                  passed: true,
                  attempts: 0,
                  token,
                  target_dir: targetDir,
                },
              },
            },
          }
        }
      }

      const prepared = await prepareAugurDeterministicArtifacts(context, message, {
        clearSemanticOutputs: true,
        eventKindPrefix: 'augur.semantic_prepare',
        forcedBlastMode: analysisMode,
      })
      const workingDir = message.working_dir
      if (!workingDir) {
        throw new Error('working_dir is required for Augur semantic preparation')
      }
      const resolvedBundleMode = plan.bundle_mode ?? (analysisMode === 'incremental' ? 'selective' : 'holistic')
      const analysisContext = await buildAugurAnalysisContext(context, workingDir, prepared.project, prepared.runDir, analysisMode)
      return {
        runtimeMessage: {
          ...message,
          workspace: {
            working_dir: workingDir,
            output_dir: prepared.runDir,
            agent_root: `${process.env.KORDINATE_HOME ?? '/app'}/agents/augur`,
          },
          resources: {
            validator_script: context.agentContract.validation?.validatorScript,
            concept_catalog_index: `${process.env.KORDINATE_HOME ?? '/app'}/agents/augur/references/concepts/README.md`,
            framework_catalog_index: `${process.env.KORDINATE_HOME ?? '/app'}/agents/augur/references/frameworks/README.md`,
          },
          agent_params: {
            ...(message.agent_params ?? {}),
            run_dir: prepared.runDir,
            analysis_mode: analysisMode,
            bundle_mode: resolvedBundleMode,
            startup_guidance: {
              directive: analysisContext.startup_directive,
              starter_files: analysisContext.starter_files,
            },
          },
        },
      }
    },

    async validationContext(message) {
      if (!isAugurAnalyzeRequest(context, message)) return undefined
      const workingDir = message.working_dir
      const agentHome = context.daemonConfig.executionProfile.homeDirectory
      if (!workingDir || !agentHome) return undefined
      const project = basename(workingDir)
      const latestDir = await resolveAcceptedAugurLatestAnalysisDir(agentHome, project)
      const explicitRunDir = typeof message.agent_params?.run_dir === 'string' && message.agent_params.run_dir.trim()
        ? message.agent_params.run_dir.trim()
        : undefined
      return {
        targetDir: explicitRunDir ?? latestDir,
        extraEnv: {
          ...(requestCommandText(message).includes('--deterministic-only')
            ? { AUGUR_DETERMINISTIC_ONLY: '1' }
            : {}),
          AUGUR_PROJECT_ROOT: workingDir,
        },
      }
    },
  }
}
