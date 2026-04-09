export function isRequestMessage(value) {
    if (!value || typeof value !== 'object')
        return false;
    const msg = value;
    return msg.type === 'request'
        && typeof msg.sender === 'string'
        && typeof msg.correlation_id === 'string'
        && typeof msg.prompt === 'string'
        && (msg.working_dir === undefined || typeof msg.working_dir === 'string');
}
export function sessionKeyFor(message) {
    return message.sender;
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
export function buildReflectionEvent(agentName, message, reflection) {
    return {
        agent: agentName,
        task_id: message.correlation_id,
        correlation_id: message.correlation_id,
        reflection,
    };
}
