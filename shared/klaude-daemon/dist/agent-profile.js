import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadIdentityMetadata } from './identity.js';
const DEFAULT_REFLECTION_PROMPT = [
    'Based on the completed task, return strict JSON only with exactly these keys:',
    '{"project":"...","general":"..."}',
    'project: lessons specific to the current project/repo/context.',
    'general: lessons that transfer to any project.',
    'Use strings only. If there is no strong lesson for a key, return an empty string.',
].join('\n');
const moduleDir = dirname(fileURLToPath(import.meta.url));
const bundleTextCache = new Map();
function readCached(path) {
    if (bundleTextCache.has(path))
        return bundleTextCache.get(path);
    if (!existsSync(path))
        return undefined;
    const text = readFileSync(path, 'utf8');
    bundleTextCache.set(path, text);
    return text;
}
function augurRootCandidates() {
    return [
        '/app/agents/augur',
        join(moduleDir, '..', '..', '..', 'agents', 'augur'),
    ];
}
function resolveBundleMode(message) {
    const raw = String(message.agent_params?.bundle_mode
        ?? process.env.AGENT_MEMORY_BUNDLE
        ?? process.env.AGENT_RUNTIME_BUNDLE
        ?? 'selective').toLowerCase();
    return raw.includes('holistic') ? 'holistic' : 'selective';
}
function loadRuntimeManifest(mode) {
    const filename = `analyze-${mode}-v1.json`;
    for (const root of augurRootCandidates()) {
        const path = join(root, 'bundles', 'runtime', filename);
        const text = readCached(path);
        if (!text)
            continue;
        try {
            return { root, manifest: JSON.parse(text) };
        }
        catch {
            continue;
        }
    }
    return undefined;
}
function loadAugurBundlePrefix(message) {
    const resolved = loadRuntimeManifest(resolveBundleMode(message));
    if (!resolved)
        return '';
    const { root, manifest } = resolved;
    const parts = [];
    const addLayer = (label, relativePath) => {
        if (!relativePath)
            return;
        const path = join(root, relativePath);
        const text = readCached(path)?.trim();
        if (!text)
            return;
        parts.push(`## ${label}\n\n${text}`);
    };
    const order = manifest.composition_order ?? ['skill_bundle', 'memory_bundle', 'detector_plan'];
    for (const layer of order) {
        if (layer === 'repo_context')
            continue;
        if (layer === 'skill_bundle')
            addLayer('Skill Bundle', manifest.skill_bundle);
        if (layer === 'memory_bundle')
            addLayer('Memory Bundle', manifest.memory_bundle);
        if (layer === 'detector_plan')
            addLayer('Detector Plan', manifest.detector_plan);
    }
    return parts.length > 0 ? `${parts.join('\n\n')}\n\n` : '';
}
export function loadAgentProfile(agentName) {
    const identity = loadIdentityMetadata(agentName);
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
        };
    }
    return {
        ...identity,
        defaultReflectionPrompt: DEFAULT_REFLECTION_PROMPT,
        supportedAgentParams: [],
    };
}
export function buildPromptFromProfile(profile, message) {
    const workingDirSuffix = message.working_dir
        ? `\n\nWorking directory hint: focus your work in \`${message.working_dir}\`. Start there unless the task clearly requires files outside it.`
        : '';
    const augurBundlePrefix = profile.supportedAgentParams?.includes('bundle_mode') ? loadAugurBundlePrefix(message) : '';
    if (!profile.promptPrefix) {
        return `${augurBundlePrefix}${message.prompt}${workingDirSuffix}`;
    }
    return `${profile.promptPrefix}\n\n${augurBundlePrefix}${message.prompt}${workingDirSuffix}`;
}
export function resolveReflectionPrompt(profile, message) {
    return message.reflection_prompt ?? profile.defaultReflectionPrompt ?? DEFAULT_REFLECTION_PROMPT;
}
