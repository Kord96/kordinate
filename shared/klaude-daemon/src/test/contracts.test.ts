import assert from 'node:assert/strict'
import test from 'node:test'
import { buildPrompt, buildPromptPlan, loadInjectedAgentContract, loadInjectedRuntimeProfile, resolveReflectionPrompt } from '../contracts.js'
import type { AgentContract, RuntimeProfile } from '../types.js'

function augurContract(): AgentContract {
  return {
    version: 'agent-spec-v2',
    name: 'augur-opus',
    specialization: 'augur',
    description: 'Architecture analysis agent',
    capabilities: ['Analyze repositories'],
    acceptedRequestPrefixes: ['/analyze'],
    promptPrefix: 'You are Augur. Favor design-level reasoning and architecture trade-offs.',
    defaultReflectionPrompt: 'Return strict JSON only.',
    supportedAgentParams: ['bundle_mode'],
    requiresWorkingDirectory: true,
    bundleRefs: {
      memory: 'analyze-selective-v1',
      skill: 'core-v1',
      runtime: 'analyze-selective-v1',
    },
    validation: {
      required: true,
      validatorScript: '/app/agents/augur/skills/analyze/scripts/validate_output.py',
      finalizeScript: '/app/agents/augur/scripts/finalize_analysis.py',
    },
  }
}

function genericRuntimeProfile(): RuntimeProfile {
  return {
    version: 'runtime-profile-v2',
    kind: 'gemini-sdk',
    toolGuidance: [
      'Use `Read` to open files when a path is known.',
      'Use `Bash` only for real shell commands.',
    ],
  }
}

test('injected contract loader reads AGENT_CONTRACT_JSON', () => {
  const previous = process.env.AGENT_CONTRACT_JSON
  try {
    process.env.AGENT_CONTRACT_JSON = JSON.stringify(augurContract())
    const contract = loadInjectedAgentContract('augur-opus')
    assert.equal(contract.specialization, 'augur')
    assert.deepEqual(contract.acceptedRequestPrefixes, ['/analyze'])
    assert.deepEqual(contract.supportedAgentParams, ['bundle_mode'])
    assert.equal(contract.requiresWorkingDirectory, true)
    assert.match(contract.validation?.validatorScript ?? '', /validate_output\.py$/)
  } finally {
    if (previous === undefined) delete process.env.AGENT_CONTRACT_JSON
    else process.env.AGENT_CONTRACT_JSON = previous
  }
})

test('injected runtime profile loader reads RUNTIME_PROFILE_JSON', () => {
  const previous = process.env.RUNTIME_PROFILE_JSON
  try {
    process.env.RUNTIME_PROFILE_JSON = JSON.stringify(genericRuntimeProfile())
    const profile = loadInjectedRuntimeProfile()
    assert.equal(profile.kind, 'gemini-sdk')
    assert.equal(profile.toolGuidance?.length, 2)
  } finally {
    if (previous === undefined) delete process.env.RUNTIME_PROFILE_JSON
    else process.env.RUNTIME_PROFILE_JSON = previous
  }
})

test('buildPrompt prepends prompt prefix when present', () => {
  const prompt = buildPrompt(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Review this design',
  })

  assert.match(prompt, /You are Augur/)
  assert.match(prompt, /Review this design/)
})

test('buildPromptPlan composes repo bundle layers from injected bundle refs', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
  })

  assert.match(promptPlan.fullPrompt, /Augur Analyze Bundle — Selective v1/)
  assert.match(promptPlan.fullPrompt, /## Memory Bundle/)
  assert.match(promptPlan.dynamicPrompt, /Analyze the repo/)
  assert.ok(promptPlan.cacheablePrefix)
  assert.ok(promptPlan.cacheKey)
})

test('buildPromptPlan defaults to holistic bundle guidance for full analysis when bundle mode is unspecified', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    agent_params: {
      analysis_mode: 'full',
    },
  })

  assert.match(promptPlan.fullPrompt, /Analyze Bundle — Holistic/i)
})

test('buildPromptPlan defaults to selective bundle guidance for incremental analysis when bundle mode is unspecified', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    agent_params: {
      analysis_mode: 'incremental',
    },
  })

  assert.match(promptPlan.fullPrompt, /Analyze Bundle — Selective/i)
})

test('custom reflection prompt overrides contract default', () => {
  const prompt = resolveReflectionPrompt(augurContract(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Review this design',
    reflection_prompt: 'Focus only on bundle tradeoffs.',
  })

  assert.match(prompt, /Focus only on bundle tradeoffs/)
})

test('buildPromptPlan keeps cacheable prefix separate from task prompt and runtime context', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze only the auth flow',
    working_dir: '/kord/repos/kordinate',
  })

  assert.match(promptPlan.cacheablePrefix ?? '', /You are Augur/)
  assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Analyze only the auth flow/)
  assert.match(promptPlan.dynamicPrompt, /Analyze only the auth flow/)
  assert.match(promptPlan.dynamicPrompt, /Working directory hint:/)
})

test('buildPromptPlan renders startup guidance outside the cached prefix', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    agent_params: {
      startup_guidance: {
        directive: 'Read prepared artifacts before repo exploration.',
        starter_files: ['/tmp/blast.json', '/tmp/facts/index.json'],
      },
    },
  })

  assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Startup Guidance/)
  assert.match(promptPlan.dynamicPrompt, /## Startup Guidance/)
  assert.match(promptPlan.dynamicPrompt, /Read prepared artifacts before repo exploration\./)
  assert.match(promptPlan.dynamicPrompt, /\/tmp\/blast\.json/)
})
