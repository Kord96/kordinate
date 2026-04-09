export function buildDiscoveryRecord(input) {
    const now = new Date().toISOString();
    const example = {
        type: 'request',
        sender: `${input.agent}-reply-topic`,
        correlation_id: `${input.agent}-request-1`,
        prompt: `Do the requested work as ${input.agent}.`,
        working_dir: input.config.executionProfile.workingDirectory,
        timeout_ms: 120000,
    };
    return {
        agent: input.agent,
        profile: input.profile,
        provider: input.config.executionProfile.provider,
        runtime: input.config.executionProfile.runtime,
        model: input.config.executionProfile.model,
        request_topic: input.agent,
        reply_mode: 'sender-topic',
        working_dir_supported: true,
        request_schema: {
            required: ['type', 'sender', 'correlation_id', 'prompt'],
            optional: ['working_dir', 'timeout_ms', 'reflect', 'reflection_prompt', 'agent_params'],
        },
        request_example: example,
        health_url: input.healthUrl,
        working_directory: input.config.executionProfile.workingDirectory,
        supported_agent_params: input.agentProfile.supportedAgentParams ?? [],
        registered_at: now,
        last_seen_at: now,
    };
}
export async function publishDiscoveryRegistration(discoveryServerUrl, record) {
    const response = await fetch(new URL('/register', discoveryServerUrl), {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(record),
    });
    if (!response.ok) {
        throw new Error(`discovery registration failed with ${response.status}`);
    }
}
