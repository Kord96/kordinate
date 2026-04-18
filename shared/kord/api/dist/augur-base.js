import { readdir, readFile, stat } from 'node:fs/promises';
import { isAbsolute, join, relative, resolve } from 'node:path';
import yaml from 'js-yaml';
function isWithin(parentPath, childPath) {
    const relativePath = relative(parentPath, childPath);
    return relativePath !== '' && !relativePath.startsWith('..') && !isAbsolute(relativePath);
}
async function pathExists(path) {
    try {
        await stat(path);
        return true;
    }
    catch {
        return false;
    }
}
async function readJson(path) {
    return JSON.parse(await readFile(path, 'utf8'));
}
async function readYaml(path) {
    return yaml.load(await readFile(path, 'utf8'));
}
async function findAnalysisDirById(analysisRoot, analysisId) {
    if (!analysisId || !(await pathExists(analysisRoot)))
        return null;
    const firstLevel = await readdir(analysisRoot, { withFileTypes: true });
    for (const entry of firstLevel) {
        if (!entry.isDirectory())
            continue;
        const candidate = join(analysisRoot, entry.name, analysisId);
        if (await pathExists(join(candidate, 'meta.json'))) {
            return candidate;
        }
    }
    return null;
}
async function loadStoryDirectory(dirPath) {
    if (!(await pathExists(dirPath)))
        return [];
    const entries = (await readdir(dirPath)).filter(name => name.endsWith('.yaml')).sort();
    return Promise.all(entries.map(name => readYaml(join(dirPath, name))));
}
function normalizeNarratives(document) {
    if (document && typeof document === 'object' && Array.isArray(document.narratives)) {
        return document.narratives;
    }
    return [];
}
function validationPassed(meta) {
    const validation = meta.validation;
    if (!validation || typeof validation !== 'object')
        return false;
    return validation.passed === true;
}
async function loadAcceptedMeta(metaPath) {
    const meta = await readJson(metaPath);
    if (!validationPassed(meta)) {
        throw new Error('analysis not accepted');
    }
    return meta;
}
export async function resolveAugurProjectNames(projectsRoot) {
    const root = resolve(projectsRoot);
    if (!(await pathExists(root)))
        return [];
    const entries = await readdir(root, { withFileTypes: true });
    return entries.filter(entry => entry.isDirectory()).map(entry => entry.name).sort();
}
function projectAnalysisRoot(projectsRoot, project) {
    return join(resolve(projectsRoot), project, 'analysis');
}
function resolveAnalysisDirRef(analysisRoot, value) {
    if (typeof value !== 'string' || !value.trim())
        return '';
    const raw = value.trim();
    return isAbsolute(raw) ? resolve(raw) : resolve(analysisRoot, raw);
}
export async function resolveLatestAcceptedAnalysisDir(projectsRoot, project) {
    const analysisRoot = projectAnalysisRoot(projectsRoot, project);
    const latestPath = join(analysisRoot, 'latest.json');
    if (!(await pathExists(latestPath)))
        return null;
    const payload = await readJson(latestPath);
    const analysisId = typeof payload.analysis_id === 'string' ? payload.analysis_id : '';
    const embeddedDir = resolveAnalysisDirRef(analysisRoot, payload.analysis_dir);
    const analysisDir = embeddedDir && isWithin(analysisRoot, embeddedDir)
        ? embeddedDir
        : await findAnalysisDirById(analysisRoot, analysisId);
    if (!analysisDir)
        return null;
    const metaPath = join(analysisDir, 'meta.json');
    if (!(await pathExists(metaPath)))
        return null;
    const meta = await loadAcceptedMeta(metaPath);
    if (analysisId && meta.analysis_id !== analysisId)
        return null;
    return analysisDir;
}
export async function loadAugurProjectSummary(projectsRoot, project) {
    const analysisDir = await resolveLatestAcceptedAnalysisDir(projectsRoot, project);
    if (!analysisDir)
        return null;
    const [meta, atlas] = await Promise.all([
        loadAcceptedMeta(join(analysisDir, 'meta.json')),
        readJson(join(analysisDir, 'atlas.json')),
    ]);
    return {
        project,
        title: String(atlas.project || project),
        purpose: String(atlas.purpose || ''),
        latest_analysis_id: String(meta.analysis_id || ''),
        latest_commit_sha: String(meta.sha || ''),
    };
}
export async function listAugurAnalysisSummaries(projectsRoot, project) {
    const indexPath = join(projectAnalysisRoot(projectsRoot, project), 'index.json');
    if (!(await pathExists(indexPath)))
        return [];
    const payload = await readJson(indexPath);
    const analyses = Array.isArray(payload.analyses) ? payload.analyses : [];
    return analyses
        .filter(item => item && typeof item === 'object' && (item.validation?.passed === true))
        .map(item => {
        const record = item;
        return {
            analysis_id: String(record.analysis_id || ''),
            commit_sha: String(record.sha || ''),
            analyzed_at: String(record.analyzed_at || ''),
            validation_passed: true,
            status: 'accepted',
        };
    });
}
async function findAugurAnalysisDir(projectsRoot, project, analysisId) {
    const indexPath = join(projectAnalysisRoot(projectsRoot, project), 'index.json');
    if (!(await pathExists(indexPath)))
        return null;
    const payload = await readJson(indexPath);
    const analyses = Array.isArray(payload.analyses) ? payload.analyses : [];
    const record = analyses.find(item => item && typeof item === 'object'
        && String(item.analysis_id || '') === analysisId
        && (item.validation?.passed === true));
    if (!record)
        return null;
    const root = projectAnalysisRoot(projectsRoot, project);
    const embeddedDir = resolveAnalysisDirRef(root, record.analysis_dir);
    const analysisDir = embeddedDir && isWithin(root, embeddedDir)
        ? embeddedDir
        : await findAnalysisDirById(root, analysisId);
    if (!analysisDir)
        return null;
    return analysisDir;
}
export async function loadAugurAnalysisDetails(projectsRoot, project, analysisId) {
    const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId);
    if (!analysisDir)
        return null;
    const meta = await loadAcceptedMeta(join(analysisDir, 'meta.json'));
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
    };
}
export async function loadAugurBase(projectsRoot, project, analysisId) {
    const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId);
    if (!analysisDir)
        return null;
    const [meta, atlas, stories, narrativesDoc, repairLog] = await Promise.all([
        loadAcceptedMeta(join(analysisDir, 'meta.json')),
        readJson(join(analysisDir, 'atlas.json')),
        loadStoryDirectory(join(analysisDir, 'stories')),
        readYaml(join(analysisDir, 'narratives.yaml')),
        (await pathExists(join(analysisDir, 'repair-log.json')))
            ? readJson(join(analysisDir, 'repair-log.json'))
            : Promise.resolve(null),
    ]);
    return {
        project,
        analysis_id: analysisId,
        atlas,
        stories,
        narratives: normalizeNarratives(narrativesDoc),
        meta,
        repair_log: repairLog,
    };
}
export async function loadAugurReflections(projectsRoot, project, analysisId) {
    const analysisDir = await findAugurAnalysisDir(projectsRoot, project, analysisId);
    if (!analysisDir)
        return null;
    const indexPath = join(analysisDir, 'reflections', 'index.json');
    if (!(await pathExists(indexPath)))
        return [];
    const payload = await readJson(indexPath);
    return Array.isArray(payload.reflections) ? payload.reflections : [];
}
