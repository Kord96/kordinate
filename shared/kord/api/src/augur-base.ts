import { readdir, readFile, stat } from 'node:fs/promises'
import { isAbsolute, join, relative, resolve } from 'node:path'
import yaml from 'js-yaml'

export interface AugurProjectSummary {
  project: string
  title: string
  purpose: string
  latest_analysis_id: string
  latest_commit_sha: string
}

export interface AugurAnalysisSummary {
  analysis_id: string
  commit_sha: string
  commit_time: string
  analyzed_at: string
  validation_passed: boolean
  status: string
  request_id: string
  repository: Record<string, unknown>
  agent: Record<string, unknown>
  validation: Record<string, unknown>
}

export interface AugurAnalysisDetails {
  project: string
  analysis_id: string
  meta: Record<string, unknown>
  artifacts: {
    atlas: boolean
    stories: boolean
    narratives: boolean
    repair_log: boolean
    reflections: boolean
  }
}

export interface AugurBasePayload {
  project: string
  analysis_id: string
  atlas: Record<string, unknown>
  stories: unknown[]
  narratives: unknown[]
  symbols_seed: Record<string, unknown> | null
  meta: Record<string, unknown>
  repair_log: Record<string, unknown> | null
}

function isWithin(parentPath: string, childPath: string): boolean {
  const relativePath = relative(parentPath, childPath)
  return relativePath !== '' && !relativePath.startsWith('..') && !isAbsolute(relativePath)
}

async function pathExists(path: string): Promise<boolean> {
  try {
    await stat(path)
    return true
  } catch {
    return false
  }
}

async function readJson<T = unknown>(path: string): Promise<T> {
  return JSON.parse(await readFile(path, 'utf8')) as T
}

async function readYaml(path: string): Promise<unknown> {
  return yaml.load(await readFile(path, 'utf8'))
}

async function findAnalysisDirById(analysisRoot: string, analysisId: string): Promise<string | null> {
  if (!analysisId || !(await pathExists(analysisRoot))) return null
  const firstLevel = await readdir(analysisRoot, { withFileTypes: true })
  for (const entry of firstLevel) {
    if (!entry.isDirectory()) continue
    const candidate = join(analysisRoot, entry.name, analysisId)
    if (await pathExists(join(candidate, 'meta.json'))) {
      return candidate
    }
  }
  return null
}

async function loadStoryDirectory(dirPath: string): Promise<unknown[]> {
  if (!(await pathExists(dirPath))) return []
  const entries = (await readdir(dirPath)).filter(name => name.endsWith('.yaml')).sort()
  return Promise.all(entries.map(name => readYaml(join(dirPath, name))))
}

function normalizeNarratives(document: unknown): unknown[] {
  if (document && typeof document === 'object' && Array.isArray((document as { narratives?: unknown[] }).narratives)) {
    return (document as { narratives: unknown[] }).narratives
  }
  return []
}

function validationPassed(meta: Record<string, unknown>): boolean {
  const direct = meta.validation
  if (direct && typeof direct === 'object' && (direct as { passed?: unknown }).passed === true) return true
  const analysis = meta.analysis
  if (!analysis || typeof analysis !== 'object') return false
  const nested = (analysis as { validation?: unknown }).validation
  if (!nested || typeof nested !== 'object') return false
  return (nested as { passed?: unknown }).passed === true
}

async function loadAcceptedMeta(metaPath: string): Promise<Record<string, unknown>> {
  const meta = await readJson<Record<string, unknown>>(metaPath)
  if (!validationPassed(meta)) {
    throw new Error('analysis not accepted')
  }
  return meta
}

export async function resolveAugurProjectNames(projectsRoot: string): Promise<string[]> {
  const root = resolve(projectsRoot)
  if (!(await pathExists(root))) return []
  const entries = await readdir(root, { withFileTypes: true })
  return entries.filter(entry => entry.isDirectory()).map(entry => entry.name).sort()
}

function projectAnalysisRoot(projectsRoot: string, project: string): string {
  return join(resolve(projectsRoot), project, 'analysis')
}

function resolveAnalysisDirRef(analysisRoot: string, value: unknown): string {
  if (typeof value !== 'string' || !value.trim()) return ''
  const raw = value.trim()
  return isAbsolute(raw) ? resolve(raw) : resolve(analysisRoot, raw)
}

export async function resolveLatestAcceptedAnalysisDir(projectsRoot: string, project: string): Promise<string | null> {
  const analysisRoot = projectAnalysisRoot(projectsRoot, project)
  const latestPath = join(analysisRoot, 'latest.json')
  if (!(await pathExists(latestPath))) return null
  const payload = await readJson<Record<string, unknown>>(latestPath)
  const analysisId = typeof payload.analysis_id === 'string' ? payload.analysis_id : ''
  const embeddedDir = resolveAnalysisDirRef(analysisRoot, payload.analysis_dir)
  const analysisDir = embeddedDir && isWithin(analysisRoot, embeddedDir)
    ? embeddedDir
    : await findAnalysisDirById(analysisRoot, analysisId)
  if (!analysisDir) return null
  const metaPath = join(analysisDir, 'meta.json')
  if (!(await pathExists(metaPath))) return null
  const meta = await loadAcceptedMeta(metaPath)
  const resolvedAnalysisId = String((meta.analysis && typeof meta.analysis === 'object' ? (meta.analysis as { id?: unknown }).id : '') || meta.analysis_id || '')
  if (analysisId && resolvedAnalysisId !== analysisId) return null
  return analysisDir
}

