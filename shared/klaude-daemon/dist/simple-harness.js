import { randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { createWriteStream } from 'node:fs';
import path from 'node:path';
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import { log } from './log.js';
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
function successResult(output) {
    return {
        status: 'success',
        output,
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
function errorResultFromError(error) {
    const details = formatProviderError(error);
    return {
        status: 'error',
        output: details[0] ?? 'unknown provider error',
        errors: details,
    };
}
function nextSessionState(session, providerSessionId) {
    return {
        ...session,
        providerSessionId: providerSessionId ?? session.providerSessionId,
    };
}
function shouldReflect(request) {
    return request.reflect === true;
}
function isAlfredRuntimeContext() {
    const profile = (process.env.AGENT_PROFILE_NAME ?? '').trim().toLowerCase();
    const name = (process.env.AGENT_NAME ?? '').trim().toLowerCase();
    return profile === 'alfred' || name.startsWith('alfred');
}
export function classifyAlfredDirectIntent(prompt) {
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
function resolveOriginalPrompt(request) {
    return request.raw_prompt?.trim() || request.prompt.trim();
}
function resolveWorkingDirectory(request, fallback) {
    return request.working_dir ?? fallback ?? process.env.AGENT_HOME_DIR ?? process.cwd();
}
function shellSingleQuote(value) {
    return `'${value.replace(/'/g, `'\"'\"'`)}'`;
}
async function runBashCommand(options) {
    return await new Promise((resolve, reject) => {
        const child = spawn('/bin/bash', ['-lc', options.command], {
            cwd: options.cwd,
            env: {
                ...process.env,
                ...(options.env ?? {}),
            },
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        let stdout = '';
        let stderr = '';
        const timeoutHandle = options.timeoutMs
            ? setTimeout(() => child.kill('SIGKILL'), options.timeoutMs)
            : undefined;
        child.stdout.on('data', chunk => { stdout += chunk.toString(); });
        child.stderr.on('data', chunk => { stderr += chunk.toString(); });
        child.on('error', error => {
            if (timeoutHandle)
                clearTimeout(timeoutHandle);
            reject(Object.assign(error, { stdout, stderr }));
        });
        child.on('close', code => {
            if (timeoutHandle)
                clearTimeout(timeoutHandle);
            if (code === 0) {
                resolve({ stdout, stderr });
                return;
            }
            reject(Object.assign(new Error(stderr.trim() || stdout.trim() || `command failed with exit ${code}`), {
                stdout,
                stderr,
                exitCode: code ?? undefined,
            }));
        });
    });
}
function passEnv() {
    const env = {};
    if (process.env.PASSWORD_STORE_DIR)
        env.PASSWORD_STORE_DIR = process.env.PASSWORD_STORE_DIR;
    if (process.env.GNUPGHOME)
        env.GNUPGHOME = process.env.GNUPGHOME;
    return env;
}
async function passShow(keyPath, cwd) {
    const { stdout } = await runBashCommand({
        command: `pass show ${shellSingleQuote(keyPath)}`,
        cwd,
        env: passEnv(),
        timeoutMs: 10000,
    });
    return stdout.trimEnd();
}
async function passInsert(keyPath, value, cwd) {
    await runBashCommand({
        command: `printf '%s\\n' ${shellSingleQuote(value)} | pass insert -m -f ${shellSingleQuote(keyPath)}`,
        cwd,
        env: passEnv(),
        timeoutMs: 10000,
    });
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
export function enforceAlfredDirectIntentContract(request, result) {
    if (!isAlfredRuntimeContext() || result.status !== 'success')
        return result;
    const intent = classifyAlfredDirectIntent(resolveOriginalPrompt(request));
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
async function callOpenAiChatCompletion(options) {
    if (!options.apiKey) {
        throw new Error('BACKEND_API_KEY is not configured for simple harness runtime');
    }
    const baseUrl = (options.baseUrl ?? 'https://api.openai.com/v1').replace(/\/$/, '');
    const controller = new AbortController();
    const timeoutHandle = options.timeoutMs
        ? setTimeout(() => controller.abort(), options.timeoutMs)
        : undefined;
    try {
        const response = await fetch(`${baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'content-type': 'application/json',
                authorization: `Bearer ${options.apiKey}`,
            },
            body: JSON.stringify({
                model: options.model,
                messages: options.messages,
                tools: options.tools,
                tool_choice: options.tools && options.tools.length > 0 ? 'auto' : undefined,
                temperature: 0,
            }),
            signal: controller.signal,
        });
        const json = await response.json();
        if (!response.ok) {
            throw new Error(summarizeUnknown(json, 1600) ?? `chat completion failed with status ${response.status}`);
        }
        return json;
    }
    finally {
        if (timeoutHandle)
            clearTimeout(timeoutHandle);
    }
}
function simpleHarnessTools() {
    return [
        {
            type: 'function',
            function: {
                name: 'read_file',
                description: 'Read the contents of a UTF-8 text file',
                parameters: {
                    type: 'object',
                    properties: { path: { type: 'string' } },
                    required: ['path'],
                    additionalProperties: false,
                },
            },
        },
        {
            type: 'function',
            function: {
                name: 'write_file',
                description: 'Write UTF-8 text to a file path',
                parameters: {
                    type: 'object',
                    properties: {
                        path: { type: 'string' },
                        content: { type: 'string' },
                    },
                    required: ['path', 'content'],
                    additionalProperties: false,
                },
            },
        },
        {
            type: 'function',
            function: {
                name: 'list_dir',
                description: 'List files and directories for one path',
                parameters: {
                    type: 'object',
                    properties: { path: { type: 'string' } },
                    required: ['path'],
                    additionalProperties: false,
                },
            },
        },
        {
            type: 'function',
            function: {
                name: 'pass_show',
                description: 'Read a secret from the shared pass store',
                parameters: {
                    type: 'object',
                    properties: { key_path: { type: 'string' } },
                    required: ['key_path'],
                    additionalProperties: false,
                },
            },
        },
        {
            type: 'function',
            function: {
                name: 'pass_insert',
                description: 'Store a secret in the shared pass store and overwrite if it already exists',
                parameters: {
                    type: 'object',
                    properties: {
                        key_path: { type: 'string' },
                        value: { type: 'string' },
                    },
                    required: ['key_path', 'value'],
                    additionalProperties: false,
                },
            },
        },
    ];
}
async function executeSimpleHarnessToolCall(call, cwd) {
    switch (call.name) {
        case 'read_file': {
            const target = String(call.arguments.path ?? '');
            return await readFile(path.isAbsolute(target) ? target : path.join(cwd, target), 'utf8');
        }
        case 'write_file': {
            const target = String(call.arguments.path ?? '');
            const content = String(call.arguments.content ?? '');
            const absolute = path.isAbsolute(target) ? target : path.join(cwd, target);
            await mkdir(path.dirname(absolute), { recursive: true });
            await writeFile(absolute, content, 'utf8');
            return 'written';
        }
        case 'list_dir': {
            const target = String(call.arguments.path ?? '');
            const absolute = path.isAbsolute(target) ? target : path.join(cwd, target);
            const entries = await readdir(absolute, { withFileTypes: true });
            const payload = await Promise.all(entries.map(async (entry) => {
                const full = path.join(absolute, entry.name);
                const info = await stat(full);
                return {
                    name: entry.name,
                    type: entry.isDirectory() ? 'dir' : entry.isFile() ? 'file' : 'other',
                    size: info.size,
                };
            }));
            return JSON.stringify(payload);
        }
        case 'pass_show':
            return await passShow(String(call.arguments.key_path ?? ''), cwd);
        case 'pass_insert':
            await passInsert(String(call.arguments.key_path ?? ''), String(call.arguments.value ?? ''), cwd);
            return 'stored';
    }
}
async function runDirectIntent(request, options) {
    const runtimeHome = resolveWorkingDirectory(request, options.workingDirectory);
    const debugDir = path.join(runtimeHome, '.daemon-logs');
    await mkdir(debugDir, { recursive: true });
    const structuredLogPath = path.join(debugDir, `simple-harness-${options.sessionId}-${Date.now()}-stream.jsonl`);
    const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' });
    const writeEvent = (event) => {
        structuredLogStream.write(`${JSON.stringify(event)}\n`);
    };
    const originalPrompt = resolveOriginalPrompt(request);
    const intent = classifyAlfredDirectIntent(originalPrompt);
    const cwd = resolveWorkingDirectory(request, options.workingDirectory);
    if (!intent) {
        await new Promise(resolve => structuredLogStream.end(resolve));
        throw new Error('unsupported direct Alfred intent');
    }
    try {
        writeEvent({
            type: 'system',
            subtype: 'init',
            runtime: 'simple-harness',
            cwd,
            session_id: options.sessionId,
            intent: intent.kind,
        });
        if (intent.kind === 'get_secret') {
            writeEvent({
                type: 'assistant',
                message: {
                    role: 'assistant',
                    content: [{ type: 'tool_use', name: 'pass_show', input: { key_path: intent.keyPath } }],
                },
            });
            const output = await passShow(intent.keyPath, cwd);
            writeEvent({
                type: 'user',
                message: {
                    role: 'user',
                    content: [{ type: 'tool_result', tool_name: 'pass_show', key_path: intent.keyPath, output }],
                },
            });
            writeEvent({ type: 'result', subtype: 'success', result: output });
            await new Promise(resolve => structuredLogStream.end(resolve));
            const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
            return { output, structuredLogPath, structuredLogTail };
        }
        writeEvent({
            type: 'assistant',
            message: {
                role: 'assistant',
                content: [{ type: 'tool_use', name: 'pass_insert', input: { key_path: intent.keyPath } }],
            },
        });
        await passInsert(intent.keyPath, intent.value, cwd);
        writeEvent({
            type: 'user',
            message: {
                role: 'user',
                content: [{ type: 'tool_result', tool_name: 'pass_insert', key_path: intent.keyPath, output: 'stored' }],
            },
        });
        const verified = await passShow(intent.keyPath, cwd);
        writeEvent({
            type: 'assistant',
            message: {
                role: 'assistant',
                content: [{ type: 'tool_use', name: 'pass_show', input: { key_path: intent.keyPath } }],
            },
        });
        writeEvent({
            type: 'user',
            message: {
                role: 'user',
                content: [{ type: 'tool_result', tool_name: 'pass_show', key_path: intent.keyPath, output: verified }],
            },
        });
        writeEvent({ type: 'result', subtype: 'success', result: 'stored' });
        await new Promise(resolve => structuredLogStream.end(resolve));
        const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
        return { output: 'stored', structuredLogPath, structuredLogTail };
    }
    catch (error) {
        writeEvent({
            type: 'result',
            subtype: 'error',
            error: error instanceof Error ? error.message : String(error),
        });
        await new Promise(resolve => structuredLogStream.end(resolve));
        let structuredLogTail = '';
        try {
            structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
        }
        catch {
            // ignore
        }
        throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
            structuredLogPath,
            structuredLogTail,
        });
    }
}
async function runToolLoop(request, options) {
    const runtimeHome = resolveWorkingDirectory(request, options.workingDirectory);
    const debugDir = path.join(runtimeHome, '.daemon-logs');
    await mkdir(debugDir, { recursive: true });
    const structuredLogPath = path.join(debugDir, `simple-harness-${options.sessionId}-${Date.now()}-stream.jsonl`);
    const structuredLogStream = createWriteStream(structuredLogPath, { flags: 'a' });
    const writeEvent = (event) => {
        structuredLogStream.write(`${JSON.stringify(event)}\n`);
    };
    const cwd = resolveWorkingDirectory(request, options.workingDirectory);
    const messages = [
        {
            role: 'system',
            content: 'You are a constrained operator. Use the provided tools to read files, write files, and read or store secrets through pass. Respond tersely and only after performing the necessary action.',
        },
        {
            role: 'user',
            content: request.prompt,
        },
    ];
    const tools = simpleHarnessTools();
    try {
        writeEvent({ type: 'system', subtype: 'init', runtime: 'simple-harness', cwd, session_id: options.sessionId, model: options.model });
        for (let step = 0; step < 8; step += 1) {
            const response = await callOpenAiChatCompletion({
                model: options.model,
                apiKey: options.apiKey,
                baseUrl: options.baseUrl,
                messages,
                tools,
                timeoutMs: request.timeout_ms,
            });
            writeEvent({ type: 'assistant', message: response });
            const choice = Array.isArray(response.choices) ? response.choices[0] : undefined;
            const message = choice && typeof choice === 'object' ? choice.message : undefined;
            const toolCalls = Array.isArray(message?.tool_calls) ? message.tool_calls : [];
            if (toolCalls.length === 0) {
                const content = typeof message?.content === 'string'
                    ? message.content
                    : Array.isArray(message?.content)
                        ? message.content.map(item => typeof item === 'string' ? item : summarizeUnknown(item, 400) ?? '').join('\n').trim()
                        : '';
                writeEvent({ type: 'result', subtype: 'success', result: content });
                await new Promise(resolve => structuredLogStream.end(resolve));
                const structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
                return { output: content.trim(), structuredLogPath, structuredLogTail };
            }
            messages.push({
                role: 'assistant',
                content: message?.content ?? '',
                tool_calls: toolCalls,
            });
            for (const toolCallRaw of toolCalls) {
                const fn = toolCallRaw.function;
                const name = String(fn?.name ?? '');
                const id = String(toolCallRaw.id ?? randomUUID());
                let args = {};
                try {
                    args = JSON.parse(String(fn?.arguments ?? '{}'));
                }
                catch {
                    args = {};
                }
                writeEvent({ type: 'tool_use', id, name, arguments: args });
                const output = await executeSimpleHarnessToolCall({ id, name, arguments: args }, cwd);
                writeEvent({ type: 'tool_result', id, name, output: summarizeText(output, 1200) });
                messages.push({
                    role: 'tool',
                    tool_call_id: id,
                    content: output,
                });
            }
        }
        throw new Error('simple harness exceeded maximum steps');
    }
    catch (error) {
        writeEvent({ type: 'result', subtype: 'error', error: error instanceof Error ? error.message : String(error) });
        await new Promise(resolve => structuredLogStream.end(resolve));
        let structuredLogTail = '';
        try {
            structuredLogTail = (await readFile(structuredLogPath, 'utf8')).slice(-4000);
        }
        catch {
            // ignore
        }
        throw Object.assign(error instanceof Error ? error : new Error(String(error)), {
            structuredLogPath,
            structuredLogTail,
        });
    }
}
async function maybeReflectWithSimpleHarness(taskOutput, options, reflectionPrompt) {
    try {
        const response = await callOpenAiChatCompletion({
            model: options.model,
            apiKey: options.apiKey,
            baseUrl: options.baseUrl,
            messages: [
                { role: 'system', content: 'Return strict JSON only.' },
                { role: 'user', content: buildDefaultReflectionPrompt(taskOutput, reflectionPrompt) },
            ],
            timeoutMs: 15000,
        });
        const choice = Array.isArray(response.choices) ? response.choices[0] : undefined;
        const message = choice && typeof choice === 'object' ? choice.message : undefined;
        const text = typeof message?.content === 'string' ? message.content : '';
        const reflection = parseReflectionPayload(text);
        if (!reflection)
            return { errors: ['Failed to parse reflection payload'] };
        return { reflection };
    }
    catch (error) {
        return { errors: [error instanceof Error ? error.message : String(error)] };
    }
}
export class SimpleHarnessAdapter {
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
        const originalPrompt = resolveOriginalPrompt(request);
        try {
            const execution = classifyAlfredDirectIntent(originalPrompt)
                ? await runDirectIntent({ ...request, raw_prompt: originalPrompt }, {
                    sessionId,
                    workingDirectory: this.workingDirectory,
                })
                : await runToolLoop(request, {
                    model: this.model,
                    apiKey: this.apiKey,
                    baseUrl: this.baseUrl,
                    sessionId,
                    workingDirectory: this.workingDirectory,
                });
            const baseResult = enforceAlfredDirectIntentContract({ ...request, raw_prompt: originalPrompt }, successResult(execution.output));
            if (!shouldReflect(request)) {
                return { session: nextSession, result: baseResult };
            }
            const reflectionResult = await maybeReflectWithSimpleHarness(baseResult.output, {
                model: this.model,
                apiKey: this.apiKey,
                baseUrl: this.baseUrl,
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
        // No-op for simple harness.
    }
}
