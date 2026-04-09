export function buildDiscoveryRecord(input) {
    const now = new Date().toISOString();
    return {
        name: input.agent,
        capabilities: input.agentProfile.capabilities ?? [],
        backend_provider: input.config.executionProfile.provider,
        backend_model: input.config.executionProfile.model,
        supported_agent_params: input.agentProfile.supportedAgentParams ?? [],
        active: true,
        specialization: input.specialization,
        runtime: input.config.executionProfile.runtime,
        health_url: input.healthUrl,
        request_topic: input.agent,
        default_working_dir: input.config.executionProfile.workingDirectory,
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
