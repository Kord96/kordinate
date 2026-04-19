import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const DEFAULT_REFLECTION_PROMPT = [
    'Based on the completed task, return strict JSON only with exactly these keys:',
    '{"project":"...","general":"..."}',
    'project: lessons specific to the current project/repo/context.',
    'general: lessons that transfer to any project.',
    'Use strings only. If there is no strong lesson for a key, return an empty string.',
].join('\n');
const moduleDir = dirname(fileURLToPath(import.meta.url));
const bundleTextCache = new Map();
function parseJsonEnv(name) {
    const raw = process.env[name];
    if (!raw || !raw.trim()) {
        throw new Error(`${name} required`);
    }
    return JSON.parse(raw);
}
function readCached(path) {
    if (bundleTextCache.has(path))
        return bundleTextCache.get(path);
    if (!existsSync(path))
        return undefined;
    const text = readFileSync(path, 'utf8');
    bundleTextCache.set(path, text);
    return text;
}
function agentRootCandidates(agentName) {
    return [
        join('/app/agents', agentName),
        join(moduleDir, '..', '..', '..', 'agents', agentName),
    ];
}
function resolveRepoBundleFile(agentName, dir, selection) {
    if (!selection)
        return undefined;
    const exts = ['', '.md', '.json', '.yaml', '.yml'];
    for (const root of agentRootCandidates(agentName)) {
        const bundleDirs = [join(root, '.generated', 'bundles', dir), join(root, 'bundles', dir)];
        for (const bundleDir of bundleDirs) {
            if (!existsSync(bundleDir))
                continue;
            for (const ext of exts) {
                const candidate = join(bundleDir, `${selection}${ext}`);
                if (existsSync(candidate))
                    return candidate;
            }
        }
    }
    return undefined;
}
function applyBundleModeSelection(selection, bundleMode, dir) {
    if (!selection)
        return selection;
    if (dir !== 'memory' && dir !== 'runtime')
        return selection;
    return selection
        .replace('analyze-selective-', `analyze-${bundleMode}-`)
        .replace('analyze-holistic-', `analyze-${bundleMode}-`);
}
function loadRepoBundlePrefix(contract, bundleMode) {
    const layers = [
        { label: 'Skill Bundle', dir: 'skill', selection: contract.bundleRefs?.skill },
        { label: 'Memory Bundle', dir: 'memory', selection: applyBundleModeSelection(contract.bundleRefs?.memory, bundleMode, 'memory') },
        { label: 'Runtime Bundle', dir: 'runtime', selection: applyBundleModeSelection(contract.bundleRefs?.runtime, bundleMode, 'runtime') },
    ];
    const parts = layers.flatMap(layer => {
        const path = resolveRepoBundleFile(contract.specialization, layer.dir, layer.selection);
        const text = path ? readCached(path)?.trim() : undefined;
        return text ? [`## ${layer.label}\n\n${text}`] : [];
    });
    return parts.length > 0 ? `${parts.join('\n\n')}\n\n` : '';
}
function resolveBundleMode(message) {
    const analysisMode = typeof message.agent_params?.analysis_mode === 'string'
        ? message.agent_params.analysis_mode.trim().toLowerCase()
        : '';
    const raw = String(message.agent_params?.bundle_mode ?? 'auto').toLowerCase();
    if (raw.includes('holistic')
        || raw.includes('full-bundle')
        || raw === 'full'
        || raw === 'opus-full') {
        return 'holistic';
    }
    if (raw && raw !== 'auto' && raw !== 'default') {
        return 'selective';
    }
    if (analysisMode === 'incremental') {
        return 'selective';
    }
    if (analysisMode === 'full') {
        return 'holistic';
    }
    return 'selective';
}
function loadPromptContext(contract, message) {
    const scriptPath = contract.workflow?.promptContextScript;
    if (!scriptPath)
        return undefined;
    const mode = typeof message.agent_params?.analysis_mode === 'string'
        ? message.agent_params.analysis_mode.trim()
        : '';
    try {
        const payload = execFileSync('python3', [
            scriptPath,
            '--bundle-mode', resolveBundleMode(message),
            '--analysis-mode', mode,
        ], {
            encoding: 'utf8',
        }).trim();
        return JSON.parse(payload);
    }
    catch {
        return undefined;
    }
}
function renderStartupGuidance(agentParams) {
    const guidance = agentParams?.startup_guidance;
    if (!guidance || typeof guidance !== 'object' || Array.isArray(guidance))
        return '';
    const guidanceRecord = guidance;
    const directive = typeof guidanceRecord.directive === 'string' ? guidanceRecord.directive.trim() : '';
    const starterFiles = Array.isArray(guidanceRecord.starter_files)
        ? guidanceRecord.starter_files.filter((value) => typeof value === 'string' && value.trim().length > 0)
        : [];
    const parts = [];
    if (directive)
        parts.push(`Directive: ${directive}`);
    if (starterFiles.length > 0) {
        parts.push('Starter artifacts:');
        parts.push(...starterFiles.map(path => `- \`${path}\``));
    }
    return parts.length > 0 ? `## Startup Guidance\n\n${parts.join('\n')}\n\n` : '';
}
function renderRuntimeContext(agentContract, message, runtimeProfile) {
    const workspace = message.workspace;
    const agent = message.agent;
    const requestedBundleMode = typeof message.agent_params?.bundle_mode === 'string'
        ? resolveBundleMode(message)
        : undefined;
    const toolGuidance = runtimeProfile.toolGuidance ?? [];
    const runArtifactGuidance = runtimeProfile.runArtifactGuidance ?? [];
    if (workspace && typeof workspace.working_dir === 'string' && typeof workspace.output_dir === 'string') {
        const lines = [];
        lines.push(`- Working directory: \`${workspace.working_dir}\``);
        lines.push(`- Output directory: \`${workspace.output_dir}\``);
        if (typeof agent?.root_dir === 'string' && agent.root_dir.trim()) {
            lines.push(`- Agent root: \`${agent.root_dir.trim()}\``);
        }
        if (typeof agent?.validator_script === 'string' && agent.validator_script.trim()) {
            lines.push(`- Validator script: \`${agent.validator_script.trim()}\``);
        }
        if (typeof agent?.concept_catalog_index === 'string' && agent.concept_catalog_index.trim()) {
            lines.push(`- Concept catalog entrypoint: \`${agent.concept_catalog_index.trim()}\``);
        }
        if (typeof agent?.framework_catalog_index === 'string' && agent.framework_catalog_index.trim()) {
            lines.push(`- Framework catalog entrypoint: \`${agent.framework_catalog_index.trim()}\``);
        }
        if (requestedBundleMode) {
            lines.push(`- Bundle mode: \`${requestedBundleMode}\``);
        }
        lines.push('- Start in the working directory and treat it as the authoritative repo root for analysis and edits.');
        lines.push('- Generated artifacts belong in the output directory.');
        lines.push('- Use the provided validator path and catalog entrypoints directly instead of discovering alternate internal paths.');
        lines.push('- Use the prepared run artifacts under the output directory for startup orientation before broad repo reading.');
        lines.push('- Treat `facts/startup.json` and `facts/index.json` under the output directory as the authoritative manifest for prepared deterministic fact domains in this run.');
        lines.push('- Use the agent root as the stable base for agent-owned resources and the provided catalog entrypoints for on-demand concept/framework reads.');
        lines.push('- Use deterministic artifacts for startup orientation first, then move into repo code for the main architectural synthesis.');
        lines.push('- Revisit larger supporting fact domains only when they help resolve ambiguity, answer semantic questions, or confirm concepts.');
        lines.push('- Read repo code through fact-selected files, architecture entrypoints, adjacent implementation, or concrete validation gaps.');
        lines.push('- Do not begin with repo-root listings or metadata-file discovery.');
        lines.push('- Follow the runtime-harness tool schema directly instead of assuming specific tool names from prior runs or other runtimes.');
        for (const guidance of toolGuidance) {
            lines.push(`- ${guidance}`);
        }
        for (const guidance of runArtifactGuidance) {
            lines.push(`- ${guidance}`);
        }
        return `## Runtime Context\n${lines.join('\n')}\n\n`;
    }
    const runtimeHints = [];
    if (message.working_dir) {
        runtimeHints.push(`Working directory hint: use \`${message.working_dir}\` as the authoritative starting project root and current working directory.`);
    }
    const runDir = typeof message.agent_params?.run_dir === 'string' && message.agent_params.run_dir.trim()
        ? message.agent_params.run_dir.trim()
        : '';
    if (runDir) {
        runtimeHints.push(`Prepared analysis run: use \`${runDir}\` as the authoritative output directory for this request.`);
        runtimeHints.push(`Start with \`${runDir}/blast.json\` and \`${runDir}/facts/\` for prepared run artifacts.`);
    }
    if (requestedBundleMode) {
        runtimeHints.push(`Bundle mode hint: use \`${requestedBundleMode}\` prompt preload assumptions for this request.`);
    }
    runtimeHints.push(...toolGuidance);
    runtimeHints.push(...runArtifactGuidance);
    return runtimeHints.length > 0
        ? `## Runtime Context\n${runtimeHints.map(line => `- ${line}`).join('\n')}\n\n`
        : '';
}
function hashPromptPrefix(value) {
    return createHash('sha256').update(value).digest('hex');
}
export function loadInjectedAgentContract(expectedAgentName) {
    const contract = parseJsonEnv('AGENT_CONTRACT_JSON');
    if (contract.name !== expectedAgentName) {
        throw new Error(`AGENT_CONTRACT_JSON name mismatch: expected ${expectedAgentName}, got ${contract.name}`);
    }
    return contract;
}
export function loadInjectedRuntimeProfile() {
    return parseJsonEnv('RUNTIME_PROFILE_JSON');
}
export function buildPromptPlan(agentContract, runtimeProfile, message) {
    const runtimePreamble = runtimeProfile.promptPreamble?.trim()
        ? `${runtimeProfile.promptPreamble.trim()}\n\n`
        : '';
    const runtimeContext = renderRuntimeContext(agentContract, message, runtimeProfile);
    const startupGuidance = renderStartupGuidance(message.agent_params);
    const resolvedBundleMode = resolveBundleMode(message);
    const promptContext = loadPromptContext(agentContract, message);
    const bundlePrefix = promptContext?.bundle_prefix ?? loadRepoBundlePrefix(agentContract, resolvedBundleMode);
    const bundleModeGuide = promptContext?.bundle_mode_guide ?? '';
    const modeGuide = promptContext?.mode_guide ?? '';
    const cacheablePrefix = agentContract.promptPrefix || bundlePrefix
        ? `${agentContract.promptPrefix ? `${agentContract.promptPrefix}\n\n` : ''}${bundlePrefix}`
        : '';
    const dynamicPrompt = `${runtimePreamble}${runtimeContext}${startupGuidance}${bundleModeGuide}${modeGuide}${message.prompt}`;
    const fullPrompt = cacheablePrefix
        ? `${cacheablePrefix}${dynamicPrompt}`
        : dynamicPrompt;
    return {
        fullPrompt,
        dynamicPrompt,
        cacheablePrefix: cacheablePrefix || undefined,
        cacheKey: cacheablePrefix ? hashPromptPrefix(cacheablePrefix) : undefined,
        cacheStrategy: cacheablePrefix ? 'provider' : undefined,
    };
}
export function buildPrompt(agentContract, runtimeProfile, message) {
    return buildPromptPlan(agentContract, runtimeProfile, message).fullPrompt;
}
export function resolveReflectionPrompt(agentContract, message) {
    return message.reflection_prompt ?? agentContract.defaultReflectionPrompt ?? DEFAULT_REFLECTION_PROMPT;
}
