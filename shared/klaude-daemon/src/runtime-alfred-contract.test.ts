import assert from 'node:assert/strict'
import test from 'node:test'
import type { RuntimeRequest, RuntimeResult } from './types.js'
import { __testOnly } from './runtime.js'

test('alfred direct get rejects empty success', () => {
  process.env.AGENT_PROFILE_NAME = 'alfred'
  const request = { prompt: 'Get key test/demo' } as RuntimeRequest
  const result = { status: 'success', output: '' } as RuntimeResult
  assert.deepEqual(__testOnly.enforceAlfredDirectIntentContract(request, result), {
    status: 'error',
    output: 'get_secret completed without returning a concrete result',
    errors: ['get_secret completed without returning a concrete result'],
  })
})

test('alfred direct store rejects generic assistant text', () => {
  process.env.AGENT_PROFILE_NAME = 'alfred'
  const request = { prompt: 'Store key test/demo value SECRET_VALUE' } as RuntimeRequest
  const result = { status: 'success', output: 'What can I help you with today?' } as RuntimeResult
  assert.deepEqual(__testOnly.enforceAlfredDirectIntentContract(request, result), {
    status: 'error',
    output: 'store_secret returned generic assistant text instead of executing the operation',
    errors: ['store_secret returned generic assistant text instead of executing the operation'],
  })
})

test('alfred direct store accepts stored confirmation', () => {
  process.env.AGENT_PROFILE_NAME = 'alfred'
  const request = { prompt: 'Store key test/demo value SECRET_VALUE' } as RuntimeRequest
  const result = { status: 'success', output: 'stored' } as RuntimeResult
  assert.deepEqual(__testOnly.enforceAlfredDirectIntentContract(request, result), result)
})
