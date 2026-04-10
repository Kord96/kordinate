export function isRequestMessage(value) {
    if (!value || typeof value !== 'object')
        return false;
    const msg = value;
    return msg.type === 'request'
        && typeof msg.sender === 'string'
        && typeof msg.correlation_id === 'string'
        && typeof msg.prompt === 'string'
        && (msg.working_dir === undefined || typeof msg.working_dir === 'string')
        && (msg.session_id === undefined || typeof msg.session_id === 'string');
}
export function sessionKeyFor(message) {
    return message.session_id ?? message.sender;
}
export function getOrCreateSession(sessions, message) {
    const key = sessionKeyFor(message);
    const existing = sessions.get(key);
    if (existing)
        return existing;
    const created = { key, lastCorrelationId: message.correlation_id };
    sessions.set(key, created);
    return created;
}
export function updateSessionAfterRequest(session, message) {
    return {
        ...session,
        lastCorrelationId: message.correlation_id,
    };
}
export function buildResponseMessage(agentName, message, response) {
    return {
        type: 'response',
        sender: agentName,
        correlation_id: message.correlation_id,
        ...response,
    };
}
export function buildReflectionEvent(input) {
    return {
        agent: input.agentName,
        agent_profile: input.agentProfile,
        backend_provider: input.backendProvider,
        backend_runtime: input.backendRuntime,
        backend_model: input.backendModel,
        task_id: input.message.correlation_id,
        correlation_id: input.message.correlation_id,
        working_dir: input.message.working_dir,
        captured_at: new Date().toISOString(),
        reflection: input.reflection,
    };
}