export async function loadAugurProjectSummary(projectsRoot: string, project: string): Promise<AugurProjectSummary | null> {
  const analysisDir = await resolveLatestAcceptedAnalysisDir(projectsRoot, project)
  if (!analysisDir) return null
  const [meta, atlas] = await Promise.all([
    loadAcceptedMeta(join(analysisDir, 'meta.json')),
    readJson<Record<string, unknown>>(join(analysisDir, 'atlas.json')),
  ])
  return {
    project,
    title: String(atlas.project || project),
    purpose: String(atlas.purpose || ''),
    latest_analysis_id: String((meta.analysis && typeof meta.analysis === 'object' ? (meta.analysis as { id?: unknown }).id : '') || meta.analysis_id || ''),
    latest_commit_sha: String((meta.repository && typeof meta.repository === 'object' ? (meta.repository as { commit?: unknown }).commit : '') || meta.sha || ''),
  }
}

export async function listAugurAnalysisSummaries(projectsRoot: string, project: string): Promise<AugurAnalysisSummary[]> {
  const indexPath = join(projectAnalysisRoot(projectsRoot, project), 'index.json')
  if (!(await pathExists(indexPath))) return []
  const payload = await readJson<Record<string, unknown>>(indexPath)
  const analyses = Array.isArray(payload.analyses) ? payload.analyses : []
  return analyses
    .filter(item => item && typeof item === 'object' && ((item as { validation?: { passed?: unknown } }).validation?.passed === true))
    .map(item => {
      const record = item as Record<string, unknown>
      return {
        analysis_id: String(record.analysis_id || ''),
        commit_sha: String(record.sha || ''),
        commit_time: String(record.commit_time || ''),
        analyzed_at: String(record.analyzed_at || ''),
        validation_passed: true,
        status: 'accepted',
        request_id: String(record.request_id || ''),
        repository: (record.repository && typeof record.repository === 'object') ? record.repository as Record<string, unknown> : {},
        agent: (record.agent && typeof record.agent === 'object') ? record.agent as Record<string, unknown> : {},
        validation: (record.validation && typeof record.validation === 'object') ? record.validation as Record<string, unknown> : {},
      }
    })
}

async function findAugurAnalysisDir(projectsRoot: string, project: string, analysisId: string): Promise<string | null> {
  const indexPath = join(projectAnalysisRoot(projectsRoot, project), 'index.json')
  if (!(await pathExists(indexPath))) return null
  const payload = await readJson<Record<string, unknown>>(indexPath)
  const analyses = Array.isArray(payload.analyses) ? payload.analyses : []
  const record = analyses.find(item =>
    item && typeof item === 'object'
    && String((item as Record<string, unknown>).analysis_id || '') === analysisId
    && ((item as { validation?: { passed?: unknown } }).validation?.passed === true),
  ) as Record<string, unknown> | undefined
  if (!record) return null
  const root = projectAnalysisRoot(projectsRoot, project)
  const embeddedDir = resolveAnalysisDirRef(root, record.analysis_dir)
  const analysisDir = embeddedDir && isWithin(root, embeddedDir)
    ? embeddedDir
    : await findAnalysisDirById(root, analysisId)
  if (!analysisDir) return null
  return analysisDir
}

export async function loadAugurAnalysisDetails(projectsRoot: string, project: string, analysisId: string): Promise<AugurAnalysisDetails | null> {
  const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId)
  if (!analysisDir) return null
  const meta = await loadAcceptedMeta(join(analysisDir, 'meta.json'))
  return {
    project,
    analysis_id: analysisId,
    meta,
    artifacts: {
      atlas: await pathExists(join(analysisDir, 'atlas.json')),
      stories: await pathExists(join(analysisDir, 'stories')),
      narratives: await pathExists(join(analysisDir, 'narratives.yaml')),
      repair_log: await pathExists(join(analysisDir, 'repair-log.json')),
      reflections: await pathExists(join(analysisDir, 'reflections')),
    },
  }
}

export async function loadAugurBase(projectsRoot: string, project: string, analysisId: string): Promise<AugurBasePayload | null> {
  const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId)
  if (!analysisDir) return null
  const [meta, atlas, stories, narrativesDoc, symbolsSeed, repairLog] = await Promise.all([
    loadAcceptedMeta(join(analysisDir, 'meta.json')),
    readJson<Record<string, unknown>>(join(analysisDir, 'atlas.json')),
    loadStoryDirectory(join(analysisDir, 'stories')),
    readYaml(join(analysisDir, 'narratives.yaml')),
    (await pathExists(join(analysisDir, 'facts', 'symbols-seed.json')))
      ? readJson<Record<string, unknown>>(join(analysisDir, 'facts', 'symbols-seed.json'))
      : Promise.resolve(null),
    (await pathExists(join(analysisDir, 'repair-log.json')))
      ? readJson<Record<string, unknown>>(join(analysisDir, 'repair-log.json'))
      : Promise.resolve(null),
  ])
  return {
    project,
    analysis_id: analysisId,
    atlas,
    stories,
    narratives: normalizeNarratives(narrativesDoc),
    symbols_seed: symbolsSeed,
    meta,
    repair_log: repairLog,
  }
}

export async function loadAugurReflections(projectsRoot: string, project: string, analysisId: string): Promise<unknown[] | null> {
  const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId)
  if (!analysisDir) return null
  const indexPath = join(analysisDir, 'reflections', 'index.json')
  if (!(await pathExists(indexPath))) return []
  const payload = await readJson<Record<string, unknown>>(indexPath)
  return Array.isArray(payload.reflections) ? payload.reflections : []
}
