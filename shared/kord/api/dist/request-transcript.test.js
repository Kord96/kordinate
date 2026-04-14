import test from 'node:test';
import assert from 'node:assert/strict';
import { buildTranscriptEventFromGateway, buildTranscriptEventFromProgress, coalesceTranscriptEvent } from './request-transcript.js';
test('gateway timeout normalizes to request.timed_out transcript event', () => {
    const event = buildTranscriptEventFromGateway('req-1', {
        event: 'prompt_timeout',
        timestamp: '2026-04-14T00:02:00.000Z',
        resolved_agent: 'generic-opus',
        timeout_ms: 120000,
    });
    assert.equal(event?.type, 'request.timed_out');
    assert.equal(event?.agent_may_continue, true);
    assert.equal(event?.timeout_ms, 120000);
});
test('low-signal tool use becomes a single agent.update', () => {
    const progress = {
        type: 'progress',
        sender: 'generic-opus',
        correlation_id: 'req-2',
        timestamp: '2026-04-14T00:00:10.000Z',
        event: {
            source: 'provider',
            kind: 'assistant',
            runtime: 'claude-agent-sdk',
            model: 'opus',
            payload: {
                message: {
                    content: [
                        { type: 'tool_use', name: 'Read', input: { file_path: '/tmp/foo' } },
                    ],
                },
            },
        },
    };
    const event = buildTranscriptEventFromProgress(progress);
    assert.equal(event?.type, 'agent.update');
    assert.equal(event?.message, 'agent is gathering context');
});
test('duplicate transcript events are coalesced', () => {
    const left = {
        type: 'agent.update',
        at: '2026-04-14T00:00:00.000Z',
        request_id: 'req-3',
        message: 'agent is gathering context',
    };
    const right = {
        type: 'agent.update',
        at: '2026-04-14T00:00:01.000Z',
        request_id: 'req-3',
        message: 'agent is gathering context',
    };
    assert.equal(coalesceTranscriptEvent(left, right), true);
});
