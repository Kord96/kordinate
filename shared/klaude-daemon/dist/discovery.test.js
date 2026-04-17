import assert from 'node:assert/strict';
import test from 'node:test';
import { buildDiscoveryRecord } from './discovery.js';
test('buildDiscoveryRecord exposes prompting contract and agent metadata', () => {
    const config = {
        executionProfile: {
            provider: 'deepseek',
            runtime: 'openclaude-harness',
            model: 'deepseek-chat',
            homeDirectory: '/runtime/alfred',
            workingDirectory: '/kord/repos/kordinate',
        },
        kafkaBrokers: ['kafka:9092'],
        kafkaSessionTimeoutMs: 600000,
        kafkaHeartbeatIntervalMs: 3000,
        reflectionsTopic: 'reflections',
        progressTopic: 'kord-progress',
        discoveryServerUrl: 'http://discovery:9091',
        discoveryPublishIntervalMs: 30000,
        healthUrl: 'http://agent-alfred:9090/health',
        stateDir: '.daemon-state',
        sessionMapPath: '.daemon-state/sessions.json',
    };
    const record = buildDiscoveryRecord({
        agent: 'alfred',
        specialization: 'alfred',
        agentContract: {
            name: 'alfred',
            specialization: 'alfred',
            description: 'Password and operator assistant',
            capabilities: ['Manage local secrets'],
            supportedAgentParams: [],
            requiresWorkingDirectory: false,
        },
        config,
        healthUrl: config.healthUrl,
    });
    assert.equal(record.name, 'alfred');
    assert.equal(record.backend_provider, 'deepseek');
    assert.equal(record.backend_model, 'deepseek-chat');
    assert.ok(Array.isArray(record.capabilities));
    assert.equal(record.specialization, 'alfred');
    assert.equal(record.request_topic, 'alfred');
    assert.equal(record.health_url, 'http://agent-alfred:9090/health');
    assert.equal(record.default_working_dir, '/kord/repos/kordinate');
});
