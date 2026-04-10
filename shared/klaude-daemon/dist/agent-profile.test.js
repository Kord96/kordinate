import assert from 'node:assert/strict';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import test from 'node:test';
import { buildPromptFromProfile, loadAgentProfile, resolveReflectionPrompt } from './agent-profile.js';
test('augur profile exposes supported bundle param', () => {
    const profile = loadAgentProfile('augur');
    assert.deepEqual(profile.supportedAgentParams, ['bundle_mode']);
    assert.ok(Array.isArray(profile.capabilities));
});
test('buildPromptFromProfile prepends prompt prefix when present', () => {
    const profile = loadAgentProfile('augur');
    const prompt = buildPromptFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Review this design',
    });
    assert.match(prompt, /You are Augur/);
    assert.match(prompt, /Review this design/);
});
test('buildPromptFromProfile composes augur bundle layers for bundle_mode', () => {
    const profile = loadAgentProfile('augur');
    const prompt = buildPromptFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Analyze the repo',
        agent_params: { bundle_mode: 'selective' },
    });
    assert.match(prompt, /Augur Analyze Skill Bundle — Core v1/);
    assert.match(prompt, /Augur Analyze Bundle — Selective v1/);
    assert.match(prompt, /framework detection -> fact extraction -> concept inference -> atlas synthesis/);
});
test('custom reflection prompt overrides profile default', () => {
    const profile = loadAgentProfile('augur');
    const prompt = resolveReflectionPrompt(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Review this design',
        reflection_prompt: 'Focus only on bundle tradeoffs.',
    });
    assert.match(prompt, /Focus only on bundle tradeoffs/);
});
test('unknown agent profile falls back to generic behavior', () => {
    const profile = loadAgentProfile('reviewer');
    const prompt = buildPromptFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Do the task',
    });
    assert.equal(prompt, 'Do the task');
    assert.deepEqual(profile.supportedAgentParams, []);
});
test('buildPromptFromProfile appends working directory hint when provided', () => {
    const profile = loadAgentProfile('reviewer');
    const prompt = buildPromptFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Inspect the repo',
        working_dir: '/kord/shared/repos/kordinate',
    });
    assert.match(prompt, /Inspect the repo/);
    assert.match(prompt, /Working directory hint:/);
    assert.match(prompt, /\/kord\/shared\/repos\/kordinate/);
});
test('buildPromptFromProfile composes seeded bundle layers for non-augur agents', () => {
    const runtimeDir = mkdtempSync(join(tmpdir(), 'agent-profile-'));
    const previousAgentHome = process.env.AGENT_HOME_DIR;
    process.env.AGENT_HOME_DIR = runtimeDir;
    try {
        writeFileSync(join(runtimeDir, 'memory-bundle.md'), '# Memory\n\nUse direct action.', 'utf8');
        writeFileSync(join(runtimeDir, 'skill-bundle.md'), '# Skill\n\nFollow the workflow.', 'utf8');
        writeFileSync(join(runtimeDir, 'runtime-bundle.md'), '# Runtime\n\nBe terse.', 'utf8');
        const prompt = buildPromptFromProfile(loadAgentProfile('reviewer'), {
            type: 'request',
            sender: 'agent-a',
            correlation_id: 'corr-1',
            prompt: 'Do the task',
        });
        assert.match(prompt, /## Skill Bundle/);
        assert.match(prompt, /## Memory Bundle/);
        assert.match(prompt, /## Runtime Bundle/);
        assert.match(prompt, /Do the task/);
    }
    finally {
        if (previousAgentHome === undefined) {
            delete process.env.AGENT_HOME_DIR;
        }
        else {
            process.env.AGENT_HOME_DIR = previousAgentHome;
        }
        rmSync(runtimeDir, { recursive: true, force: true });
    }
});
