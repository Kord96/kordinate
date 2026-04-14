import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { basename, dirname, join } from 'node:path';
import { constants as fsConstants } from 'node:fs';
import { access, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
async function pathExists(path) {
    try {
        await access(path, fsConstants.F_OK);
        return true;
    }
    catch {
        return false;
    }
}
async function removePathIfExists(target) {
    await rm(target, { recursive: true, force: true });
}
function requestCommandText(message) {
    return typeof message.raw_prompt === 'string' && message.raw_prompt.trim()
        ? message.raw_prompt
        : message.prompt;
}
function gitArgsForRepo(repoPath, ...gitArgs) {
    return ['-c', `safe.directory=${repoPath}`, '-C', repoPath, ...gitArgs];
}
function correlationSuffix(message) {
    const raw = typeof message.correlation_id === 'string' ? message.correlation_id.trim() : '';
    if (!raw)
        return 'run';
    const safe = raw.replace(/[^a-zA-Z0-9_-]+/g, '-');
    return safe.slice(-12) || 'run';
}
async function runCommand(command, args, cwd, extraEnv) {
    return await new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            cwd,
            env: {
                ...process.env,
                ...(extraEnv ?? {}),
            },
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        let stdout = '';
        let stderr = '';
        child.stdout.on('data', chunk => { stdout += String(chunk); });
        child.stderr.on('data', chunk => { stderr += String(chunk); });
        child.on('close', code => {
            if (code === 0) {
                resolve(stdout.trim());
                return;
            }
            reject(new Error(`${command} ${args.join(' ')} failed with code ${code}: ${(stderr || stdout).trim()}`));
        });
    });
}
async function runRequiredCommand(command, args, cwd, extraEnv) {
    await runCommand(command, args, cwd, extraEnv);
}
function isAugurAnalyzeRequest(context, message) {
    const commandText = requestCommandText(message);
    return context.agentProfileName === 'augur'
        && commandText.trim().startsWith('/analyze')
        && typeof message.working_dir === 'string'
        && message.working_dir.length > 0;
}
function isAugurDeterministicOnlyRequest(context, message) {
    const commandText = requestCommandText(message);
    return isAugurAnalyzeRequest(context, message) && commandText.includes('--deterministic-only');
}
function isForceFullAugurAnalyzeRequest(context, message) {
    const commandText = requestCommandText(message);
    return isAugurAnalyzeRequest(context, message) && commandText.includes('--full');
}
async function computeAugurBlastManifest(context, message) {
    const workingDir = message.working_dir;
    const agentHome = context.daemonConfig.executionProfile.homeDirectory;
    if (!workingDir || !agentHome) {
        throw new Error('working_dir and agent home are required for Augur analysis');
    }
    const project = basename(workingDir);
    const kordHome = process.env.KORDINATE_HOME ?? '/app';
    const payload = await runCommand('python3', [
        join(kordHome, 'agents', 'augur', 'scripts', 'compute_blast_radius.py'),
        workingDir,
        '--agent-home', agentHome,
        '--project', project,
    ], agentHome);
    if (!payload) {
        throw new Error('compute_blast_radius.py did not return a manifest');
    }
    return JSON.parse(payload);
}
async function isAcceptedAugurSemanticAnalysisDir(targetDir) {
    const metaPath = join(targetDir, 'meta.json');
    const atlasPath = join(targetDir, 'atlas.json');
    const storiesDir = join(targetDir, 'stories');
    const narrativesPath = join(targetDir, 'narratives.yaml');
    if (!(await pathExists(metaPath)))
        return false;
    if (!(await pathExists(atlasPath)))
        return false;
    if (!(await pathExists(storiesDir)))
        return false;
    if (!(await pathExists(narrativesPath)))
        return false;
    try {
        const meta = JSON.parse(await readFile(metaPath, 'utf8'));
        return meta.validation?.passed === true;
    }
    catch {
        return false;
    }
}
async function resolveAcceptedAugurLatestAnalysisDir(agentHome, project) {
    const latestPath = join(agentHome, 'memory', 'projects', project, 'analysis', 'latest.json');
    if (!(await pathExists(latestPath)))
        return undefined;
    try {
        const latest = JSON.parse(await readFile(latestPath, 'utf8'));
        const analysisDir = typeof latest.analysis_dir === 'string' && latest.analysis_dir.trim()
            ? latest.analysis_dir.trim()
            : undefined;
        if (!analysisDir)
            return undefined;
        if (!(await isAcceptedAugurSemanticAnalysisDir(analysisDir)))
            return undefined;
        return analysisDir;
    }
    catch {
        return undefined;
    }
}
async function hashValidatedDirectory(root) {
    const hash = createHash('sha256');
    async function walk(dir, relativePrefix = '') {
        const { readdir } = await import('node:fs/promises');
        const entries = (await readdir(dir, { withFileTypes: true }))
            .filter(entry => entry.name !== '.validate-lock')
            .sort((a, b) => a.name.localeCompare(b.name));
        for (const entry of entries) {
            const absolutePath = join(dir, entry.name);
            const relativePath = relativePrefix ? `${relativePrefix}/${entry.name}` : entry.name;
            if (entry.isDirectory()) {
                hash.update(`dir:${relativePath}\n`);
                await walk(absolutePath, relativePath);
            }
            else if (entry.isFile()) {
                hash.update(`file:${relativePath}\n`);
                hash.update(await readFile(absolutePath));
                hash.update('\n');
            }
        }
    }
    await walk(root);
    return hash.digest('hex');
}
async function prepareAugurDeterministicArtifacts(context, message, options) {
    const workingDir = message.working_dir;
    const agentHome = context.daemonConfig.executionProfile.homeDirectory;
    if (!workingDir || !agentHome) {
        throw new Error('working_dir and agent home are required for Augur deterministic preparation');
    }
    const project = basename(workingDir);
    const kordHome = process.env.KORDINATE_HOME ?? '/app';
    const currentSha = await runCommand('git', gitArgsForRepo(workingDir, 'rev-parse', 'HEAD'), agentHome);
    const commitTime = currentSha
        ? await runCommand('git', gitArgsForRepo(workingDir, 'show', '-s', '--format=%ct', currentSha), agentHome)
        : undefined;
    if (!currentSha || !commitTime) {
        throw new Error('could not resolve git HEAD for Augur deterministic preparation');
    }
    const runId = `${commitTime}-${currentSha.slice(0, 40)}-${correlationSuffix(message)}`;
    const runDir = join(agentHome, 'memory', 'projects', project, 'analysis', runId);
    const factsDir = join(runDir, 'facts');
    const env = {
        KORDINATE_HOME: kordHome,
        AGENT_HOME_DIR: agentHome,
        ROOT: workingDir,
        PROJECT: project,
        RUN: runDir,
    };
    if (options?.clearSemanticOutputs) {
        await removePathIfExists(runDir);
    }
    await mkdir(factsDir, { recursive: true });
    const eventKindPrefix = options?.eventKindPrefix ?? 'augur.deterministic_prepare';
    await context.publishProgress(message, {
        source: 'agent-daemon',
        kind: `${eventKindPrefix}.start`,
        payload: { project, working_dir: workingDir, run_dir: runDir },
    });
    await runRequiredCommand('python3', [
        join(kordHome, 'agents', 'augur', 'scripts', 'compute_blast_radius.py'),
        workingDir,
        '--agent-home', agentHome,
        '--project', project,
        '--current-sha', currentSha,
        '--output', join(runDir, 'blast.json'),
    ], agentHome, env);
    const blastPath = join(runDir, 'blast.json');
    try {
        const blast = JSON.parse(await readFile(blastPath, 'utf8'));
        if (options?.forcedBlastMode) {
            blast.mode = options.forcedBlastMode;
            const existingReasons = Array.isArray(blast.reasons)
                ? blast.reasons.map(reason => String(reason))
                : [];
            blast.reasons = Array.from(new Set([...existingReasons, `forced-${options.forcedBlastMode}`]));
        }
        blast.analysis_dir = runDir;
        await writeFile(blastPath, `${JSON.stringify(blast, null, 2)}\n`, 'utf8');
    }
    catch {
        // Leave the original blast file untouched if rewrite fails; validation will surface it later.
    }
    await runRequiredCommand('python3', [
        join(kordHome, 'agents', 'augur', 'scripts', 'detect_frameworks.py'),
        workingDir,
        '--project', project,
        '--agent-home', agentHome,
        '--output', join(factsDir, 'frameworks.json'),
        '--pretty',
    ], agentHome, env);
    await runRequiredCommand('python3', [
        join(kordHome, 'agents', 'augur', 'scripts', 'extract_facts.py'),
        workingDir,
        '--output-dir', factsDir,
        '--analysis-mode', 'full',
        '--pretty',
    ], agentHome, env);
    await runRequiredCommand('python3', [
        join(kordHome, 'agents', 'augur', 'scripts', 'infer_concepts_from_facts.py'),
        factsDir,
        '--output', join(factsDir, 'concept-evidence.json'),
    ], agentHome, env);
    await context.publishProgress(message, {
        source: 'agent-daemon',
        kind: `${eventKindPrefix}.complete`,
        payload: { run_dir: runDir },
    });
    return { project, runDir };
}
function buildAugurAnalysisContext(workingDir, project, runDir, analysisMode) {
    const analysisDir = dirname(runDir);
    const projectMem = dirname(analysisDir);
    const factsDir = join(runDir, 'facts');
    const startupPath = join(factsDir, 'startup.json');
    const blastPath = join(runDir, 'blast.json');
    const conceptEvidencePath = join(factsDir, 'concept-evidence.json');
    const atlasPath = join(runDir, 'atlas.json');
    const starterFiles = [
        blastPath,
        startupPath,
        join(factsDir, 'frameworks.json'),
        join(factsDir, 'boundaries.json'),
        join(factsDir, 'dispatch-bindings.json'),
        join(factsDir, 'hot-files.json'),
    ];
    const startupDirective = analysisMode === 'incremental'
        ? [
            'Begin with the prepared analysis artifacts, not generic repo orientation.',
            'Read starter_files first and treat facts/startup.json as the startup manifest for follow-up fact selection.',
            'Expand into repo code only through fact-selected files, hot files, architecture entrypoints, or concrete validation gaps.',
            'Use hot-files.json and fact source_files to rank what code to inspect next.',
            'Preserve unchanged accepted outputs unless blast evidence forces wider revision.',
            'When you need schemas, use the exact canonical files under /app/agents/augur/schemas/.',
            'Available tools are Read, Edit, and Bash. Use Bash with find, rg, jq, or python for discovery or filtering; do not assume Glob or Grep tools exist.',
        ].join(' ')
        : [
            'Begin with the prepared analysis artifacts, not generic repo orientation.',
            'Read starter_files first and treat facts/startup.json as the startup manifest for follow-up fact selection.',
            'Expand into repo code only through fact-selected files, hot files, architecture entrypoints, or concrete validation gaps.',
            'Use hot-files.json and fact source_files to rank what code to inspect next.',
            'Do not read large domains like concept-evidence.json, external-clients.json, config.json, or import-graph.json in full before narrowing them by component, concept, or hotspot.',
            'Before atlas.json exists, only inspect those large domains through filtered queries keyed by component_ids, source_files, concept ids, or hotspot paths.',
            'Do not begin by listing the repo root or reading repo metadata files.',
            'Follow the already-loaded Augur skill, mode guide, and canonical schema files instead of guessing alternate paths or formats.',
            'When you need schemas, use the exact canonical files under /app/agents/augur/schemas/.',
            'Available tools are Read, Edit, and Bash. Use Bash with find, rg, jq, or python for discovery or filtering; do not assume Glob or Grep tools exist.',
        ].join(' ');
    return {
        project,
        mode: analysisMode,
        working_dir: workingDir,
        run_dir: runDir,
        analysis_dir: analysisDir,
        project_mem: projectMem,
        facts_dir: factsDir,
        startup_path: startupPath,
        blast_path: blastPath,
        concept_evidence_path: conceptEvidencePath,
        atlas_path: atlasPath,
        latest_path: join(analysisDir, 'latest.json'),
        starter_files: starterFiles,
        startup_directive: startupDirective,
    };
}
function buildAugurValidationRepairPrompt(input) {
    const findings = input.findings.map(line => `- ${line}`).join('\n');
    return [
        `Validation failed for \`${input.targetDir}\`.`,
        'You must fix the generated output in place and obtain a validation completion token before finishing.',
        `Validator: \`${input.validatorScript}\``,
        `Attempt ${input.attempt} of ${input.maxAttempts}.`,
        '',
        'Current validator findings:',
        findings || '- Validation failed with no structured findings.',
        '',
        'Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.',
        `Do not call \`/validate-output\` as a shell command. If you need to validate manually inside the runtime, run \`python3 ${input.validatorScript} ${input.targetDir}\`.`,
        'Re-read the canonical schema files and fix the output to match them exactly:',
        '- `/app/agents/augur/schemas/atlas-schema.md`',
        '- `/app/agents/augur/schemas/story-schema.md`',
        '- `/app/agents/augur/schemas/narratives-schema.md`',
    ].join('\n');
}
function createAugurWorkflowHooks(context) {
    return {
        async beforeRuntime(message) {
            if (!isAugurAnalyzeRequest(context, message))
                return undefined;
            if (isAugurDeterministicOnlyRequest(context, message)) {
                const workingDir = message.working_dir;
                const agentHome = context.daemonConfig.executionProfile.homeDirectory;
                if (!workingDir || !agentHome) {
                    return {
                        skipResult: {
                            status: 'error',
                            output: 'working_dir and agent home are required for Augur deterministic-only',
                            errors: ['working_dir and agent home are required for Augur deterministic-only'],
                        },
                    };
                }
                const prepared = await prepareAugurDeterministicArtifacts(context, message, {
                    clearSemanticOutputs: true,
                    eventKindPrefix: 'augur.deterministic_only',
                });
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
                };
            }
            let analysisMode = 'full';
            if (!isForceFullAugurAnalyzeRequest(context, message)) {
                const blast = await computeAugurBlastManifest(context, message);
                analysisMode = blast.mode === 'incremental' ? 'incremental' : 'full';
                if (blast.mode === 'skip') {
                    const targetDir = typeof blast.base_analysis_dir === 'string' && blast.base_analysis_dir.trim()
                        ? blast.base_analysis_dir.trim()
                        : undefined;
                    const agentHome = context.daemonConfig.executionProfile.homeDirectory;
                    const workingDir = message.working_dir;
                    const project = workingDir ? basename(workingDir) : undefined;
                    const acceptedLatestDir = agentHome && project
                        ? await resolveAcceptedAugurLatestAnalysisDir(agentHome, project)
                        : undefined;
                    if (!targetDir || !(await pathExists(targetDir)) || !acceptedLatestDir || acceptedLatestDir !== targetDir) {
                        throw new Error('blast reported skip but no accepted latest semantic analysis directory was available');
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
                    });
                    const token = await hashValidatedDirectory(targetDir);
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
                    };
                }
            }
            const prepared = await prepareAugurDeterministicArtifacts(context, message, {
                clearSemanticOutputs: true,
                eventKindPrefix: 'augur.semantic_prepare',
                forcedBlastMode: analysisMode,
            });
            const workingDir = message.working_dir;
            if (!workingDir) {
                throw new Error('working_dir is required for Augur semantic preparation');
            }
            const analysisContext = buildAugurAnalysisContext(workingDir, prepared.project, prepared.runDir, analysisMode);
            return {
                runtimeMessage: {
                    ...message,
                    agent_params: {
                        ...(message.agent_params ?? {}),
                        run_dir: prepared.runDir,
                        analysis_mode: analysisMode,
                        analysis_context: analysisContext,
                        startup_guidance: {
                            directive: analysisContext.startup_directive,
                            starter_files: analysisContext.starter_files,
                        },
                    },
                },
            };
        },
        async validationContext(message) {
            if (!isAugurAnalyzeRequest(context, message))
                return undefined;
            const workingDir = message.working_dir;
            const agentHome = context.daemonConfig.executionProfile.homeDirectory;
            if (!workingDir || !agentHome)
                return undefined;
            const project = basename(workingDir);
            const latestDir = await resolveAcceptedAugurLatestAnalysisDir(agentHome, project);
            const explicitRunDir = typeof message.agent_params?.run_dir === 'string' && message.agent_params.run_dir.trim()
                ? message.agent_params.run_dir.trim()
                : undefined;
            return {
                targetDir: explicitRunDir ?? latestDir,
                extraEnv: {
                    ...(requestCommandText(message).includes('--deterministic-only')
                        ? { AUGUR_DETERMINISTIC_ONLY: '1' }
                        : {}),
                    AUGUR_PROJECT_ROOT: workingDir,
                },
                repairPromptBuilder: buildAugurValidationRepairPrompt,
            };
        },
    };
}
export function createAgentWorkflowHooks(context) {
    if (context.agentProfileName === 'augur') {
        return createAugurWorkflowHooks(context);
    }
    return undefined;
}
