import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { basename, join } from 'node:path';
import { constants as fsConstants, existsSync, readFileSync } from 'node:fs';
import { access, readFile, readdir, rm } from 'node:fs/promises';
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
    const payload = buildResponseMessage(AGENT_NAME, message, sanitizeResponseForKafka(response));
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
const maxKafkaResponseBytes = Number.parseInt(process.env.KLAUDE_DAEMON_MAX_KAFKA_RESPONSE_BYTES ?? '900000', 10);
function truncateText(value, maxLength) {
    if (value.length <= maxLength)
        return value;
    return `${value.slice(0, Math.max(0, maxLength - 17))}\n\n[truncated by daemon]`;
}
function sanitizeResponseForKafka(response) {
    const payload = {
        ...response,
        errors: Array.isArray(response.errors) ? [...response.errors] : response.errors,
        metadata: response.metadata ? { ...response.metadata } : response.metadata,
    };
    let serialized = JSON.stringify(buildResponseMessage(AGENT_NAME, {
        type: 'request',
        sender: '',
        correlation_id: '',
        prompt: '',
    }, payload));
    if (Buffer.byteLength(serialized, 'utf8') <= maxKafkaResponseBytes)
        return payload;
    if (Array.isArray(payload.errors)) {
        payload.errors = payload.errors.map(error => truncateText(String(error), 1200)).slice(0, 8);
    }
    if (typeof payload.output === 'string') {
        payload.output = truncateText(payload.output, 4000);
    }
    if (payload.metadata && typeof payload.metadata === 'object') {
        const metadata = payload.metadata;
        const runtime = metadata.runtime;
        if (runtime && typeof runtime === 'object') {
            const runtimeRecord = { ...runtime };
            if (typeof runtimeRecord.stdout === 'string')
                runtimeRecord.stdout = truncateText(runtimeRecord.stdout, 1200);
            if (typeof runtimeRecord.stderr === 'string')
                runtimeRecord.stderr = truncateText(runtimeRecord.stderr, 1200);
            metadata.runtime = runtimeRecord;
        }
    }
    serialized = JSON.stringify(buildResponseMessage(AGENT_NAME, {
        type: 'request',
        sender: '',
        correlation_id: '',
        prompt: '',
    }, payload));
    if (Buffer.byteLength(serialized, 'utf8') <= maxKafkaResponseBytes)
        return payload;
    return {
        ...payload,
        output: typeof payload.output === 'string' ? truncateText(payload.output, 1200) : payload.output,
        errors: Array.isArray(payload.errors)
            ? payload.errors.map(error => truncateText(String(error), 400)).slice(0, 4)
            : payload.errors,
        metadata: payload.metadata ? {
            timing: payload.metadata.timing,
            telemetry: payload.metadata.telemetry,
            validation: payload.metadata.validation,
        } : payload.metadata,
    };
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
function isKafkaMembershipLostError(error) {
    const message = error instanceof Error ? error.message : String(error);
    const normalized = message.toLowerCase();
    return normalized.includes('the group is rebalancing')
        || normalized.includes('the coordinator is not aware of this member');
}
function validateRequestContract(message) {
    if (agentContract.requiresWorkingDirectory && !message.working_dir) {
        return 'working_dir is required for this agent';
    }
    if (message.workspace) {
        if (!message.workspace.working_dir?.trim()) {
            return 'workspace.working_dir is required when workspace is provided';
        }
        if (!message.workspace.output_dir?.trim()) {
            return 'workspace.output_dir is required when workspace is provided';
        }
        if (message.working_dir && message.workspace.working_dir !== message.working_dir) {
            return 'working_dir must match workspace.working_dir when both are provided';
        }
    }
    if (agentContract.validation?.required && !message.resources) {
        return 'resources contract is required for agents with validation';
    }
    if (message.resources) {
        if (agentContract.validation?.required && !message.resources.validator_script?.trim()) {
            return 'resources.validator_script is required for agents with validation';
        }
    }
    if (message.workspace?.agent_root !== undefined && !message.workspace.agent_root?.trim()) {
        return 'workspace.agent_root must be non-empty when provided';
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
        workspace: promptMessage.workspace,
        resources: promptMessage.resources,
        // Request timeout is gateway/accounting metadata only. Do not propagate it
        // into the runtime, otherwise async runs and repair resumes can be killed by
        // stale per-request execution deadlines.
        timeout_ms: undefined,
        reflect: overrides?.reflect ?? (agentContract.validation?.required ? false : promptMessage.reflect),
        reflection_prompt: promptMessage.reflection_prompt,
        agent_params: promptMessage.agent_params,
        progress: event => publishProgress(message, event),
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
    const isAugurAnalyzeValidator = validatorScript.endsWith('/skills/analyze/validator/validate.py')
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
    let effectivePayload = finalizePayload;
    if (!effectivePayload) {
        try {
            const metaPath = join(targetDir, 'meta.json');
            if (existsSync(metaPath)) {
                effectivePayload = JSON.parse(readFileSync(metaPath, 'utf8'));
            }
        }
        catch {
            effectivePayload = undefined;
        }
    }
    if (effectivePayload && typeof effectivePayload === 'object') {
        const artifactBlock = effectivePayload.artifacts;
        if (artifactBlock && typeof artifactBlock === 'object') {
            for (const [key, value] of Object.entries(artifactBlock)) {
                if (typeof value === 'string' && value.trim())
                    files[key] = value;
            }
        }
        const schemaBlock = effectivePayload.schemas;
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
async function clearValidationLock(targetDir) {
    await rm(join(targetDir, '.validate-lock'), { force: true });
}
async function maybeRunFinalValidation(session, message, result) {
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
    const workflowContext = await agentWorkflowHooks?.validationContext?.(message);
    const validatorEnv = workflowContext?.extraEnv;
    const priorAttempts = typeof result.metadata?.validation?.attempts === 'number'
        ? Math.max(0, result.metadata.validation.attempts)
        : 0;
    const validationToken = await hashValidatedDirectory(targetDir);
    const validationRun = await runValidatorScript(validation.validatorScript, targetDir, true, {
        ...(validatorEnv ?? {}),
        AUGUR_VALIDATION_TOKEN: validationToken,
        AUGUR_VALIDATION_ATTEMPTS: String(priorAttempts),
    });
    if (validationRun.valid) {
        await clearValidationLock(targetDir);
        return {
            session,
            result: {
                ...result,
                output: `${result.output}\n\nValidation token: ${validationToken}`,
                metadata: {
                    ...(result.metadata ?? {}),
                    artifacts: buildArtifactsMetadata(targetDir),
                    validation: {
                        required: true,
                        passed: true,
                        attempts: priorAttempts,
                        token: validationToken,
                        target_dir: targetDir,
                    },
                },
            },
        };
    }
    return {
        session,
        result: {
            status: 'error',
            output: validationRun.findings[0] ?? 'validation failed',
            errors: validationRun.findings.length > 0 ? validationRun.findings : ['validation failed'],
            metadata: {
                ...(result.metadata ?? {}),
                validation: {
                    required: true,
                    passed: false,
                    attempts: priorAttempts,
                    target_dir: targetDir,
                },
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
    const preparedMessage = message;
    const session = sessionForMessage(message);
    const workflowResult = await agentWorkflowHooks?.beforeRuntime?.(preparedMessage);
    const effectiveMessage = workflowResult?.runtimeMessage ?? preparedMessage;
    const contractError = validateRequestContract(effectiveMessage);
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
    await ensureGitSafeDirectory(effectiveMessage.working_dir);
    samplePeakRss();
    const executeStartAt = Date.now();
    let executedSession = session;
    let executedResult;
    if (workflowResult?.skipResult) {
        executedResult = workflowResult.skipResult;
    }
    else {
        const readySession = await runtime.startOrResumeWarmSession(session);
        const runtimeSession = effectiveMessage.agent_params?.run_dir
            ? { ...readySession, providerSessionId: undefined }
            : readySession;
        const runtimeRequest = buildRuntimePromptRequest(runtimeSession, effectiveMessage);
        const run = await runtime.executePrompt(runtimeSession, runtimeRequest);
        executedSession = updateSessionPromptCache(run.session, runtimeRequest, run.result);
        executedResult = run.result;
    }
    samplePeakRss();
    const { session: nextSession, result } = await maybeRunFinalValidation(executedSession, effectiveMessage, executedResult);
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
                let membershipLost = false;
                let heartbeatFailureLogged = false;
                const heartbeatTimer = setInterval(() => {
                    if (membershipLost)
                        return;
                    void heartbeat().catch(error => {
                        const errorMessage = error instanceof Error ? error.message : String(error);
                        if (isKafkaMembershipLostError(error)) {
                            membershipLost = true;
                            log('consumer_membership_lost', {
                                topic: batch.topic,
                                correlation_id: parsed.correlation_id,
                                error: errorMessage,
                            });
                            return;
                        }
                        if (!heartbeatFailureLogged) {
                            heartbeatFailureLogged = true;
                            log('consumer_heartbeat_failed', {
                                topic: batch.topic,
                                correlation_id: parsed.correlation_id,
                                error: errorMessage,
                            });
                        }
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
                if (membershipLost || isStale() || !isRunning()) {
                    log('consumer_offset_commit_skipped', {
                        topic: batch.topic,
                        correlation_id: parsed.correlation_id,
                        membership_lost: membershipLost,
                        stale: isStale(),
                        running: isRunning(),
                    });
                    break;
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
