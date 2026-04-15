import assert from 'node:assert/strict';
import test from 'node:test';
import { buildPromptFromProfile, buildPromptPlanFromProfile, loadAgentProfile, resolveReflectionPrompt } from './agent-profile.js';
test('augur profile exposes supported bundle param', () => {
    const profile = loadAgentProfile('augur');
    assert.deepEqual(profile.supportedAgentParams, ['bundle_mode']);
    assert.equal(profile.requiresWorkingDirectory, true);
    assert.equal(profile.validation?.required, true);
    assert.match(profile.validation?.validatorScript ?? '', /validate_output\.py$/);
    assert.match(profile.validation?.finalizeScript ?? '', /finalize_analysis\.py$/);
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
    const promptPlan = buildPromptPlanFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Analyze the repo',
        agent_params: { bundle_mode: 'selective' },
    });
    assert.match(promptPlan.fullPrompt, /Augur Analyze Skill Bundle — Core v1/);
    assert.match(promptPlan.fullPrompt, /Augur Analyze Bundle — Selective v1/);
    assert.match(promptPlan.fullPrompt, /concept-evidence/);
    assert.match(promptPlan.dynamicPrompt, /Analyze the repo/);
    assert.ok(promptPlan.cacheablePrefix);
    assert.ok(promptPlan.cacheKey);
});
test('buildPromptFromProfile accepts full-bundle aliases for holistic mode', () => {
    const profile = loadAgentProfile('augur');
    const promptPlan = buildPromptPlanFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Analyze the repo deeply',
        agent_params: { bundle_mode: 'full-bundle' },
    });
    assert.match(promptPlan.fullPrompt, /Augur Analyze Bundle — Holistic v1/);
    assert.match(promptPlan.dynamicPrompt, /Bundle mode hint: use `holistic`/);
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
    assert.equal(profile.requiresWorkingDirectory, false);
    assert.equal(profile.validation, undefined);
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
test('buildPromptFromProfile composes repo bundle layers for non-augur agents', () => {
    const previousMemoryBundle = process.env.AGENT_MEMORY_BUNDLE;
    const previousSkillBundle = process.env.AGENT_SKILL_BUNDLE;
    const previousRuntimeBundle = process.env.AGENT_RUNTIME_BUNDLE;
    try {
        process.env.AGENT_MEMORY_BUNDLE = 'platform-admin-v1';
        process.env.AGENT_SKILL_BUNDLE = 'get-store-core-v1';
        process.env.AGENT_RUNTIME_BUNDLE = 'direct-action-v1';
        const prompt = buildPromptFromProfile(loadAgentProfile('alfred'), {
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
        if (previousMemoryBundle === undefined) {
            delete process.env.AGENT_MEMORY_BUNDLE;
        }
        else {
            process.env.AGENT_MEMORY_BUNDLE = previousMemoryBundle;
        }
        if (previousSkillBundle === undefined) {
            delete process.env.AGENT_SKILL_BUNDLE;
        }
        else {
            process.env.AGENT_SKILL_BUNDLE = previousSkillBundle;
        }
        if (previousRuntimeBundle === undefined) {
            delete process.env.AGENT_RUNTIME_BUNDLE;
        }
        else {
            process.env.AGENT_RUNTIME_BUNDLE = previousRuntimeBundle;
        }
    }
});
test('buildPromptPlanFromProfile keeps cacheable prefix separate from task prompt', () => {
    const profile = loadAgentProfile('augur');
    const promptPlan = buildPromptPlanFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Analyze only the auth flow',
        working_dir: '/kord/repos/kordinate',
        agent_params: { bundle_mode: 'selective' },
    });
    assert.match(promptPlan.cacheablePrefix ?? '', /You are Augur/);
    assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Analyze only the auth flow/);
    assert.match(promptPlan.dynamicPrompt, /Analyze only the auth flow/);
    assert.match(promptPlan.dynamicPrompt, /Working directory hint:/);
});
test('buildPromptPlanFromProfile renders startup guidance outside the cached prefix', () => {
    const profile = loadAgentProfile('augur');
    const promptPlan = buildPromptPlanFromProfile(profile, {
        type: 'request',
        sender: 'agent-a',
        correlation_id: 'corr-1',
        prompt: 'Analyze the repo',
        agent_params: {
            bundle_mode: 'selective',
            startup_guidance: {
                directive: 'Read prepared artifacts before repo exploration.',
                starter_files: ['/tmp/blast.json', '/tmp/facts/index.json'],
            },
        },
    });
    assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Startup Guidance/);
    assert.match(promptPlan.dynamicPrompt, /## Startup Guidance/);
    assert.match(promptPlan.dynamicPrompt, /Read prepared artifacts before repo exploration\./);
    assert.match(promptPlan.dynamicPrompt, /\/tmp\/blast\.json/);
    assert.match(promptPlan.dynamicPrompt, /\/tmp\/facts\/index\.json/);
});
