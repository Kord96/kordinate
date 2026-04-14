export function createRequestRecord(input) {
    return {
        request_id: input.request_id,
        agent: input.agent,
        status: 'pending',
        created_at: input.created_at,
        timeout_ms: input.timeout_ms,
        debug: { events: [] },
        transcript: { events: [] },
    };
}
export function applyFailureToRequestRecord(record, input) {
    return {
        ...record,
        status: input.is_timeout ? 'timed_out' : 'error',
        completed_at: input.completed_at,
        timed_out_at: input.is_timeout ? input.completed_at : record.timed_out_at,
        error: input.message,
    };
}
export function applyResponseToRequestRecord(record, response, completedAt) {
    const alreadyTimedOut = record.status === 'timed_out';
    const nextStatus = alreadyTimedOut
        ? 'timed_out'
        : response.status === 'error'
            ? 'error'
            : 'completed';
    return {
        ...record,
        status: nextStatus,
        completed_at: record.completed_at ?? completedAt,
        response: alreadyTimedOut ? record.response : response,
        late_reply_received: alreadyTimedOut ? true : record.late_reply_received,
        late_response: alreadyTimedOut ? response : record.late_response,
        error: alreadyTimedOut ? record.error : response.status === 'error' ? response.output : undefined,
    };
}
