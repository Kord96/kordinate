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
    const event = buildReflectionEvent('agent-b', request, {
        project: 'project lesson',
        general: 'general lesson',
    });
    assert.deepEqual(event, {
        agent: 'agent-b',
        task_id: 'corr-1',
        correlation_id: 'corr-1',
        reflection: {
            project: 'project lesson',
            general: 'general lesson',
        },
    });
});
