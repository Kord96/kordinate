import test from 'node:test'
import assert from 'node:assert/strict'
import { applyFailureToRequestRecord, applyResponseToRequestRecord, createRequestRecord } from './request-model.js'
import type { ResponseMessage } from './types.js'

test('timeout failure marks request as timed_out', () => {
  const record = createRequestRecord({
    request_id: 'req-1',
    agent: 'generic-opus',
    created_at: '2026-04-14T00:00:00.000Z',
    timeout_ms: 120000,
  })

  const next = applyFailureToRequestRecord(record, {
    message: 'timed out waiting for req-1',
    completed_at: '2026-04-14T00:02:00.000Z',
    is_timeout: true,
  })

  assert.equal(next.status, 'timed_out')
  assert.equal(next.timed_out_at, '2026-04-14T00:02:00.000Z')
  assert.equal(next.error, 'timed out waiting for req-1')
})

test('late reply after timeout is preserved separately', () => {
  const timedOut = applyFailureToRequestRecord(createRequestRecord({
    request_id: 'req-2',
    agent: 'generic-opus',
    created_at: '2026-04-14T00:00:00.000Z',
    timeout_ms: 120000,
  }), {
    message: 'timed out waiting for req-2',
    completed_at: '2026-04-14T00:02:00.000Z',
    is_timeout: true,
  })

  const lateResponse: ResponseMessage = {
    type: 'response',
    sender: 'generic-opus',
    correlation_id: 'req-2',
    status: 'success',
    output: 'finished later',
  }

  const next = applyResponseToRequestRecord(timedOut, lateResponse, '2026-04-14T00:03:00.000Z')
  assert.equal(next.status, 'timed_out')
  assert.equal(next.late_reply_received, true)
  assert.equal(next.late_response?.output, 'finished later')
  assert.equal(next.response, undefined)
})
