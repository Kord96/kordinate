import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const moduleDir = dirname(fileURLToPath(import.meta.url));
const configPath = join(moduleDir, '..', '..', '..', 'runtime', 'path-config.json');
const defaultConfig = {
    kordinateHome: '/app',
    runtimeRoot: '/kord',
    agentsRuntimeRoot: '/kord/agents',
    sharedRoot: '/kord/shared',
    projectsRoot: '/kord/shared/repos',
    augurReleaseStore: '/kord/shared/runtime/artifacts/augur',
    augurMemoryProjectsRoot: '/kord/agents/augur-local-codex/memory/projects',
};
export function loadPathConfig() {
    if (!existsSync(configPath))
        return defaultConfig;
    try {
        return { ...defaultConfig, ...JSON.parse(readFileSync(configPath, 'utf8')) };
    }
    catch {
        return defaultConfig;
    }
}
