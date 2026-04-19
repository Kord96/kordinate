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
    const analysisContext = message.agent_params?.analysis_context;
    const requestedBundleMode = typeof message.agent_params?.bundle_mode === 'string'
        ? resolveBundleMode(message)
        : undefined;
    const toolGuidance = runtimeProfile.toolGuidance ?? [];
    const runArtifactGuidance = runtimeProfile.runArtifactGuidance ?? [];
    if (analysisContext && typeof analysisContext === 'object' && !Array.isArray(analysisContext)) {
        const context = analysisContext;
        const lines = [];
        const pushLine = (label, value) => {
            if (typeof value === 'string' && value.trim())
                lines.push(`- ${label}: \`${value.trim()}\``);
        };
        pushLine('Mode', context.mode);
        pushLine('Run dir', context.run_dir);
        pushLine('Facts dir', context.facts_dir);
        pushLine('Startup manifest', context.startup_path);
        pushLine('Blast file', context.blast_path);
        pushLine('Atlas output path', context.atlas_path);
        pushLine('Stories output dir', context.stories_dir);
        pushLine('Narratives output path', context.narratives_path);
        pushLine('Meta output path', context.meta_path);
        pushLine('Grounding summary path', context.grounding_summary_path);
        pushLine('Write handoff path', context.write_handoff_path);
        if (typeof agentContract.validation?.validatorScript === 'string' && agentContract.validation.validatorScript.trim()) {
            lines.push(`- Validator script: \`${agentContract.validation.validatorScript.trim()}\``);
        }
        if (typeof agentContract.validation?.finalizeScript === 'string' && agentContract.validation.finalizeScript.trim()) {
            lines.push(`- Finalize script: \`${agentContract.validation.finalizeScript.trim()}\``);
        }
        if (requestedBundleMode) {
            lines.push(`- Bundle mode: \`${requestedBundleMode}\``);
        }
        lines.push('- Shell environment already provides `KORDINATE_HOME`, `RUN`, `ANALYSIS`, and `PROJECT_MEM` for this request.');
        lines.push('- Use those exact variables in Bash commands instead of retyping long absolute paths.');
        lines.push('- Never invent or rewrite sibling run directories. Write outputs only under the exact `Run dir` above.');
        lines.push('- The canonical semantic output targets for this request are the exact `Atlas output path`, `Stories output dir`, `Narratives output path`, and `Meta output path` listed above.');
        lines.push('- Start from the prepared run artifacts above before reading repo code.');
        lines.push('- Treat the prepared run dir above as the authoritative home for generated artifacts such as `facts/*`, `atlas.json`, `stories/`, `narratives.yaml`, and `meta.json`.');
        lines.push('- Use `facts/startup.json` and `facts/index.json` as the authoritative manifest for which deterministic fact domains exist in this run.');
        lines.push('- Use deterministic artifacts for startup orientation first, then move into repo code for the main architectural synthesis.');
        lines.push('- Revisit larger supporting fact domains only when they help resolve ambiguity, answer semantic questions, or confirm concepts.');
        lines.push('- Read repo code through fact-selected files, architecture entrypoints, adjacent implementation, or concrete validation gaps.');
        lines.push('- Do not begin with repo-root listings or metadata-file discovery.');
        if (context.execution_strategy === 'staged-weak') {
            lines.push('- Execution strategy: `staged-weak`.');
            lines.push('- Breadth reading is allowed until you are sufficiently grounded.');
            lines.push('- Once grounded, stop broad repo exploration and update the exact `Grounding summary path` above.');
            lines.push('- After any compaction, re-read the `Write handoff path`, the `Grounding summary path`, starter facts, and schema files before doing new repo reads.');
            lines.push('- In staged-weak mode, write artifacts in this order: atlas, stories, narratives, then finalize.');
            lines.push('- Do not return to broad repo exploration after switching into write mode unless validation identifies a specific grounding gap.');
        }
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
        runtimeHints.push(`Prepared analysis run: use \`${runDir}\` as the authoritative semantic analysis directory for this request.`);
        runtimeHints.push(`Start with \`${runDir}/blast.json\` and \`${runDir}/facts/\`.`);
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
