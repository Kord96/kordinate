import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

type PathConfig = {
  kordinateHome: string
  runtimeRoot: string
  agentsRuntimeRoot: string
  sharedRoot: string
  projectsRoot: string
  augurReleaseStore: string
  augurMemoryProjectsRoot: string
}

const moduleDir = dirname(fileURLToPath(import.meta.url))
const configPath = join(moduleDir, '..', '..', '..', 'runtime', 'path-config.json')

const defaultConfig: PathConfig = {
  kordinateHome: '/app',
  runtimeRoot: '/kord',
  agentsRuntimeRoot: '/kord/agents',
  sharedRoot: '/kord/shared',
  projectsRoot: '/kord/shared/repos',
  augurReleaseStore: '/kord/shared/runtime/artifacts/augur',
  augurMemoryProjectsRoot: '/kord/agents/augur-local-codex/memory/projects',
}

export function loadPathConfig(): PathConfig {
  if (!existsSync(configPath)) return defaultConfig
  try {
    return { ...defaultConfig, ...(JSON.parse(readFileSync(configPath, 'utf8')) as Partial<PathConfig>) }
  } catch {
    return defaultConfig
  }
}
