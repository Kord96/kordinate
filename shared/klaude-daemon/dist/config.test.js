import assert from 'node:assert/strict';
import test from 'node:test';
import { loadDaemonConfig, resolveRuntimeForModel } from './config.js';
test('loadDaemonConfig defaults to openai via codex sdk', () => {
    const previous = { ...process.env };
    for (const key of [
        'DAEMON_PROVIDER', 'DAEMON_RUNTIME', 'DAEMON_MODEL',
        'BACKEND_API_KEY', 'BACKEND_BASE_URL',
        'CODEX_SKIP_GIT_REPO_CHECK', 'CODEX_WORKING_DIRECTORY',
        'KAFKA_BROKERS', 'REFLECTIONS_TOPIC', 'DISCOVERY_SERVER_URL',
        'DISCOVERY_PUBLISH_INTERVAL_MS', 'DAEMON_HEALTH_URL',
        'DAEMON_STATE_DIR', 'DAEMON_SESSION_MAP_PATH',
    ])
        delete process.env[key];
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'openai',
        runtime: 'codex-sdk',
        model: 'gpt-5.4',
        apiKey: undefined,
        baseUrl: undefined,
        skipGitRepoCheck: false,
        workingDirectory: undefined,
    });
    assert.deepEqual(config.kafkaBrokers, ['localhost:9092']);
    assert.equal(config.reflectionsTopic, 'reflections');
    assert.equal(config.discoveryServerUrl, undefined);
    assert.equal(config.discoveryPublishIntervalMs, 30000);
    assert.equal(config.healthUrl, undefined);
    assert.equal(config.stateDir, '.daemon-state');
    assert.equal(config.sessionMapPath, '.daemon-state/sessions.json');
    process.env = previous;
});
test('loadDaemonConfig supports claude execution profile', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'anthropic';
    process.env.DAEMON_RUNTIME = 'claude-agent-sdk';
    process.env.DAEMON_MODEL = 'claude-sonnet-4-6';
    delete process.env.BACKEND_API_KEY;
    process.env.ANTHROPIC_API_KEY = 'anthropic-key';
    process.env.BACKEND_BASE_URL = 'https://api.anthropic.com';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'anthropic',
        runtime: 'claude-agent-sdk',
        model: 'claude-sonnet-4-6',
        apiKey: 'anthropic-key',
        baseUrl: 'https://api.anthropic.com',
    });
    process.env = previous;
});
test('loadDaemonConfig supports openclaude harness openai api key fallback', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'openai';
    process.env.DAEMON_RUNTIME = 'openclaude-harness';
    process.env.DAEMON_MODEL = 'gpt-5.4';
    delete process.env.BACKEND_API_KEY;
    process.env.OPENAI_API_KEY = 'openai-key';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'openai',
        runtime: 'openclaude-harness',
        model: 'gpt-5.4',
        apiKey: 'openai-key',
        baseUrl: undefined,
        workingDirectory: undefined,
    });
    process.env = previous;
});
test('loadDaemonConfig supports codex execution profile overrides', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'openai';
    process.env.DAEMON_RUNTIME = 'codex-sdk';
    process.env.DAEMON_MODEL = 'gpt-5.3-codex';
    process.env.BACKEND_API_KEY = 'codex-key';
    process.env.BACKEND_BASE_URL = 'https://proxy.example.com/v1';
    process.env.CODEX_SKIP_GIT_REPO_CHECK = 'true';
    process.env.CODEX_WORKING_DIRECTORY = '/tmp/workdir';
    process.env.KAFKA_BROKERS = 'kafka-a:9092,kafka-b:9092';
    process.env.DISCOVERY_SERVER_URL = 'http://discovery.internal';
    process.env.DISCOVERY_PUBLISH_INTERVAL_MS = '45000';
    process.env.DAEMON_HEALTH_URL = 'http://agent-charon:9090/health';
    process.env.DAEMON_STATE_DIR = '/var/lib/klaude-daemon';
    process.env.DAEMON_SESSION_MAP_PATH = '/var/lib/klaude-daemon/sessions.json';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'openai',
        runtime: 'codex-sdk',
        model: 'gpt-5.3-codex',
        apiKey: 'codex-key',
        baseUrl: 'https://proxy.example.com/v1',
        skipGitRepoCheck: true,
        workingDirectory: '/tmp/workdir',
    });
    assert.deepEqual(config.kafkaBrokers, ['kafka-a:9092', 'kafka-b:9092']);
    assert.equal(config.discoveryServerUrl, 'http://discovery.internal');
    assert.equal(config.discoveryPublishIntervalMs, 45000);
    assert.equal(config.healthUrl, 'http://agent-charon:9090/health');
    assert.equal(config.stateDir, '/var/lib/klaude-daemon');
    assert.equal(config.sessionMapPath, '/var/lib/klaude-daemon/sessions.json');
    process.env = previous;
});
test('loadDaemonConfig maps legacy alfred-direct runtime to simple-harness', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'fireworks';
    process.env.DAEMON_RUNTIME = 'alfred-direct';
    process.env.DAEMON_MODEL = 'accounts/fireworks/models/gpt-oss-20b';
    process.env.BACKEND_API_KEY = 'fireworks-key';
    process.env.BACKEND_BASE_URL = 'https://api.fireworks.ai/inference/v1';
    process.env.CODEX_WORKING_DIRECTORY = '/runtime/alfred-gpt-oss-20b';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'fireworks',
        runtime: 'simple-harness',
        model: 'accounts/fireworks/models/gpt-oss-20b',
        apiKey: 'fireworks-key',
        baseUrl: 'https://api.fireworks.ai/inference/v1',
        workingDirectory: '/runtime/alfred-gpt-oss-20b',
    });
    process.env = previous;
});
test('loadDaemonConfig supports deepseek through codex sdk', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'deepseek';
    process.env.DAEMON_RUNTIME = 'codex-sdk';
    process.env.BACKEND_API_KEY = 'deepseek-key';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'deepseek',
        runtime: 'codex-sdk',
        model: 'deepseek-chat',
        apiKey: 'deepseek-key',
        baseUrl: 'https://api.deepseek.com/v1',
        skipGitRepoCheck: false,
        workingDirectory: undefined,
    });
    process.env = previous;
});
test('resolveRuntimeForModel maps model families to the expected runtimes', () => {
    assert.equal(resolveRuntimeForModel('gpt-5.4', 'openai'), 'codex-sdk');
    assert.equal(resolveRuntimeForModel('gpt-5.3-codex', 'openai'), 'codex-sdk');
    assert.equal(resolveRuntimeForModel('claude-sonnet-4-6', 'anthropic'), 'claude-agent-sdk');
    assert.equal(resolveRuntimeForModel('sonnet', 'anthropic'), 'claude-agent-sdk');
    assert.equal(resolveRuntimeForModel('haiku', 'anthropic'), 'claude-agent-sdk');
    assert.equal(resolveRuntimeForModel('deepseek-reasoner', 'deepseek'), 'openclaude-harness');
    assert.equal(resolveRuntimeForModel('gemini-3.1-pro-preview', 'gemini'), 'openclaude-harness');
    assert.equal(resolveRuntimeForModel('accounts/fireworks/models/glm-5', 'fireworks'), 'openclaude-harness');
});
test('loadDaemonConfig defaults non-claude non-gpt models to openclaude harness', () => {
    const previous = { ...process.env };
    process.env.DAEMON_PROVIDER = 'deepseek';
    process.env.DAEMON_MODEL = 'deepseek-reasoner';
    delete process.env.DAEMON_RUNTIME;
    process.env.BACKEND_API_KEY = 'deepseek-key';
    const config = loadDaemonConfig();
    assert.deepEqual(config.executionProfile, {
        provider: 'deepseek',
        runtime: 'openclaude-harness',
        model: 'deepseek-reasoner',
        apiKey: 'deepseek-key',
        baseUrl: 'https://api.deepseek.com/v1',
        workingDirectory: undefined,
    });
    process.env = previous;
});
test('updateSessionAfterRequest stores latest correlation id', async () => {
    const { updateSessionAfterRequest } = await import('./protocol.js');
    const updated = updateSessionAfterRequest({ key: 'agent-a', providerSessionId: 'thread-1' }, { type: 'request', sender: 'agent-a', correlation_id: 'corr-2', prompt: 'hello' });
    assert.deepEqual(updated, {
        key: 'agent-a',
        providerSessionId: 'thread-1',
        lastCorrelationId: 'corr-2',
    });
});
