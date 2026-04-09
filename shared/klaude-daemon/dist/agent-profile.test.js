import assert from 'node:assert/strict';
import test from 'node:test';
import { buildPromptFromProfile, loadAgentProfile, resolveReflectionPrompt } from './agent-profile.js';
test('augur profile exposes supported bundle param', () => {
    const profile = loadAgentProfile('augur');
    assert.deepEqual(profile.supportedAgentParams, ['bundle_mode']);
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
