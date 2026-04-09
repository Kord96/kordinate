import assert from 'node:assert/strict';
import test from 'node:test';
import { loadAgentProfile } from './agent-profile.js';
import { buildDiscoveryRecord } from './discovery.js';
test('buildDiscoveryRecord exposes prompting contract and agent metadata', () => {
    const config = {
        executionProfile: {
            provider: 'deepseek',
            runtime: 'openclaude-harness',
            model: 'deepseek-chat',
            workingDirectory: '/kord/shared/repos/kordinate',
        },
        kafkaBrokers: ['kafka:9092'],
        reflectionsTopic: 'reflections',
        discoveryServerUrl: 'http://discovery:9091',
        discoveryPublishIntervalMs: 30000,
        healthUrl: 'http://agent-alfred:9090/health',
        stateDir: '.daemon-state',
        sessionMapPath: '.daemon-state/sessions.json',
    };
    const record = buildDiscoveryRecord({
        agent: 'alfred',
        profile: 'alfred',
        agentProfile: loadAgentProfile('alfred'),
        config,
        healthUrl: config.healthUrl,
    });
    assert.equal(record.agent, 'alfred');
    assert.equal(record.request_topic, 'alfred');
    assert.equal(record.reply_mode, 'sender-topic');
    assert.equal(record.working_dir_supported, true);
    assert.deepEqual(record.request_schema.required, ['type', 'sender', 'correlation_id', 'prompt']);
    assert.match(record.request_example.prompt, /alfred/);
    assert.equal(record.request_example.working_dir, '/kord/shared/repos/kordinate');
    assert.equal(record.health_url, 'http://agent-alfred:9090/health');
});
