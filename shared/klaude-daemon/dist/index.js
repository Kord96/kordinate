import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { basename, join } from 'node:path';
import { constants as fsConstants } from 'node:fs';
import { access, readdir, readFile, rm } from 'node:fs/promises';
import { createServer } from 'node:http';
import { Kafka } from 'kafkajs';
import { createAgentWorkflowHooks } from './agent-workflows.js';
import { CompletedRequestStore } from './completed-request-store.js';
import { loadDaemonConfig } from './config.js';
import { buildPromptPlanFromProfile, loadAgentProfile } from './agent-profile.js';
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
const AGENT_PROFILE = process.env.AGENT_PROFILE ?? AGENT_NAME;
const agentProfile = loadAgentProfile(AGENT_PROFILE);
const daemonConfig = loadDaemonConfig();
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
    agentProfileName: AGENT_PROFILE,
    agentProfile,
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
        agentProfile: AGENT_PROFILE,
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
        received_at: new Date(input.receivedAt).toISOString(),
        started_at: new Date(input.startedAt).toISOString(),
        completed_at: nowIso(),
        total_ms: Date.now() - input.receivedAt,
        session_prepare_ms: input.executeStartAt - input.startedAt,
        execute_prompt_ms: input.executeEndAt - input.executeStartAt,
        persist_sessions_ms: input.persistEndAt - input.persistStartAt,
        publish_response_ms: 0,
    };
}
function validateRequestContract(message) {
    if (agentProfile.requiresWorkingDirectory && !message.working_dir) {
        return 'working_dir is required for this agent';
    }
    return undefined;
}
function buildRuntimePromptRequest(session, message, overrides) {
    const promptMessage = {
        ...message,
        prompt: overrides?.prompt ?? message.prompt,
        raw_prompt: overrides?.rawPrompt ?? message.raw_prompt ?? message.prompt,
    };
    const promptPlan = buildPromptPlanFromProfile(agentProfile, promptMessage);
    const prompt = session.promptCacheKey && session.promptCacheKey === promptPlan.cacheKey
        ? promptPlan.dynamicPrompt
        : promptPlan.fullPrompt;
    return {
        prompt,
        raw_prompt: promptMessage.raw_prompt,
        promptPlan,
        working_dir: promptMessage.working_dir,
        timeout_ms: promptMessage.timeout_ms,
        reflect: overrides?.reflect ?? (agentProfile.validation?.required ? false : promptMessage.reflect),
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
    const validatorScript = agentProfile.validation?.validatorScript ?? '';
    const isAugurAnalyzeValidator = validatorScript.endsWith('/skills/analyze/scripts/validate_output.py')
        && validatorScript.includes('/agents/augur/');
    if (isAugurAnalyzeValidator || AGENT_PROFILE === 'augur') {
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
async function runFinalizeScript(finalizeScript, targetDir, token, attempts) {
    const env = { ...process.env };
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
    const validation = agentProfile.validation;
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
    const maxAttempts = Math.max(validation.maxAttempts ?? 3, 1);
    const workflowContext = await agentWorkflowHooks?.validationContext?.(message);
    const validatorEnv = workflowContext?.extraEnv;
    let currentSession = session;
    let currentResult = result;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
        const validationRun = await runValidatorScript(validation.validatorScript, targetDir, false, validatorEnv);
        if (validationRun.valid) {
            await clearValidationLock(targetDir);
            const token = await hashValidatedDirectory(targetDir);
            let finalizePayload;
            if (validation.finalizeScript && await pathExists(validation.finalizeScript)) {
                const finalized = await runFinalizeScript(validation.finalizeScript, targetDir, token, attempt);
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
        if (attempt >= maxAttempts || currentResult.status === 'cancelled') {
            await runValidatorScript(validation.validatorScript, targetDir, true, validatorEnv);
            return {
                session: currentSession,
                result: {
                    status: 'error',
                    output: validationRun.findings[0] ?? 'validation failed',
                    errors: validationRun.findings.length > 0 ? validationRun.findings : ['validation failed'],
                    metadata: {
                        ...(currentResult.metadata ?? {}),
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
        currentResult = repairRun.result;
    }
    return { session: currentSession, result: currentResult };
}
async function handleRequest(message) {
    const receivedAt = Date.now();
    const contractError = validateRequestContract(message);
    if (contractError) {
        await publishResponse(message, {
            status: 'error',
            output: contractError,
            errors: [contractError],
            metadata: {
                timing: {
                    received_at: new Date(receivedAt).toISOString(),
                    started_at: new Date(receivedAt).toISOString(),
                    completed_at: nowIso(),
                    total_ms: 0,
                    session_prepare_ms: 0,
                    execute_prompt_ms: 0,
                    persist_sessions_ms: 0,
                    publish_response_ms: 0,
                },
            },
        });
        return {
            status: 'error',
            errors: [contractError],
        };
    }
    const startedAt = Date.now();
    const preparedMessage = message;
    const session = sessionForMessage(message);
    await ensureGitSafeDirectory(preparedMessage.working_dir);
    const executeStartAt = Date.now();
    let executedSession = session;
    let executedResult;
    const workflowResult = await agentWorkflowHooks?.beforeRuntime?.(preparedMessage);
    if (workflowResult?.skipResult) {
        executedResult = workflowResult.skipResult;
    }
    else {
        const runtimeMessage = workflowResult?.runtimeMessage ?? preparedMessage;
        const readySession = await runtime.startOrResumeWarmSession(session);
        const runtimeRequest = buildRuntimePromptRequest(readySession, runtimeMessage);
        const run = await runtime.executePrompt(readySession, runtimeRequest);
        executedSession = updateSessionPromptCache(run.session, runtimeRequest, run.result);
        executedResult = run.result;
    }
    const { session: nextSession, result } = await maybeRunValidationLoop(executedSession, preparedMessage, executedResult);
    const executeEndAt = Date.now();
    sessions.set(nextSession.key, nextSession);
    const persistStartAt = Date.now();
    await persistSessions();
    markCompletedRequest(message.correlation_id, result.status);
    await persistCompletedRequests();
    const persistEndAt = Date.now();
    const response = {
        status: result.status,
        output: result.output,
        reflection: result.reflection,
        errors: result.errors,
        metadata: {
            ...(result.metadata ?? {}),
            timing: buildTimingMetadata({
                receivedAt,
                startedAt,
                executeStartAt,
                executeEndAt,
                persistStartAt,
                persistEndAt,
            }),
        },
    };
    await publishResponse(message, response);
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
        agent_profile_name: AGENT_PROFILE,
        agent_profile: agentProfile,
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
        specialization: AGENT_PROFILE,
        agentProfile,
        config: daemonConfig,
        healthUrl,
    });
    startDiscoveryHeartbeat(discoveryRecord);
    await consumer.run({
        eachMessage: async ({ topic, message }) => {
            const raw = message.value?.toString() ?? '';
            let parsed;
            try {
                parsed = JSON.parse(raw);
            }
            catch (error) {
                log('message_parse_failed', { topic, error: error.message });
                return;
            }
            if (!isRequestMessage(parsed)) {
                log('message_ignored', { topic, reason: 'not_request' });
                return;
            }
            if (hasCompletedRequest(parsed.correlation_id)) {
                log('message_ignored', {
                    topic,
                    reason: 'duplicate_completed_request',
                    correlation_id: parsed.correlation_id,
                });
                return;
            }
            log('request_received', {
                topic,
                sender: parsed.sender,
                correlation_id: parsed.correlation_id,
                working_dir: parsed.working_dir ?? null,
                session_id: parsed.session_id ?? null,
                has_working_dir: Boolean(parsed.working_dir),
            });
            try {
                const summary = await handleRequest(parsed);
                log('request_handled', {
                    topic,
                    sender: parsed.sender,
                    correlation_id: parsed.correlation_id,
                    status: summary.status,
                    errors: summary.errors,
                });
            }
            catch (error) {
                const messageText = error.message;
                log('request_failed', {
                    topic,
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
                            received_at: nowIso(),
                            started_at: nowIso(),
                            completed_at: nowIso(),
                            total_ms: 0,
                            session_prepare_ms: 0,
                            execute_prompt_ms: 0,
                            persist_sessions_ms: 0,
                            publish_response_ms: 0,
                        },
                    },
                });
                markCompletedRequest(parsed.correlation_id, 'error');
                await persistCompletedRequests();
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
