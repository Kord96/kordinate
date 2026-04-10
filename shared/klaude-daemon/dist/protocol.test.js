import assert from 'node:assert/strict';
import test from 'node:test';
import { buildReflectionEvent, buildResponseMessage, getOrCreateSession, isRequestMessage, sessionKeyFor } from './protocol.js';
test('isRequestMessage accepts valid request envelope', () => {
    const message = {
        type: 'request',
        sender: 'agent-a',
        correlation_id: '123',
        prompt: 'hello',
        working_dir: '/tmp/project',
    };
    assert.equal(isRequestMessage(message), true);
});
test('sessionKeyFor uses sender', () => {
    const message = {
        type: 'request',
        sender: 'agent-a',
        correlation_id: '123',
        prompt: 'hello',
    };
    assert.equal(sessionKeyFor(message), 'agent-a');
});
test('getOrCreateSession reuses session by sender', () => {
    const sessions = new Map();
    const message = {
        type: 'request',
        sender: 'agent-a',
        correlation_id: '123',
        prompt: 'hello',
    };
    const first = getOrCreateSession(sessions, message);
    const second = getOrCreateSession(sessions, message);
    assert.equal(first, second);
    assert.equal(first.key, 'agent-a');
});
test('buildResponseMessage targets original correlation and daemon sender', () => {
    const request = {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'hello',
    };
    const response = buildResponseMessage('agent-b', request, {
        status: 'success',
        output: 'done',
        errors: [],
        metadata: {
            timing: {
                received_at: '2026-04-09T00:00:00.000Z',
                started_at: '2026-04-09T00:00:00.100Z',
                completed_at: '2026-04-09T00:00:01.000Z',
                total_ms: 1000,
                session_prepare_ms: 100,
                execute_prompt_ms: 700,
                persist_sessions_ms: 200,
                publish_response_ms: 0,
            },
        },
    });
    assert.deepEqual(response, {
        type: 'response',
        sender: 'agent-b',
        correlation_id: 'corr-1',
        status: 'success',
        output: 'done',
        errors: [],
        metadata: {
            timing: {
                received_at: '2026-04-09T00:00:00.000Z',
                started_at: '2026-04-09T00:00:00.100Z',
                completed_at: '2026-04-09T00:00:01.000Z',
                total_ms: 1000,
                session_prepare_ms: 100,
                execute_prompt_ms: 700,
                persist_sessions_ms: 200,
                publish_response_ms: 0,
            },
        },
    });
});
test('buildReflectionEvent uses receiving agent and correlation id', () => {
    const request = {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'hello',
    };
    const event = buildReflectionEvent({
        agentName: 'agent-b',
        agentProfile: 'specialist',
        backendProvider: 'anthropic',
        backendRuntime: 'claude-agent-sdk',
        backendModel: 'opus',
        message: request,
        reflection: {
            project: 'project lesson',
            general: 'general lesson',
        },
    });
    assert.equal(event.agent, 'agent-b');
    assert.equal(event.agent_profile, 'specialist');
    assert.equal(event.backend_provider, 'anthropic');
    assert.equal(event.backend_runtime, 'claude-agent-sdk');
    assert.equal(event.backend_model, 'opus');
    assert.equal(event.task_id, 'corr-1');
    assert.equal(event.correlation_id, 'corr-1');
    assert.equal(event.working_dir, undefined);
    assert.equal(typeof event.captured_at, 'string');
    assert.deepEqual(event.reflection, {
        project: 'project lesson',
        general: 'general lesson',
    });
});
