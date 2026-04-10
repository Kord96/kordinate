import assert from 'node:assert/strict';
import test from 'node:test';
import { formatProviderError } from './runtime.js';
test('formatProviderError preserves stderr and exit details', () => {
    const error = Object.assign(new Error('Claude Code process exited with code 1'), {
        stderr: 'Authentication failed',
        exitCode: 1,
        signal: 'SIGTERM',
    });
    assert.deepEqual(formatProviderError(error), [
        'Claude Code process exited with code 1',
        'stderr: Authentication failed',
        'exit_code: 1',
        'signal: SIGTERM',
    ]);
});
test('formatProviderError includes nested cause details', () => {
    const cause = Object.assign(new Error('anthropic sdk failed'), {
        stderr: 'invalid api key',
    });
    const error = Object.assign(new Error('Claude Code process exited with code 1'), {
        cause,
    });
    assert.deepEqual(formatProviderError(error), [
        'Claude Code process exited with code 1',
        'cause: anthropic sdk failed',
        'cause: stderr: invalid api key',
    ]);
});
