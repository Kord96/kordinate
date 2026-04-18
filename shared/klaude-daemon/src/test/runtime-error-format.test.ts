import assert from 'node:assert/strict'
import test from 'node:test'
import { formatProviderError } from '../runtime.js'

test('formatProviderError preserves stderr and exit details', () => {
  const error = Object.assign(new Error('Claude Code process exited with code 1'), {
    stderr: 'Authentication failed',
    exitCode: 1,
    signal: 'SIGTERM',
  })

  assert.deepEqual(formatProviderError(error), [
    'Claude Code process exited with code 1',
    'stderr: Authentication failed',
    'exit_code: 1',
    'signal: SIGTERM',
  ])
})

test('formatProviderError includes nested cause details', () => {
  const cause = Object.assign(new Error('anthropic sdk failed'), {
    stderr: 'invalid api key',
  })
  const error = Object.assign(new Error('Claude Code process exited with code 1'), {
    cause,
  })

  assert.deepEqual(formatProviderError(error), [
    'Claude Code process exited with code 1',
    'cause: anthropic sdk failed',
    'cause: stderr: invalid api key',
  ])
})

test('formatProviderError includes structured log diagnostics', () => {
  const error = Object.assign(new Error('openclaude timed out after 20000ms'), {
    structuredLogPath: '/tmp/openclaude-stream.jsonl',
    structuredLogTail: '{"type":"assistant"}',
  })

  assert.deepEqual(formatProviderError(error), [
    'openclaude timed out after 20000ms',
    'structured_log_path: /tmp/openclaude-stream.jsonl',
    'structured_log_tail: {"type":"assistant"}',
  ])
})
