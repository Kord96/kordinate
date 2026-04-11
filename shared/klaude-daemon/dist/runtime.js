import { randomUUID } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { createWriteStream } from 'node:fs';
import path from 'node:path';
import { mkdir, readFile } from 'node:fs/promises';
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Codex } from '@openai/codex-sdk';
import { log } from './log.js';
const OPENCLAUDE_NPM_PACKAGE = process.env.OPENCLAUDE_NPM_PACKAGE ?? '@gitlawb/openclaude';
const OPENCLAUDE_BIN = process.env.OPENCLAUDE_BIN ?? 'openclaude';
function parseReflectionPayload(text) {
    try {
        const parsed = JSON.parse(text);
        if (typeof parsed.project === 'string' && typeof parsed.general === 'string') {
            return { project: parsed.project, general: parsed.general };
        }
    }
    catch {
        // ignore
    }
    return undefined;
}
function buildDefaultReflectionPrompt(taskOutput, overridePrompt) {
    const base = overridePrompt ?? [
        'Based on the completed task, return strict JSON only with exactly these keys:',
        '{"project":"...","general":"..."}',
        'project: lessons specific to the current project/repo/context.',
        'general: lessons that transfer to any project.',
        'Use strings only. If there is no strong lesson for a key, return an empty string.',
    ].join('\n');
    return `${base}\n\nTask output:\n${taskOutput}`;
}
function appendErrors(result, errors) {
    if (!errors || errors.length === 0)
        return result;
    return {
        ...result,
        errors: [...(result.errors ?? []), ...errors],
    };
}
function withReflection(result, reflection) {
    if (!reflection)
        return result;
    return {
        ...result,
        reflection,
    };
}
function finalizeRuntimeResult(result, reflectionResult) {
    if (!reflectionResult)
        return result;
    return appendErrors(withReflection(result, reflectionResult.reflection), reflectionResult.errors);
}
function errorResult(message) {
    return {
        status: 'error',
        output: message,
        errors: [message],
    };
}
function appendDiagnosticPart(parts, label, value) {
    if (typeof value !== 'string')
        return;
    const trimmed = value.trim();
    if (!trimmed)
        return;
    parts.push(`${label}: ${trimmed}`);
}
export function formatProviderError(error) {
    if (!(error instanceof Error)) {
        return [String(error)];
    }
    const parts = [];
    const seen = new Set();
    const pushUnique = (text) => {
        const trimmed = text.trim();
        if (!trimmed || seen.has(trimmed))
            return;
        seen.add(trimmed);
        parts.push(trimmed);
    };
    pushUnique(error.message);
    const maybeWithProps = error;
    appendDiagnosticPart(parts, 'stderr', maybeWithProps.stderr);
    appendDiagnosticPart(parts, 'stdout', maybeWithProps.stdout);
    appendDiagnosticPart(parts, 'debug_log_path', maybeWithProps.debugLogPath);
    appendDiagnosticPart(parts, 'debug_log_tail', maybeWithProps.debugLogTail);
    appendDiagnosticPart(parts, 'structured_log_path', maybeWithProps.structuredLogPath);
    appendDiagnosticPart(parts, 'structured_log_tail', maybeWithProps.structuredLogTail);
    if (typeof maybeWithProps.code === 'string' || typeof maybeWithProps.code === 'number') {
        pushUnique(`code: ${String(maybeWithProps.code)}`);
    }
    if (typeof maybeWithProps.exitCode === 'number') {
        pushUnique(`exit_code: ${String(maybeWithProps.exitCode)}`);
    }
    if (typeof maybeWithProps.signal === 'string' && maybeWithProps.signal.trim()) {
        pushUnique(`signal: ${maybeWithProps.signal.trim()}`);
    }
    if (maybeWithProps.cause instanceof Error) {
        for (const detail of formatProviderError(maybeWithProps.cause)) {
            if (detail !== error.message)
                pushUnique(`cause: ${detail}`);
        }
    }
    else if (typeof maybeWithProps.cause === 'string' && maybeWithProps.cause.trim()) {
        pushUnique(`cause: ${maybeWithProps.cause.trim()}`);
    }
    return parts.length > 0 ? parts : ['unknown provider error'];
}
export const __testOnly = {
    classifyAlfredDirectIntent,
    enforceAlfredDirectIntentContract,
};
function errorResultFromError(error) {
    const details = formatProviderError(error);
    return {
        status: 'error',
        output: details[0] ?? 'unknown provider error',
        errors: details,
    };
}
function successResult(output) {
    return {
        status: 'success',
        output,
    };
}
function isAlfredRuntimeContext() {
    const profile = (process.env.AGENT_PROFILE_NAME ?? '').trim().toLowerCase();
    const name = (process.env.AGENT_NAME ?? '').trim().toLowerCase();
    return profile === 'alfred' || name.startsWith('alfred');
}
function classifyAlfredDirectIntent(prompt) {
    const trimmed = prompt.trim();
    const getMatch = /^get key ([^\s]+)\s*$/i.exec(trimmed);
    if (getMatch) {
        return { kind: 'get_secret', keyPath: getMatch[1] };
    }
    const storeMatch = /^store key ([^\s]+)\s+value\s+([\s\S]+)$/i.exec(trimmed);
    if (storeMatch) {
        return { kind: 'store_secret', keyPath: storeMatch[1], value: storeMatch[2].trim() };
    }
    return undefined;
}
function invalidAlfredDirectResult(intent, output) {
    const trimmed = output.trim();
    if (!trimmed) {
        return `${intent.kind} completed without returning a concrete result`;
    }
    const normalized = trimmed.toLowerCase();
    if (normalized === 'what can i help you with today?') {
        return `${intent.kind} returned generic assistant text instead of executing the operation`;
    }
    if (intent.kind === 'get_secret' && ['stored', 'validated', 'no change'].includes(normalized)) {
        return 'get_secret returned a write-style confirmation instead of the requested value';
    }
    if (intent.kind === 'store_secret' && trimmed === intent.value) {
        return 'store_secret echoed the secret value instead of returning a confirmation';
    }
    return undefined;
}
function enforceAlfredDirectIntentContract(request, result) {
    if (!isAlfredRuntimeContext() || result.status !== 'success')
        return result;
    const intent = classifyAlfredDirectIntent(request.prompt);
    if (!intent)
        return result;
    const violation = invalidAlfredDirectResult(intent, result.output);
    if (!violation)
        return result;
    log('alfred_contract_violation', {
        intent: intent.kind,
        key_path: intent.keyPath,
        violation,
        output: summarizeText(result.output, 400) || null,
    });
    return {
        status: 'error',
        output: violation,
        errors: [violation],
    };
}
function summarizeText(text, maxLength = 400) {
    const normalized = text.replace(/\s+/g, ' ').trim();
    if (normalized.length <= maxLength)
        return normalized;
    return `${normalized.slice(0, maxLength - 3)}...`;
}
function summarizeUnknown(value, maxLength = 1200) {
    if (typeof value === 'string')
        return summarizeText(value, maxLength);
    if (value === null || value === undefined)
        return undefined;
    try {
        return summarizeText(JSON.stringify(value), maxLength);
    }
    catch {
        return summarizeText(String(value), maxLength);
    }
}
function extractBashCommand(input) {
    if (!input || typeof input !== 'object')
        return undefined;
    const candidate = input;
    for (const key of ['command', 'cmd', 'script']) {
        if (typeof candidate[key] === 'string' && candidate[key].trim()) {
            return candidate[key].trim();
        }
    }
    return undefined;
}
function processOpenClaudeStructuredMessage(message, options) {
    if (message.type === 'assistant' && Array.isArray(message.message?.content)) {
        for (const block of message.message.content) {
            if (block.type === 'tool_use') {
                const toolInputSummary = summarizeUnknown(block.input);
                const bashCommand = extractBashCommand(block.input);
                log('harness_tool_use', {
                    runtime: 'openclaude-harness',
                    model: options.model,
                    session_id: options.sessionId,
                    tool_name: block.name ?? 'unknown',
                    tool_input: toolInputSummary ?? null,
                    bash_command: bashCommand ?? null,
                });
            }
        }
        return;
    }
    if (message.type === 'tool_progress') {
        log('harness_tool_progress', {
            runtime: 'openclaude-harness',
            model: options.model,
            session_id: options.sessionId,
            tool_name: message.tool_name ?? 'unknown',
            tool_use_id: message.tool_use_id ?? null,
            elapsed_time_seconds: message.elapsed_time_seconds ?? null,
        });
    }
}
function consumeOpenClaudeStructuredChunk(state, chunkText, options) {
    state.buffer += chunkText;
    while (true) {
        const newlineIndex = state.buffer.indexOf('\n');
        if (newlineIndex === -1)
            break;
        const line = state.buffer.slice(0, newlineIndex).trim();
        state.buffer = state.buffer.slice(newlineIndex + 1);
        if (!line)
            continue;
        state.rawLines.push(line);
        if (state.rawLines.length > 200)
            state.rawLines.shift();
        state.writeLine(line);
        let parsed;
        try {
            parsed = JSON.parse(line);
        }
        catch {
            continue;
        }
        processOpenClaudeStructuredMessage(parsed, options);
        if (parsed.type === 'result' && typeof parsed.result === 'string') {
            state.resultText = parsed.result;
        }
    }
}
function finalizeOpenClaudeStructuredStream(state, options) {
    if (!state.buffer.trim())
        return;
    consumeOpenClaudeStructuredChunk(state, '\n', options);
}
function processCodexStructuredEvent(event, options) {
    const base = {
        runtime: 'codex-sdk',
        model: options.model,
        session_id: options.sessionId,
    };
    if ((event.type === 'item.started' || event.type === 'item.updated' || event.type === 'item.completed') && event.item) {
        const item = event.item;
        log('codex_item_event', {
            ...base,
            event_type: event.type,
            item_type: item.type ?? 'unknown',
            item_id: item.id ?? null,
            status: item.status ?? null,
            command: typeof item.command === 'string' ? item.command : null,
            text: typeof item.text === 'string' ? summarizeText(item.text, 400) : null,
            tool_server: typeof item.server === 'string' ? item.server : null,
            tool_name: typeof item.tool === 'string' ? item.tool : null,
            tool_arguments: summarizeUnknown(item.arguments) ?? null,
            aggregated_output: typeof item.aggregated_output === 'string' ? summarizeText(item.aggregated_output, 1200) : null,
            error_message: typeof item.error?.message === 'string' ? item.error.message : null,
            file_changes: Array.isArray(item.changes) ? summarizeUnknown(item.changes, 1200) ?? null : null,
        });
        return;
    }
    if (event.type === 'turn.completed') {
        log('codex_turn_completed', {
            ...base,
            usage: summarizeUnknown(event.usage) ?? null,
        });
        return;
    }
    if (event.type === 'turn.failed' || event.type === 'error') {
        log('codex_turn_error', {
            ...base,
            error: summarizeUnknown(event.error ?? event.message) ?? null,
        });
    }
}
async function runCodexStructuredTurn(threadFactory, prompt, options) {
    const runtimeHome = resolveOpenClaudeHome(options.workingDirectory);
    const debugDir = path.join(runtimeHome, '.daemon-logs');
    await mkdir(debugDir, { recursive: true });
    const structuredLogPath = path.join(debugDir, `codex-${options.sessionId}-${Date.now()}-stream.jsonl`);
    const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' });
    const thread = threadFactory();
    let finalResponse = '';
    log('codex_stream_start', {
        runtime: 'codex-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
    });
    try {
        const { events } = await thread.runStreamed(prompt);
        for await (const event of events) {
            structuredLogStream.write(`${JSON.stringify(event)}\n`);
            processCodexStructuredEvent(event, options);
            if ((event.type === 'item.completed' || event.type === 'item.updated')
                && event.item?.type === 'agent_message'
                && typeof event.item.text === 'string') {
                finalResponse = event.item.text;
            }
        }
    }
    catch (error) {
        await new Promise(resolve => structuredLogStream.end(resolve));
        let structuredLogTail = '';
        try {
            structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
        }
        catch {
            // ignore
        }
        log('codex_stream_error', {
            runtime: 'codex-sdk',
            model: options.model,
            session_id: options.sessionId,
            structured_log_path: structuredLogPath,
            error: error instanceof Error ? error.message : String(error),
        });
        throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
            structuredLogPath,
            structuredLogTail,
        });
    }
    finally {
        if (!structuredLogStream.closed) {
            await new Promise(resolve => structuredLogStream.end(resolve));
        }
    }
    let structuredLogTail = '';
    try {
        structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
    }
    catch {
        // ignore
    }
    log('codex_stream_complete', {
        runtime: 'codex-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
    });
    return {
        output: finalResponse.trim(),
        providerSessionId: thread.id ?? undefined,
        structuredLogPath,
        structuredLogTail,
    };
}
function processClaudeStructuredMessage(message, options) {
    const type = typeof message.type === 'string' ? message.type : 'unknown';
    log('claude_message', {
        runtime: 'claude-agent-sdk',
        model: options.model,
        session_id: options.sessionId,
        message_type: type,
        subtype: typeof message.subtype === 'string' ? message.subtype : null,
        parent_tool_use_id: typeof message.parent_tool_use_id === 'string' ? message.parent_tool_use_id : null,
        content: summarizeUnknown(message, 1200) ?? null,
    });
}
async function runClaudeStructuredQuery(streamFactory, options) {
    const runtimeHome = resolveOpenClaudeHome(options.workingDirectory);
    const debugDir = path.join(runtimeHome, '.daemon-logs');
    await mkdir(debugDir, { recursive: true });
    const structuredLogPath = path.join(debugDir, `claude-${options.sessionId}-${Date.now()}-stream.jsonl`);
    const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' });
    const messages = [];
    log('claude_stream_start', {
        runtime: 'claude-agent-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
    });
    try {
        for await (const message of streamFactory()) {
            messages.push(message);
            structuredLogStream.write(`${JSON.stringify(message)}\n`);
            processClaudeStructuredMessage(message, options);
        }
    }
    catch (error) {
        await new Promise(resolve => structuredLogStream.end(resolve));
        let structuredLogTail = '';
        try {
            structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
        }
        catch {
            // ignore
        }
        log('claude_stream_error', {
            runtime: 'claude-agent-sdk',
            model: options.model,
            session_id: options.sessionId,
            structured_log_path: structuredLogPath,
            error: error instanceof Error ? error.message : String(error),
        });
        throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
            structuredLogPath,
            structuredLogTail,
        });
    }
    finally {
        if (!structuredLogStream.closed) {
            await new Promise(resolve => structuredLogStream.end(resolve));
        }
    }
    let structuredLogTail = '';
    try {
        structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
    }
    catch {
        // ignore
    }
    log('claude_stream_complete', {
        runtime: 'claude-agent-sdk',
        model: options.model,
        session_id: options.sessionId,
        structured_log_path: structuredLogPath,
    });
    return { messages, structuredLogPath, structuredLogTail };
}
function shouldReflect(request) {
    return request.reflect === true;
}
function nextSessionState(session, providerSessionId) {
    return {
        ...session,
        providerSessionId: providerSessionId ?? session.providerSessionId,
    };
}
async function maybeReflectWithClaudeAgentSdk(model, session, taskOutput, reflectionPrompt) {
    const sessionId = session.providerSessionId ?? randomUUID();
    try {
        let text = '';
        let nextSessionId = sessionId;
        const q = query({
            prompt: buildDefaultReflectionPrompt(taskOutput, reflectionPrompt),
            options: {
                cwd: process.cwd(),
                resume: session.providerSessionId,
                model,
                permissionMode: 'bypassPermissions',
                env: process.env,
            },
        });
        for await (const message of q) {
            if (message.type === 'assistant' && Array.isArray(message.message?.content)) {
                for (const block of message.message.content) {
                    if (block.type === 'text')
                        text += block.text;
                }
            }
            if ('session_id' in message && typeof message.session_id === 'string') {
                nextSessionId = message.session_id;
            }
            if (message.type === 'result' && message.subtype === 'success' && typeof message.result === 'string') {
                text = text || message.result;
            }
        }
        const reflection = parseReflectionPayload(text.trim());
        if (!reflection) {
            return { session: nextSessionState(session, nextSessionId), errors: ['Failed to parse reflection payload'] };
        }
        return { session: nextSessionState(session, nextSessionId), reflection };
    }
    catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return { session: nextSessionState(session, sessionId), errors: [message] };
    }
}
async function maybeReflectWithCodex(threadFactory, taskOutput, reflectionPrompt) {
    try {
        const result = await threadFactory().run(buildDefaultReflectionPrompt(taskOutput, reflectionPrompt));
        const text = typeof result === 'string' ? result : result.finalResponse;
        const reflection = parseReflectionPayload(text);
        if (!reflection) {
            return { errors: ['Failed to parse reflection payload'] };
        }
        return { reflection };
    }
    catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return { errors: [message] };
    }
}
export function getOpenClaudeBinaryConfig(env = process.env) {
    return {
        command: env.OPENCLAUDE_BIN || 'openclaude',
        packageName: env.OPENCLAUDE_NPM_PACKAGE || '@gitlawb/openclaude',
    };
}
function commandExists(command) {
    const result = spawnSync(command, ['--version'], { stdio: 'ignore' });
    return result.status === 0;
}
function installOpenClaudeFromNpm(packageName) {
    const install = spawnSync('npm', ['install', '-g', packageName], { encoding: 'utf8' });
    if (install.status === 0)
        return;
    const stderr = (install.stderr || '').trim();
    const stdout = (install.stdout || '').trim();
    throw new Error(stderr || stdout || `failed to install ${packageName} with npm`);
}
function ensureOpenClaudeCommand() {
    const config = getOpenClaudeBinaryConfig();
    if (commandExists(config.command))
        return config.command;
    if (config.command !== OPENCLAUDE_BIN) {
        throw new Error(`OPENCLAUDE_BIN '${config.command}' is not executable`);
    }
    installOpenClaudeFromNpm(config.packageName);
    if (commandExists(config.command))
        return config.command;
    throw new Error(`installed ${config.packageName}, but '${config.command}' is still not executable`);
}
function resolveOpenClaudeHome(workingDirectory) {
    return workingDirectory
        ?? process.env.AGENT_HOME_DIR
        ?? process.env.HOME
        ?? process.cwd();
}
async function runOpenClaudePrint(prompt, options) {
    const env = {};
    for (const [key, value] of Object.entries(process.env)) {
        if (value !== undefined)
            env[key] = value;
    }
    const runtimeHome = resolveOpenClaudeHome(options.workingDirectory);
    const timeoutMs = Number.isFinite(options.timeoutMs)
        ? Math.max(1, options.timeoutMs)
        : undefined;
    const debugDir = path.join(runtimeHome, '.daemon-logs');
    await mkdir(debugDir, { recursive: true });
    const debugLogPath = path.join(debugDir, `openclaude-${options.sessionId}-${Date.now()}.log`);
    const structuredLogPath = path.join(debugDir, `openclaude-${options.sessionId}-${Date.now()}-stream.jsonl`);
    if (options.baseUrl)
        env.OPENAI_BASE_URL = options.baseUrl;
    if (options.apiKey)
        env.OPENAI_API_KEY = options.apiKey;
    env.OPENAI_MODEL = options.model;
    env.CLAUDE_CODE_USE_OPENAI = '1';
    env.HOME = runtimeHome;
    const args = [
        '--print',
        '--bare',
        '--verbose',
        '--output-format', 'stream-json',
        '--debug',
        '--debug-file', debugLogPath,
        '--dangerously-skip-permissions',
    ];
    args.push('--no-session-persistence', '--session-id', options.sessionId, '--model', options.model, prompt);
    const command = ensureOpenClaudeCommand();
    return await new Promise((resolve, reject) => {
        const child = spawn(command, args, {
            cwd: runtimeHome,
            env,
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        let stdout = '';
        let stderr = '';
        const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' });
        const structuredState = {
            buffer: '',
            resultText: '',
            rawLines: [],
            writeLine: line => { structuredLogStream.write(`${line}\n`); },
        };
        let settled = false;
        let timedOut = false;
        const timeoutHandle = timeoutMs
            ? setTimeout(() => {
                timedOut = true;
                log('harness_timeout', {
                    runtime: 'openclaude-harness',
                    model: options.model,
                    session_id: options.sessionId,
                    pid: child.pid ?? null,
                    timeout_ms: timeoutMs,
                    debug_log_path: debugLogPath,
                    structured_log_path: structuredLogPath,
                });
                child.kill('SIGKILL');
            }, timeoutMs)
            : undefined;
        log('harness_spawn', {
            runtime: 'openclaude-harness',
            model: options.model,
            session_id: options.sessionId,
            pid: child.pid ?? null,
            cwd: runtimeHome,
            debug_log_path: debugLogPath,
            structured_log_path: structuredLogPath,
            timeout_ms: timeoutMs ?? null,
        });
        child.stdout.on('data', chunk => {
            const chunkText = chunk.toString();
            stdout += chunkText;
            consumeOpenClaudeStructuredChunk(structuredState, chunkText, options);
        });
        child.stderr.on('data', chunk => { stderr += chunk.toString(); });
        child.on('error', async (error) => {
            if (settled)
                return;
            settled = true;
            if (timeoutHandle)
                clearTimeout(timeoutHandle);
            finalizeOpenClaudeStructuredStream(structuredState, options);
            await new Promise(resolve => structuredLogStream.end(resolve));
            let debugLogTail = '';
            let structuredLogTail = '';
            try {
                debugLogTail = (await readFile(debugLogPath, 'utf8')).slice(-4000);
            }
            catch {
                // ignore
            }
            try {
                structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
            }
            catch {
                // ignore
            }
            log('harness_exit', {
                runtime: 'openclaude-harness',
                model: options.model,
                session_id: options.sessionId,
                pid: child.pid ?? null,
                exit_code: null,
                timed_out: timedOut,
                debug_log_path: debugLogPath,
                structured_log_path: structuredLogPath,
                error: error.message,
            });
            reject(Object.assign(error, {
                stderr,
                stdout: structuredState.resultText || stdout,
                debugLogPath,
                debugLogTail,
                structuredLogPath,
                structuredLogTail,
            }));
        });
        child.on('close', async (code, signal) => {
            if (settled)
                return;
            settled = true;
            if (timeoutHandle)
                clearTimeout(timeoutHandle);
            finalizeOpenClaudeStructuredStream(structuredState, options);
            await new Promise(resolve => structuredLogStream.end(resolve));
            let debugLogTail = '';
            let structuredLogTail = '';
            try {
                debugLogTail = (await readFile(debugLogPath, 'utf8')).slice(-4000);
            }
            catch {
                // ignore
            }
            try {
                structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
            }
            catch {
                // ignore
            }
            log('harness_exit', {
                runtime: 'openclaude-harness',
                model: options.model,
                session_id: options.sessionId,
                pid: child.pid ?? null,
                exit_code: code ?? null,
                signal: signal ?? null,
                timed_out: timedOut,
                debug_log_path: debugLogPath,
                structured_log_path: structuredLogPath,
            });
            if (code !== 0) {
                const error = Object.assign(new Error(timedOut
                    ? `openclaude timed out after ${timeoutMs}ms`
                    : (stderr.trim() || `openclaude exited with code ${code}`)), {
                    stderr,
                    stdout: structuredState.resultText || stdout,
                    exitCode: code ?? undefined,
                    signal: signal ?? undefined,
                    debugLogPath,
                    debugLogTail,
                    structuredLogPath,
                    structuredLogTail,
                });
                reject(error);
                return;
            }
            const resultText = structuredState.resultText || stdout.trim();
            resolve(resultText);
        });
    });
}
async function maybeReflectWithOpenClaude(taskOutput, options, reflectionPrompt) {
    try {
        const text = await runOpenClaudePrint(buildDefaultReflectionPrompt(taskOutput, reflectionPrompt), options);
        const reflection = parseReflectionPayload(text);
        if (!reflection) {
            return { errors: ['Failed to parse reflection payload'] };
        }
        return { reflection };
    }
    catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return { errors: [message] };
    }
}
export class ClaudeAgentSdkAdapter {
    model;
    apiKey;
    constructor(model, apiKey) {
        this.model = model;
        this.apiKey = apiKey;
    }
    async startOrResumeWarmSession(session) {
        return nextSessionState(session, session.providerSessionId ?? randomUUID());
    }
    async executePrompt(session, request) {
        if (!this.apiKey) {
            return { session, result: errorResult('BACKEND_API_KEY is not configured for Claude runtime') };
        }
        const sessionId = session.providerSessionId ?? randomUUID();
        const env = {
            ...process.env,
            ANTHROPIC_API_KEY: this.apiKey,
        };
        try {
            let text = '';
            let nextSessionId = sessionId;
            const { messages } = await runClaudeStructuredQuery(() => query({
                prompt: request.prompt,
                options: {
                    cwd: process.cwd(),
                    resume: session.providerSessionId,
                    model: this.model,
                    permissionMode: 'bypassPermissions',
                    env,
                },
            }), {
                model: this.model,
                sessionId,
                workingDirectory: process.cwd(),
            });
            for (const message of messages) {
                const messageRecord = message;
                const content = messageRecord.message?.content;
                if (messageRecord.type === 'assistant' && Array.isArray(content)) {
                    for (const block of content) {
                        if (block.type === 'text')
                            text += block.text;
                    }
                }
                if (typeof messageRecord.session_id === 'string') {
                    nextSessionId = messageRecord.session_id;
                }
                if (messageRecord.type === 'result' && messageRecord.subtype === 'success' && typeof messageRecord.result === 'string') {
                    text = text || messageRecord.result;
                }
            }
            const baseResult = enforceAlfredDirectIntentContract(request, successResult(text.trim()));
            const nextSession = nextSessionState(session, nextSessionId);
            if (!shouldReflect(request)) {
                return { session: nextSession, result: baseResult };
            }
            const reflectionResult = await maybeReflectWithClaudeAgentSdk(this.model, nextSession, baseResult.output, request.reflection_prompt);
            return {
                session: reflectionResult.session,
                result: finalizeRuntimeResult(baseResult, reflectionResult),
            };
        }
        catch (error) {
            return { session: nextSessionState(session, sessionId), result: errorResultFromError(error) };
        }
    }
    async interruptActiveExecution(_session) {
        // Query.interrupt wiring can be added once the daemon keeps active Query instances per sender.
    }
}
export class CodexSdkAdapter {
    codex;
    model;
    skipGitRepoCheck;
    workingDirectory;
    constructor(model, options) {
        const env = {};
        for (const [key, value] of Object.entries(process.env)) {
            if (value !== undefined && key !== 'OPENAI_BASE_URL') {
                env[key] = value;
            }
        }
        this.codex = new Codex({
            apiKey: options.apiKey,
            baseUrl: options.baseUrl,
            env,
        });
        this.model = model;
        this.skipGitRepoCheck = options.skipGitRepoCheck;
        this.workingDirectory = options.workingDirectory;
    }
    async startOrResumeWarmSession(session) {
        return session;
    }
    async executePrompt(session, request) {
        try {
            const threadOptions = {
                model: this.model,
                skipGitRepoCheck: this.skipGitRepoCheck,
                workingDirectory: this.workingDirectory,
            };
            const thread = session.providerSessionId
                ? this.codex.resumeThread(session.providerSessionId, threadOptions)
                : this.codex.startThread(threadOptions);
            const sessionId = session.providerSessionId ?? randomUUID();
            const runResult = await runCodexStructuredTurn(() => thread, request.prompt, {
                model: this.model,
                sessionId,
                workingDirectory: this.workingDirectory,
            });
            const output = runResult.output;
            const nextSession = nextSessionState(session, runResult.providerSessionId ?? thread.id ?? session.providerSessionId);
            const baseResult = enforceAlfredDirectIntentContract(request, successResult(output));
            if (!shouldReflect(request)) {
                return { session: nextSession, result: baseResult };
            }
            const reflectionResult = await maybeReflectWithCodex(() => {
                const reflectionThread = nextSession.providerSessionId
                    ? this.codex.resumeThread(nextSession.providerSessionId, threadOptions)
                    : this.codex.startThread(threadOptions);
                return reflectionThread;
            }, output, request.reflection_prompt);
            return {
                session: nextSession,
                result: finalizeRuntimeResult(baseResult, reflectionResult),
            };
        }
        catch (error) {
            return { session, result: errorResultFromError(error) };
        }
    }
    async interruptActiveExecution(_session) {
        // Codex interruption semantics will be added later.
    }
}
export class OpenClaudeHarnessAdapter {
    model;
    baseUrl;
    apiKey;
    workingDirectory;
    constructor(model, options) {
        this.model = model;
        this.baseUrl = options.baseUrl;
        this.apiKey = options.apiKey;
        this.workingDirectory = options.workingDirectory;
    }
    async startOrResumeWarmSession(session) {
        return nextSessionState(session, session.providerSessionId ?? randomUUID());
    }
    async executePrompt(session, request) {
        const sessionId = session.providerSessionId ?? randomUUID();
        const nextSession = nextSessionState(session, sessionId);
        try {
            const output = await runOpenClaudePrint(request.prompt, {
                model: this.model,
                sessionId,
                baseUrl: this.baseUrl,
                apiKey: this.apiKey,
                workingDirectory: this.workingDirectory,
                timeoutMs: request.timeout_ms,
            });
            const baseResult = enforceAlfredDirectIntentContract(request, successResult(output));
            if (!shouldReflect(request)) {
                return { session: nextSession, result: baseResult };
            }
            const reflectionResult = await maybeReflectWithOpenClaude(output, {
                model: this.model,
                sessionId,
                baseUrl: this.baseUrl,
                apiKey: this.apiKey,
                workingDirectory: this.workingDirectory,
            }, request.reflection_prompt);
            return {
                session: nextSession,
                result: finalizeRuntimeResult(baseResult, reflectionResult),
            };
        }
        catch (error) {
            return { session: nextSession, result: errorResultFromError(error) };
        }
    }
    async interruptActiveExecution(_session) {
        // Harness interruption wiring can be added later.
    }
}
export function createProviderAdapter(executionProfile) {
    if (executionProfile.runtime === 'claude-agent-sdk') {
        return new ClaudeAgentSdkAdapter(executionProfile.model, executionProfile.apiKey);
    }
    if (executionProfile.runtime === 'openclaude-harness') {
        return new OpenClaudeHarnessAdapter(executionProfile.model, {
            baseUrl: executionProfile.baseUrl,
            apiKey: executionProfile.apiKey,
            workingDirectory: executionProfile.workingDirectory,
        });
    }
    return new CodexSdkAdapter(executionProfile.model, {
        apiKey: executionProfile.apiKey,
        baseUrl: executionProfile.baseUrl,
        skipGitRepoCheck: executionProfile.skipGitRepoCheck ?? false,
        workingDirectory: executionProfile.workingDirectory,
    });
}
