import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { basename, join } from 'node:path';
import { constants as fsConstants } from 'node:fs';
import { access, readdir, readFile, rm } from 'node:fs/promises';
import { createServer } from 'node:http';
import { Kafka } from 'kafkajs';
import { createAgentWorkflowHooks } from './workflows/index.js';
import { buildPromptPlan, loadInjectedAgentContract, loadInjectedRuntimeProfile } from './contracts.js';
import { CompletedRequestStore } from './completed-request-store.js';
import { loadDaemonConfig } from './config.js';
import { buildDiscoveryRecord, publishDiscoveryRegistration } from './discovery.js';
import { log } from './log.js';
import { buildProgressMessage, buildReflectionEvent, buildResponseMessage, getOrCreateSession, isRequestMessage, updateSessionAfterRequest } from './protocol.js';
import { createProviderAdapter } from './runtime.js';
import { SessionStore } from './session-store.js';
const agentName = process.env.AGENT_NAME;
if (!agentName) {
    throw new Error('AGENT_NAME required');
}
const AGENT_NAME = agentName;
const daemonConfig = loadDaemonConfig();
const agentContract = loadInjectedAgentContract(AGENT_NAME);
const runtimeProfile = loadInjectedRuntimeProfile();
const kafka = new Kafka({
    clientId: `klaude-daemon-${AGENT_NAME}`,
    brokers: daemonConfig.kafkaBrokers,
});
const consumerGroupId = daemonConfig.kafkaConsumerGroupId ?? `klaude-daemon.${AGENT_NAME}`;
const consumer = kafka.consumer({
    groupId: consumerGroupId,
    sessionTimeout: daemonConfig.kafkaSessionTimeoutMs,
    heartbeatInterval: daemonConfig.kafkaHeartbeatIntervalMs,
});
const producer = kafka.producer();
const runtime = createProviderAdapter(daemonConfig.executionProfile);
const sessionStore = new SessionStore(daemonConfig.sessionMapPath);
const sessions = await sessionStore.load();
const completedRequestStore = new CompletedRequestStore(daemonConfig.sessionMapPath.replace(/sessions\.json$/, 'completed-requests.json'));
const completedRequests = await completedRequestStore.load();
const healthPort = Number.parseInt(process.env.DAEMON_HEALTH_PORT ?? '9090', 10);
const healthUrl = daemonConfig.healthUrl ?? `http://127.0.0.1:${healthPort}/health`;
let daemonReady = false;
let discoveryHeartbeat;
const healthServer = createServer((_req, res) => {
    res.statusCode = daemonReady ? 200 : 503;
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify({ ok: daemonReady, agent: AGENT_NAME }));
});
const agentWorkflowHooks = createAgentWorkflowHooks({
    agentName: AGENT_NAME,
    agentContract,
    daemonConfig,
    publishProgress,
    buildArtifactsMetadata,
});
function sessionForMessage(message) {
    const sessionKey = message.session_id ?? message.correlation_id;
    const existed = sessions.has(sessionKey);
    const preparedMessage = {
        ...message,
        session_id: sessionKey,
    };
    const session = getOrCreateSession(sessions, preparedMessage);
    const updated = updateSessionAfterRequest(session, message);
    sessions.set(updated.key, updated);
    log('session_selected', {
        agent: AGENT_NAME,
        sender: message.sender,
        correlation_id: message.correlation_id,
        working_dir: message.working_dir ?? null,
        session_id: message.session_id ?? null,
        session_key: sessionKey,
        reused: existed,
    });
    return updated;
}
async function persistSessions() {
    await sessionStore.save(sessions);
}
async function persistCompletedRequests() {
    await completedRequestStore.save(completedRequests);
}
function hasCompletedRequest(correlationId) {
    return completedRequests.has(correlationId);
}
function markCompletedRequest(correlationId, status) {
    completedRequests.set(correlationId, {
        correlation_id: correlationId,
        completed_at: nowIso(),
        status,
    });
}
async function publishResponse(message, response) {
    const payload = buildResponseMessage(AGENT_NAME, message, response);
    log('response_publish_start', {
        agent: AGENT_NAME,
        reply_topic: message.sender,
        correlation_id: message.correlation_id,
        status: response.status,
    });
    await producer.send({
        topic: message.sender,
        messages: [{ key: message.correlation_id, value: JSON.stringify(payload) }],
    });
    log('response_publish_complete', {
        agent: AGENT_NAME,
        reply_topic: message.sender,
        correlation_id: message.correlation_id,
        status: response.status,
    });
}
async function publishReflection(message, reflection) {
    const payload = buildReflectionEvent({
        agentName: AGENT_NAME,
        agentProfile: agentContract.specialization,
        backendProvider: daemonConfig.executionProfile.provider,
        backendRuntime: daemonConfig.executionProfile.runtime,
        backendModel: daemonConfig.executionProfile.model,
        message,
        reflection,
    });
    await producer.send({
        topic: daemonConfig.reflectionsTopic,
        messages: [{ key: message.correlation_id, value: JSON.stringify(payload) }],
    });
}
async function publishProgress(message, event) {
    const payload = buildProgressMessage(AGENT_NAME, message, event);
    await producer.send({
        topic: daemonConfig.progressTopic,
        messages: [{ key: message.correlation_id, value: JSON.stringify(payload) }],
    });
}
function nowIso() {
    return new Date().toISOString();
}
function redactExecutionProfile(profile) {
    return {
        ...profile,
        apiKey: profile.apiKey ? '[redacted]' : undefined,
    };
}
function buildTimingMetadata(input) {
    return {
        received_at: new Date(input.gatewayReceivedAt).toISOString(),
        started_at: new Date(input.daemonStartedAt).toISOString(),
        completed_at: new Date(input.daemonCompletedAt).toISOString(),
        total_ms: Math.max(0, input.daemonCompletedAt - input.gatewayReceivedAt),
        session_prepare_ms: input.executeStartAt - input.daemonStartedAt,
        execute_prompt_ms: input.executeEndAt - input.executeStartAt,
        persist_sessions_ms: input.persistEndAt - input.persistStartAt,
        publish_response_ms: 0,
    };
}
function parseGatewayReceivedAt(rawTimestamp) {
    if (rawTimestamp) {
        const parsed = Number.parseInt(rawTimestamp, 10);
        if (Number.isFinite(parsed) && parsed > 0)
            return parsed;
    }
    return Date.now();
}
function mergeUsageMetadata(left, right) {
    if (!left && !right)
        return undefined;
    return {
        input_tokens: (left?.input_tokens ?? 0) + (right?.input_tokens ?? 0),
        cached_input_tokens: (left?.cached_input_tokens ?? 0) + (right?.cached_input_tokens ?? 0),
        output_tokens: (left?.output_tokens ?? 0) + (right?.output_tokens ?? 0),
        cache_write_tokens: (left?.cache_write_tokens ?? 0) + (right?.cache_write_tokens ?? 0),
        estimated_cost: (left?.estimated_cost ?? 0) + (right?.estimated_cost ?? 0),
    };
}
function buildTelemetryMetadata(input) {
    return {
        request_id: input.requestId,
        status: input.status,
        error: input.error ?? null,
        executor: {
            name: AGENT_NAME,
            specialization: agentContract.specialization,
            provider: daemonConfig.executionProfile.provider,
            model: daemonConfig.executionProfile.model,
        },
        times: {
            gateway_received_at: new Date(input.gatewayReceivedAt).toISOString(),
            daemon_started_at: new Date(input.daemonStartedAt).toISOString(),
            daemon_completed_at: new Date(input.daemonCompletedAt).toISOString(),
        },
        metrics: {
            queue_wait_seconds: Math.max(0, input.daemonStartedAt - input.gatewayReceivedAt) / 1000,
            elapsed_seconds: Math.max(0, input.daemonCompletedAt - input.gatewayReceivedAt) / 1000,
            cpu_time_seconds: (input.cpuUsage.user + input.cpuUsage.system) / 1_000_000,
            peak_rss_mb: input.peakRssBytes / (1024 * 1024),
            input_tokens: input.usage?.input_tokens,
            cached_input_tokens: input.usage?.cached_input_tokens,
            output_tokens: input.usage?.output_tokens,
            estimated_cost_usd: input.usage?.estimated_cost,
        },
    };
}
function logTelemetry(telemetry) {
    log('request_telemetry', telemetry);
}
function validateRequestContract(message) {
    if (agentContract.requiresWorkingDirectory && !message.working_dir) {
        return 'working_dir is required for this agent';
    }
    const acceptedPrefixes = Array.isArray(agentContract.acceptedRequestPrefixes)
        ? agentContract.acceptedRequestPrefixes.filter(prefix => typeof prefix === 'string' && prefix.trim().length > 0)
        : [];
    if (acceptedPrefixes.length > 0) {
        const text = requestCommandText(message).trim();
        if (!acceptedPrefixes.some(prefix => text.startsWith(prefix))) {
            return `request does not match an accepted agent skill/command (${acceptedPrefixes.join(', ')})`;
        }
    }
    return undefined;
}
function buildRuntimePromptRequest(session, message, overrides) {
    const promptMessage = {
        ...message,
        prompt: overrides?.prompt ?? message.prompt,
        raw_prompt: overrides?.rawPrompt ?? message.raw_prompt ?? message.prompt,
    };
    const promptPlan = buildPromptPlan(agentContract, runtimeProfile, promptMessage);
    const prompt = session.promptCacheKey && session.promptCacheKey === promptPlan.cacheKey
        ? promptPlan.dynamicPrompt
        : promptPlan.fullPrompt;
    return {
        prompt,
        raw_prompt: promptMessage.raw_prompt,
        promptPlan,
        working_dir: promptMessage.working_dir,
        timeout_ms: promptMessage.timeout_ms,
        reflect: overrides?.reflect ?? (agentContract.validation?.required ? false : promptMessage.reflect),
        reflection_prompt: promptMessage.reflection_prompt,
        agent_params: promptMessage.agent_params,
        progress: event => publishProgress(message, event),
    };
}
function getWeakModelAnalysisContext(message) {
    const analysisContext = message.agent_params?.analysis_context;
    if (!analysisContext || typeof analysisContext !== 'object' || Array.isArray(analysisContext))
        return undefined;
    const record = analysisContext;
    if (record.execution_strategy !== 'staged-weak')
        return undefined;
    return {
        execution_strategy: 'staged-weak',
        grounding_summary_path: typeof record.grounding_summary_path === 'string' ? record.grounding_summary_path : undefined,
        write_handoff_path: typeof record.write_handoff_path === 'string' ? record.write_handoff_path : undefined,
        startup_path: typeof record.startup_path === 'string' ? record.startup_path : undefined,
        blast_path: typeof record.blast_path === 'string' ? record.blast_path : undefined,
        atlas_path: typeof record.atlas_path === 'string' ? record.atlas_path : undefined,
        run_dir: typeof record.run_dir === 'string' ? record.run_dir : undefined,
    };
}
function buildWeakModelSummaryPassPrompt(message, context) {
    const parts = [
        'You are in weak-model staged analysis pass 1.',
        'Goal: gather enough grounded evidence to fill the grounding summary, then stop.',
        'Breadth reading is allowed while you are still identifying the real architectural shape.',
        'Do not write atlas.json, story YAML files, narratives.yaml, or meta.json in this pass.',
        'Once you are grounded, update the grounding summary file with concrete components, flows, story plan, narrative plan, open questions, and source anchors.',
        'After the grounding summary is updated, stop immediately so a fresh write pass can begin from that summary.',
    ];
    if (context.grounding_summary_path) {
        parts.push(`Grounding summary path: ${context.grounding_summary_path}`);
    }
    if (context.write_handoff_path) {
        parts.push(`Write handoff path: ${context.write_handoff_path}`);
    }
    if (context.blast_path) {
        parts.push(`Blast file: ${context.blast_path}`);
    }
    if (context.startup_path) {
        parts.push(`Startup manifest: ${context.startup_path}`);
    }
    parts.push('', 'Original request:', message.raw_prompt ?? message.prompt);
    return parts.join('\n');
}
function buildWeakModelWritePassPrompt(message, context) {
    const parts = [
        'You are in weak-model staged analysis pass 2.',
        'Goal: write the final Augur artifacts from the grounded synthesis summary.',
        'Start by re-reading the write handoff and grounding summary files.',
        'Use the grounding summary as the primary plan for component set, flows, stories, and narratives.',
        'Write atlas.json, story YAML files, and narratives.yaml now.',
        'Do not return to broad repo exploration in this pass.',
        'Only read an additional repo file if a very specific grounding gap blocks artifact writing.',
        'After artifacts exist, stop and let validation/finalization run.',
    ];
    if (context.write_handoff_path) {
        parts.push(`Write handoff path: ${context.write_handoff_path}`);
    }
    if (context.grounding_summary_path) {
        parts.push(`Grounding summary path: ${context.grounding_summary_path}`);
    }
    if (context.atlas_path) {
        parts.push(`Atlas output path: ${context.atlas_path}`);
    }
    if (context.run_dir) {
        parts.push(`Stories output dir: ${join(context.run_dir, 'stories')}`);
        parts.push(`Narratives output path: ${join(context.run_dir, 'narratives.yaml')}`);
    }
    parts.push('', 'Original request:', message.raw_prompt ?? message.prompt);
    return parts.join('\n');
}
async function readWeakModelGroundingSummary(pathValue) {
    if (!pathValue || !(await pathExists(pathValue)))
        return undefined;
    try {
        return await readFile(pathValue, 'utf8');
    }
    catch {
        return undefined;
    }
}
function groundingSummaryLooksPopulated(summary) {
    if (!summary)
        return false;
    const requiredSignals = [
        '## Top-level Components',
        '## Key Flows',
        '## Story Plan',
        '## Narrative Plan',
    ];
    if (!requiredSignals.every(signal => summary.includes(signal)))
        return false;
    return !summary.includes('## Top-level Components\n-\n')
        || !summary.includes('## Key Flows\n-\n')
        || !summary.includes('## Open Questions\n-\n');
}
function splitWeakModelTimeout(totalMs) {
    const total = Number.isFinite(totalMs) ? Math.max(120000, totalMs) : 900000;
    const summaryMs = Math.min(Math.max(Math.floor(total * 0.45), 240000), 480000);
    const writeMs = Math.max(180000, total - summaryMs);
    return { summaryMs, writeMs };
}
async function executeWeakModelStagedAnalysis(session, message, context) {
    const timeoutSplit = splitWeakModelTimeout(message.timeout_ms);
    const beforeSummary = await readWeakModelGroundingSummary(context.grounding_summary_path);
    const summaryMessage = {
        ...message,
        timeout_ms: timeoutSplit.summaryMs,
    };
    const summaryRequest = buildRuntimePromptRequest({ ...session, providerSessionId: undefined }, summaryMessage, {
        prompt: buildWeakModelSummaryPassPrompt(message, context),
        rawPrompt: buildWeakModelSummaryPassPrompt(message, context),
        reflect: false,
    });
    const summaryRun = await runtime.executePrompt({ ...session, providerSessionId: undefined }, summaryRequest);
    const summarySession = updateSessionPromptCache(summaryRun.session, summaryRequest, summaryRun.result);
    if (summaryRun.result.status !== 'success') {
        return { session: summarySession, result: summaryRun.result };
    }
    const afterSummary = await readWeakModelGroundingSummary(context.grounding_summary_path);
    if (!groundingSummaryLooksPopulated(afterSummary) || afterSummary === beforeSummary) {
        return {
            session: summarySession,
            result: {
                status: 'error',
                output: 'weak-model summary pass did not produce a populated grounding summary',
                errors: ['weak-model summary pass did not produce a populated grounding summary'],
                metadata: summaryRun.result.metadata,
            },
        };
    }
    const writeMessage = {
        ...message,
        timeout_ms: timeoutSplit.writeMs,
    };
    const writePrompt = buildWeakModelWritePassPrompt(message, context);
    const writeRequest = buildRuntimePromptRequest({ ...summarySession, providerSessionId: undefined }, writeMessage, {
        prompt: writePrompt,
        rawPrompt: writePrompt,
        reflect: false,
    });
    const writeRun = await runtime.executePrompt({ ...summarySession, providerSessionId: undefined }, writeRequest);
    const mergedUsage = mergeUsageMetadata(summaryRun.result.metadata?.usage, writeRun.result.metadata?.usage);
    const writeResult = mergedUsage
        ? {
            ...writeRun.result,
            metadata: {
                ...(writeRun.result.metadata ?? {}),
                usage: mergedUsage,
            },
        }
        : writeRun.result;
    return {
        session: updateSessionPromptCache(writeRun.session, writeRequest, writeResult),
        result: writeResult,
    };
}
function updateSessionPromptCache(session, request, result) {
    if (result.status === 'error' || !request.promptPlan?.cacheKey)
        return session;
    return {
        ...session,
        promptCacheKey: request.promptPlan.cacheKey,
    };
}
async function pathExists(path) {
    try {
        await access(path, fsConstants.F_OK);
        return true;
    }
    catch {
        return false;
    }
}
async function runCommand(command, args) {
    return await new Promise((resolve) => {
        const child = spawn(command, args, {
            cwd: daemonConfig.executionProfile.homeDirectory ?? process.cwd(),
            env: process.env,
            stdio: ['ignore', 'pipe', 'ignore'],
        });
        let stdout = '';
        child.stdout.on('data', chunk => { stdout += String(chunk); });
        child.on('close', code => {
            resolve(code === 0 ? stdout.trim() : undefined);
        });
    });
}
async function runRequiredCommand(command, args, extraEnv) {
    return await new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            cwd: daemonConfig.executionProfile.homeDirectory ?? process.cwd(),
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
async function removePathIfExists(target) {
    await rm(target, { recursive: true, force: true });
}
function gitArgsForRepo(repoPath, ...gitArgs) {
    return ['-c', `safe.directory=${repoPath}`, '-C', repoPath, ...gitArgs];
}
function requestCommandText(message) {
    return typeof message.raw_prompt === 'string' && message.raw_prompt.trim()
        ? message.raw_prompt
        : message.prompt;
}
async function ensureGitSafeDirectory(repoPath) {
    if (!repoPath)
        return;
    await new Promise((resolve) => {
        const child = spawn('git', ['config', '--global', '--add', 'safe.directory', repoPath], {
            cwd: daemonConfig.executionProfile.homeDirectory ?? process.cwd(),
            env: process.env,
            stdio: ['ignore', 'ignore', 'ignore'],
        });
        child.on('close', () => resolve());
        child.on('error', () => resolve());
    });
}
async function findLatestAnalysisDir(analysisRoot) {
    try {
        const entries = await readdir(analysisRoot, { withFileTypes: true });
        const dirs = entries
            .filter(entry => entry.isDirectory())
            .map(entry => entry.name)
            .sort();
        if (dirs.length === 0)
            return undefined;
        return join(analysisRoot, dirs[dirs.length - 1]);
    }
    catch {
        return undefined;
    }
}
async function resolveValidationTargetDir(message) {
    const workflowContext = await agentWorkflowHooks?.validationContext?.(message);
    if (workflowContext?.targetDir)
        return workflowContext.targetDir;
    const explicit = message.agent_params?.memory_dir;
    if (typeof explicit === 'string' && explicit.trim())
        return explicit.trim();
    const homeDir = daemonConfig.executionProfile.homeDirectory;
    const workingDir = message.working_dir;
    if (!homeDir || !workingDir)
        return undefined;
    const projectRoot = join(homeDir, 'memory', 'projects', basename(workingDir));
    const analysisRoot = join(projectRoot, 'analysis');
    const validatorScript = agentContract.validation?.validatorScript ?? '';
    const isAugurAnalyzeValidator = validatorScript.endsWith('/skills/analyze/scripts/validate_output.py')
        && validatorScript.includes('/agents/augur/');
    if (isAugurAnalyzeValidator || agentContract.specialization === 'augur') {
        const sha = await runCommand('git', gitArgsForRepo(workingDir, 'rev-parse', 'HEAD'));
        const commitTime = sha ? await runCommand('git', gitArgsForRepo(workingDir, 'show', '-s', '--format=%ct', sha)) : undefined;
        if (sha && commitTime) {
            const expectedDir = join(analysisRoot, `${commitTime}-${sha.slice(0, 40)}`);
            if (await pathExists(expectedDir))
                return expectedDir;
            const latestDir = await findLatestAnalysisDir(analysisRoot);
            return latestDir ?? expectedDir;
        }
        const latestDir = await findLatestAnalysisDir(analysisRoot);
        return latestDir ?? analysisRoot;
    }
    return projectRoot;
}
async function runValidatorScript(validatorScript, targetDir, manageLock, extraEnv) {
    const runner = validatorScript.endsWith('.sh') ? 'bash' : 'python3';
    const env = {
        ...process.env,
        ...(manageLock ? { VALIDATE_LOCK: '1' } : {}),
        ...(extraEnv ?? {}),
    };
    return await new Promise((resolve) => {
        const child = spawn(runner, [validatorScript, targetDir], {
            cwd: daemonConfig.executionProfile.homeDirectory ?? process.cwd(),
            env,
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        let stdout = '';
        let stderr = '';
        child.stdout.on('data', chunk => { stdout += String(chunk); });
        child.stderr.on('data', chunk => { stderr += String(chunk); });
        child.on('close', code => {
            const findings = `${stdout}\n${stderr}`
                .split('\n')
                .map(line => line.trim())
                .filter(Boolean);
            resolve({
                valid: code === 0,
                findings,
            });
        });
    });
}
async function runFinalizeScript(finalizeScript, targetDir, token, attempts, extraEnv) {
    const env = {
        ...process.env,
        ...(extraEnv ?? {}),
    };
    return await new Promise((resolve) => {
        const child = spawn('python3', [finalizeScript, targetDir, '--validation-token', token, '--validation-attempts', String(attempts)], {
            cwd: daemonConfig.executionProfile.homeDirectory ?? process.cwd(),
            env,
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        let stdout = '';
        let stderr = '';
        child.stdout.on('data', chunk => { stdout += String(chunk); });
        child.stderr.on('data', chunk => { stderr += String(chunk); });
        child.on('close', code => {
            const findings = `${stdout}\n${stderr}`.split('\n').map(line => line.trim()).filter(Boolean);
            if (code !== 0) {
                resolve({ ok: false, findings });
                return;
            }
            try {
                resolve({
                    ok: true,
                    payload: JSON.parse(stdout),
                    findings,
                });
            }
            catch (error) {
                resolve({
                    ok: false,
                    findings: [...findings, error instanceof Error ? error.message : String(error)],
                });
            }
        });
    });
}
function buildArtifactsMetadata(targetDir, finalizePayload) {
    const files = {};
    const schemas = {};
    if (finalizePayload && typeof finalizePayload === 'object') {
        const artifactBlock = finalizePayload.artifacts;
        if (artifactBlock && typeof artifactBlock === 'object') {
            for (const [key, value] of Object.entries(artifactBlock)) {
                if (typeof value === 'string' && value.trim())
                    files[key] = value;
            }
        }
        const schemaBlock = finalizePayload.schemas;
        if (schemaBlock && typeof schemaBlock === 'object') {
            for (const [key, value] of Object.entries(schemaBlock)) {
                if (typeof value === 'string' && value.trim())
                    schemas[key] = value;
            }
        }
    }
    return {
        root: targetDir,
        files,
        schemas,
    };
}
function resolvedBundleMode(message) {
    const raw = typeof message.agent_params?.bundle_mode === 'string'
        ? message.agent_params.bundle_mode.trim().toLowerCase()
        : '';
    if (!raw)
        return 'selective';
    if (raw.includes('holistic')
        || raw.includes('full-bundle')
        || raw === 'full'
        || raw === 'opus-full') {
        return 'holistic';
    }
    return 'selective';
}
function resolveSelectedBundleRef(selection, bundleMode, dir) {
    if (!selection)
        return '';
    if (dir === 'skill')
        return selection;
    if (bundleMode === 'holistic') {
        return selection
            .replace('analyze-selective-', 'analyze-holistic-')
            .replace('analyze-evidence-driven-', 'analyze-holistic-');
    }
    return selection
        .replace('analyze-holistic-', 'analyze-selective-')
        .replace('analyze-evidence-driven-', 'analyze-selective-');
}
async function hashValidatedDirectory(root) {
    const hash = createHash('sha256');
    async function walk(dir, relativePrefix = '') {
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
function buildValidationRepairPrompt(input) {
    const findings = input.findings.map(line => `- ${line}`).join('\n');
    return [
        `Validation failed for \`${input.targetDir}\`.`,
        `You must fix the generated output in place and obtain a validation completion token before finishing.`,
        `Validator: \`${input.validatorScript}\``,
        `Attempt ${input.attempt} of ${input.maxAttempts}.`,
        '',
        'Current validator findings:',
        findings || '- Validation failed with no structured findings.',
        '',
        'Repair the output files now. Do not restart analysis. Keep the same project understanding and only change what is needed to pass validation.',
        `Do not call \`/validate-output\` as a shell command. If you need to validate manually inside the runtime, run \`python3 ${input.validatorScript} ${input.targetDir}\`.`,
    ].join('\n');
}
async function clearValidationLock(targetDir) {
    await rm(join(targetDir, '.validate-lock'), { force: true });
}
async function maybeRunValidationLoop(session, message, result) {
    const validation = agentContract.validation;
    if (!validation?.required)
        return { session, result };
    if (result.status !== 'success')
        return { session, result };
    if (result.metadata?.validation?.required && result.metadata.validation.passed) {
        return { session, result };
    }
    const targetDir = await resolveValidationTargetDir(message);
    if (!targetDir) {
        return {
            session,
            result: {
                status: 'error',
                output: 'validation target directory could not be resolved',
                errors: ['validation target directory could not be resolved'],
                metadata: {
                    ...(result.metadata ?? {}),
                    validation: {
                        required: true,
                        passed: false,
                        attempts: 0,
                    },
                },
            },
        };
    }
    if (!(await pathExists(validation.validatorScript))) {
        return {
            session,
            result: {
                status: 'error',
                output: `validator script not found: ${validation.validatorScript}`,
                errors: [`validator script not found: ${validation.validatorScript}`],
                metadata: {
                    ...(result.metadata ?? {}),
                    validation: {
                        required: true,
                        passed: false,
                        attempts: 0,
                        target_dir: targetDir,
                    },
                },
            },
        };
    }
    const maxAttempts = Number.isFinite(validation.maxAttempts)
        ? Math.max(validation.maxAttempts, 1)
        : Number.POSITIVE_INFINITY;
    const timeoutMs = Number.isFinite(message.timeout_ms) ? Math.max(1, message.timeout_ms) : 300000;
    const validationDeadline = Date.now() + timeoutMs;
    const minRepairBudgetMs = 15000;
    const workflowContext = await agentWorkflowHooks?.validationContext?.(message);
    const validatorEnv = workflowContext?.extraEnv;
    let currentSession = session;
    let currentResult = result;
    let accumulatedUsage = currentResult.metadata?.usage;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
        const validationRun = await runValidatorScript(validation.validatorScript, targetDir, false, validatorEnv);
        if (validationRun.valid) {
            await clearValidationLock(targetDir);
            const token = await hashValidatedDirectory(targetDir);
            let finalizePayload;
            if (validation.finalizeScript && await pathExists(validation.finalizeScript)) {
                const bundleMode = resolvedBundleMode(message);
                const finalized = await runFinalizeScript(validation.finalizeScript, targetDir, token, attempt, {
                    AUGUR_REQUEST_ID: message.correlation_id,
                    AUGUR_AGENT_NAME: AGENT_NAME,
                    AUGUR_AGENT_SPECIALIZATION: agentContract.specialization,
                    AUGUR_AGENT_CONTRACT_VERSION: agentContract.version ?? '',
                    AUGUR_RUNTIME_PROFILE_VERSION: runtimeProfile.version ?? '',
                    AUGUR_RUNTIME_KIND: daemonConfig.executionProfile.runtime,
                    AUGUR_PROVIDER: daemonConfig.executionProfile.provider,
                    AUGUR_MODEL: daemonConfig.executionProfile.model,
                    AUGUR_BUNDLE_MODE: bundleMode,
                    AUGUR_MEMORY_BUNDLE: resolveSelectedBundleRef(agentContract.bundleRefs?.memory, bundleMode, 'memory'),
                    AUGUR_RUNTIME_BUNDLE: resolveSelectedBundleRef(agentContract.bundleRefs?.runtime, bundleMode, 'runtime'),
                    AUGUR_SKILL_BUNDLE: resolveSelectedBundleRef(agentContract.bundleRefs?.skill, bundleMode, 'skill'),
                    AUGUR_WORKING_DIR: message.working_dir ?? '',
                    AUGUR_PROJECT: typeof message.agent_params?.project === 'string' ? message.agent_params.project : '',
                });
                if (finalized.ok) {
                    finalizePayload = finalized.payload;
                }
            }
            return {
                session: currentSession,
                result: {
                    ...currentResult,
                    output: `${currentResult.output}\n\nValidation token: ${token}`,
                    metadata: {
                        ...(currentResult.metadata ?? {}),
                        ...(accumulatedUsage ? { usage: accumulatedUsage } : {}),
                        artifacts: buildArtifactsMetadata(targetDir, finalizePayload),
                        validation: {
                            required: true,
                            passed: true,
                            attempts: attempt,
                            token,
                            target_dir: targetDir,
                        },
                    },
                },
            };
        }
        const remainingBudgetMs = validationDeadline - Date.now();
        const outOfAttempts = Number.isFinite(maxAttempts) && attempt >= maxAttempts;
        const outOfTime = remainingBudgetMs <= minRepairBudgetMs;
        if (outOfAttempts || outOfTime || currentResult.status === 'cancelled') {
            await runValidatorScript(validation.validatorScript, targetDir, true, validatorEnv);
            return {
                session: currentSession,
                result: {
                    status: 'error',
                    output: validationRun.findings[0] ?? 'validation failed',
                    errors: validationRun.findings.length > 0 ? validationRun.findings : ['validation failed'],
                    metadata: {
                        ...(currentResult.metadata ?? {}),
                        ...(accumulatedUsage ? { usage: accumulatedUsage } : {}),
                        validation: {
                            required: true,
                            passed: false,
                            attempts: attempt,
                            target_dir: targetDir,
                        },
                    },
                },
            };
        }
        const repairPromptBuilder = workflowContext?.repairPromptBuilder ?? buildValidationRepairPrompt;
        const repairPrompt = repairPromptBuilder({
            targetDir,
            validatorScript: validation.validatorScript,
            findings: validationRun.findings,
            attempt,
            maxAttempts,
        });
        const repairRequest = buildRuntimePromptRequest(currentSession, message, {
            prompt: repairPrompt,
            rawPrompt: repairPrompt,
            reflect: false,
        });
        const repairRun = await runtime.executePrompt(currentSession, repairRequest);
        currentSession = updateSessionPromptCache(repairRun.session, repairRequest, repairRun.result);
        accumulatedUsage = mergeUsageMetadata(accumulatedUsage, repairRun.result.metadata?.usage);
        currentResult = repairRun.result;
    }
    return {
        session: currentSession,
        result: {
            ...currentResult,
            metadata: {
                ...(currentResult.metadata ?? {}),
                ...(accumulatedUsage ? { usage: accumulatedUsage } : {}),
            },
        },
    };
}
async function handleRequest(message, gatewayReceivedAt) {
    const daemonStartedAt = Date.now();
    const cpuUsageStart = process.cpuUsage();
    let peakRssBytes = process.memoryUsage().rss;
    const samplePeakRss = () => {
        peakRssBytes = Math.max(peakRssBytes, process.memoryUsage().rss);
    };
    const contractError = validateRequestContract(message);
    if (contractError) {
        const daemonCompletedAt = Date.now();
        const telemetry = buildTelemetryMetadata({
            requestId: message.correlation_id,
            status: 'error',
            error: contractError,
            gatewayReceivedAt,
            daemonStartedAt,
            daemonCompletedAt,
            cpuUsage: process.cpuUsage(cpuUsageStart),
            peakRssBytes,
        });
        await publishResponse(message, {
            status: 'error',
            output: contractError,
            errors: [contractError],
            metadata: {
                timing: {
                    received_at: new Date(gatewayReceivedAt).toISOString(),
                    started_at: new Date(daemonStartedAt).toISOString(),
                    completed_at: new Date(daemonCompletedAt).toISOString(),
                    total_ms: Math.max(0, daemonCompletedAt - gatewayReceivedAt),
                    session_prepare_ms: 0,
                    execute_prompt_ms: 0,
                    persist_sessions_ms: 0,
                    publish_response_ms: 0,
                },
                telemetry,
            },
        });
        logTelemetry(telemetry);
        return {
            status: 'error',
            errors: [contractError],
        };
    }
    const preparedMessage = message;
    const session = sessionForMessage(message);
    await ensureGitSafeDirectory(preparedMessage.working_dir);
    samplePeakRss();
    const executeStartAt = Date.now();
    let executedSession = session;
    let executedResult;
    const workflowResult = await agentWorkflowHooks?.beforeRuntime?.(preparedMessage);
    const effectiveMessage = workflowResult?.runtimeMessage ?? preparedMessage;
    if (workflowResult?.skipResult) {
        executedResult = workflowResult.skipResult;
    }
    else {
        const readySession = await runtime.startOrResumeWarmSession(session);
        const weakModelContext = getWeakModelAnalysisContext(effectiveMessage);
        if (weakModelContext) {
            const run = await executeWeakModelStagedAnalysis(readySession, effectiveMessage, weakModelContext);
            executedSession = run.session;
            executedResult = run.result;
        }
        else {
            const runtimeSession = effectiveMessage.agent_params?.run_dir
                ? { ...readySession, providerSessionId: undefined }
                : readySession;
            const runtimeRequest = buildRuntimePromptRequest(runtimeSession, effectiveMessage);
            const run = await runtime.executePrompt(runtimeSession, runtimeRequest);
            executedSession = updateSessionPromptCache(run.session, runtimeRequest, run.result);
            executedResult = run.result;
        }
    }
    samplePeakRss();
    const { session: nextSession, result } = await maybeRunValidationLoop(executedSession, effectiveMessage, executedResult);
    const executeEndAt = Date.now();
    samplePeakRss();
    sessions.set(nextSession.key, nextSession);
    const persistStartAt = Date.now();
    await persistSessions();
    markCompletedRequest(message.correlation_id, result.status);
    await persistCompletedRequests();
    const persistEndAt = Date.now();
    samplePeakRss();
    const daemonCompletedAt = Date.now();
    const telemetry = buildTelemetryMetadata({
        requestId: message.correlation_id,
        status: result.status,
        error: result.status === 'error' ? (result.errors?.[0] ?? result.output) : null,
        gatewayReceivedAt,
        daemonStartedAt,
        daemonCompletedAt,
        cpuUsage: process.cpuUsage(cpuUsageStart),
        peakRssBytes,
        usage: result.metadata?.usage,
    });
    const response = {
        status: result.status,
        output: result.output,
        reflection: result.reflection,
        errors: result.errors,
        metadata: {
            ...(result.metadata ?? {}),
            telemetry,
            timing: buildTimingMetadata({
                gatewayReceivedAt,
                daemonStartedAt,
                daemonCompletedAt,
                executeStartAt,
                executeEndAt,
                persistStartAt,
                persistEndAt,
            }),
        },
    };
    await publishResponse(message, response);
    logTelemetry(telemetry);
    if (result.reflection) {
        await publishReflection(message, result.reflection);
    }
    return {
        status: result.status,
        errors: result.errors,
    };
}
async function publishDiscoveryRecord(record) {
    if (!daemonConfig.discoveryServerUrl)
        return;
    await publishDiscoveryRegistration(daemonConfig.discoveryServerUrl, record);
}
function startDiscoveryHeartbeat(record) {
    if (!daemonConfig.discoveryServerUrl)
        return;
    const publish = async () => {
        try {
            await publishDiscoveryRecord(record);
        }
        catch (error) {
            log('discovery_registration_failed', {
                agent: AGENT_NAME,
                error: error instanceof Error ? error.message : String(error),
            });
        }
    };
    void publish();
    discoveryHeartbeat = setInterval(() => {
        void publish();
    }, daemonConfig.discoveryPublishIntervalMs);
}
async function main() {
    await new Promise((resolve, reject) => {
        healthServer.once('error', reject);
        healthServer.listen(healthPort, '0.0.0.0', () => resolve());
    });
    log('daemon_start', {
        agent: AGENT_NAME,
        agent_contract: agentContract,
        runtime_profile: runtimeProfile,
        execution_profile: redactExecutionProfile(daemonConfig.executionProfile),
        brokers: daemonConfig.kafkaBrokers,
        kafka_consumer_group_id: consumerGroupId,
        kafka_session_timeout_ms: daemonConfig.kafkaSessionTimeoutMs,
        kafka_heartbeat_interval_ms: daemonConfig.kafkaHeartbeatIntervalMs,
        reflections_topic: daemonConfig.reflectionsTopic,
        progress_topic: daemonConfig.progressTopic,
        discovery_server_url: daemonConfig.discoveryServerUrl ?? null,
        session_map_path: daemonConfig.sessionMapPath,
    });
    await producer.connect();
    await consumer.connect();
    await consumer.subscribe({ topic: AGENT_NAME, fromBeginning: false });
    const discoveryRecord = buildDiscoveryRecord({
        agent: AGENT_NAME,
        specialization: agentContract.specialization,
        agentContract,
        config: daemonConfig,
        healthUrl,
    });
    startDiscoveryHeartbeat(discoveryRecord);
    await consumer.run({
        eachBatchAutoResolve: false,
        eachBatch: async ({ batch, resolveOffset, heartbeat, commitOffsetsIfNecessary, isRunning, isStale }) => {
            for (const message of batch.messages) {
                if (!isRunning() || isStale())
                    break;
                const raw = message.value?.toString() ?? '';
                let parsed;
                try {
                    parsed = JSON.parse(raw);
                }
                catch (error) {
                    log('message_parse_failed', { topic: batch.topic, error: error.message });
                    resolveOffset(message.offset);
                    await commitOffsetsIfNecessary();
                    await heartbeat();
                    continue;
                }
                if (!isRequestMessage(parsed)) {
                    log('message_ignored', { topic: batch.topic, reason: 'not_request' });
                    resolveOffset(message.offset);
                    await commitOffsetsIfNecessary();
                    await heartbeat();
                    continue;
                }
                if (hasCompletedRequest(parsed.correlation_id)) {
                    log('message_ignored', {
                        topic: batch.topic,
                        reason: 'duplicate_completed_request',
                        correlation_id: parsed.correlation_id,
                    });
                    resolveOffset(message.offset);
                    await commitOffsetsIfNecessary();
                    await heartbeat();
                    continue;
                }
                const gatewayReceivedAt = parseGatewayReceivedAt(message.timestamp);
                await publishProgress(parsed, {
                    source: 'agent-daemon',
                    kind: 'request.picked_up',
                    payload: {
                        topic: batch.topic,
                        partition: batch.partition,
                        offset: message.offset,
                    },
                });
                log('request_received', {
                    topic: batch.topic,
                    sender: parsed.sender,
                    correlation_id: parsed.correlation_id,
                    working_dir: parsed.working_dir ?? null,
                    session_id: parsed.session_id ?? null,
                    has_working_dir: Boolean(parsed.working_dir),
                });
                const heartbeatTimer = setInterval(() => {
                    void heartbeat().catch(error => {
                        log('consumer_heartbeat_failed', {
                            topic: batch.topic,
                            correlation_id: parsed.correlation_id,
                            error: error instanceof Error ? error.message : String(error),
                        });
                    });
                }, Math.max(1000, Math.floor(daemonConfig.kafkaHeartbeatIntervalMs / 2)));
                try {
                    const summary = await handleRequest(parsed, gatewayReceivedAt);
                    log('request_handled', {
                        topic: batch.topic,
                        sender: parsed.sender,
                        correlation_id: parsed.correlation_id,
                        status: summary.status,
                        errors: summary.errors,
                    });
                }
                catch (error) {
                    const messageText = error.message;
                    const daemonStartedAt = Date.now();
                    const daemonCompletedAt = daemonStartedAt;
                    const telemetry = buildTelemetryMetadata({
                        requestId: parsed.correlation_id,
                        status: 'error',
                        error: messageText,
                        gatewayReceivedAt,
                        daemonStartedAt,
                        daemonCompletedAt,
                        cpuUsage: { user: 0, system: 0 },
                        peakRssBytes: process.memoryUsage().rss,
                    });
                    log('request_failed', {
                        topic: batch.topic,
                        sender: parsed.sender,
                        correlation_id: parsed.correlation_id,
                        error: messageText,
                    });
                    await publishResponse(parsed, {
                        status: 'error',
                        output: messageText,
                        errors: [messageText],
                        metadata: {
                            timing: {
                                received_at: new Date(gatewayReceivedAt).toISOString(),
                                started_at: new Date(daemonStartedAt).toISOString(),
                                completed_at: new Date(daemonCompletedAt).toISOString(),
                                total_ms: Math.max(0, daemonCompletedAt - gatewayReceivedAt),
                                session_prepare_ms: 0,
                                execute_prompt_ms: 0,
                                persist_sessions_ms: 0,
                                publish_response_ms: 0,
                            },
                            telemetry,
                        },
                    });
                    logTelemetry(telemetry);
                    markCompletedRequest(parsed.correlation_id, 'error');
                    await persistCompletedRequests();
                }
                finally {
                    clearInterval(heartbeatTimer);
                }
                resolveOffset(message.offset);
                await commitOffsetsIfNecessary();
                await heartbeat();
            }
        },
    });
    daemonReady = true;
    log('daemon_ready', { agent: AGENT_NAME, health_port: healthPort });
}
main().catch(error => {
    if (discoveryHeartbeat)
        clearInterval(discoveryHeartbeat);
    log('daemon_fatal', { error: error.message });
    process.exit(1);
});
