import type { RequestTranscriptEvent, ResponseMessage } from './types.js'

export interface RequestRecord {
  request_id: string
  agent: string
  status: 'pending' | 'completed' | 'error' | 'timed_out'
  created_at: string
  completed_at?: string
  response?: ResponseMessage
  error?: string
  timeout_ms?: number
  timed_out_at?: string
  late_reply_received?: boolean
  last_progress_at?: string
  last_meaningful_event?: RequestTranscriptEvent
  late_response?: ResponseMessage
  debug?: {
    events: Array<Record<string, unknown>>
  }
  transcript?: {
    events: RequestTranscriptEvent[]
  }
}

export function createRequestRecord(input: {
  request_id: string
  agent: string
  created_at: string
  timeout_ms?: number
}): RequestRecord {
  return {
    request_id: input.request_id,
    agent: input.agent,
    status: 'pending',
    created_at: input.created_at,
    timeout_ms: input.timeout_ms,
    debug: { events: [] },
    transcript: { events: [] },
  }
}

export function applyFailureToRequestRecord(record: RequestRecord, input: {
  message: string
  completed_at: string
  is_timeout: boolean
}): RequestRecord {
  return {
    ...record,
    status: input.is_timeout ? 'timed_out' : 'error',
    completed_at: input.completed_at,
    timed_out_at: input.is_timeout ? input.completed_at : record.timed_out_at,
    error: input.message,
  }
}

export function applyResponseToRequestRecord(record: RequestRecord, response: ResponseMessage, completedAt: string): RequestRecord {
  const alreadyTimedOut = record.status === 'timed_out'
  const nextStatus: 'timed_out' | 'error' | 'completed' = alreadyTimedOut
    ? 'timed_out'
    : response.status === 'error'
      ? 'error'
      : 'completed'
  return {
    ...record,
    status: nextStatus,
    completed_at: record.completed_at ?? completedAt,
    response: alreadyTimedOut ? record.response : response,
    late_reply_received: alreadyTimedOut ? true : record.late_reply_received,
    late_response: alreadyTimedOut ? response : record.late_response,
    error: alreadyTimedOut ? record.error : response.status === 'error' ? response.output : undefined,
  }
}
