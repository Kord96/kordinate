import { existsSync } from 'node:fs';
import { basename } from 'node:path';
import { loadPathConfig } from './path-config.js';
const pathConfig = loadPathConfig();
function repoRootCandidates() {
    const values = [
        process.env.PROJECTS_ROOT,
        pathConfig.projectsRoot,
    ];
    return Array.from(new Set(values.filter((value) => typeof value === 'string' && value.trim().length > 0)));
}
function canonicalRepoPath(repo, rest) {
    for (const root of repoRootCandidates()) {
        const candidate = `${root}/${repo}${rest}`;
        if (existsSync(candidate))
            return candidate;
    }
    const kordHome = process.env.KORDINATE_HOME ?? pathConfig.kordinateHome;
    if (repo === basename(kordHome) && existsSync(kordHome)) {
        const candidate = `${kordHome}${rest}`;
        if (existsSync(candidate))
            return candidate;
    }
    return undefined;
}
export function canonicalizeWorkingDir(workingDir) {
    if (!workingDir)
        return workingDir;
    if (existsSync(workingDir))
        return workingDir;
    const knownPrefixes = [`${pathConfig.projectsRoot}/`, '/kord/workstation/home/project/'];
    const matchedPrefix = knownPrefixes.find(prefix => workingDir.startsWith(prefix));
    if (!matchedPrefix)
        return workingDir;
    const suffix = workingDir.slice(matchedPrefix.length);
    const slashIndex = suffix.indexOf('/');
    const repo = slashIndex === -1 ? suffix : suffix.slice(0, slashIndex);
    const rest = slashIndex === -1 ? '' : suffix.slice(slashIndex);
    if (!repo)
        return workingDir;
    return canonicalRepoPath(repo, rest) ?? workingDir;
}
