import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
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
      validatorScript: '/kord/agents/augur-opus/.augur/current/skills/analyze/validator/validate.py',
      finalizeScript: '/kord/agents/augur-opus/.augur/current/scripts/run/finalize_analysis.py',
    },
  }
}

function genericRuntimeProfile(): RuntimeProfile {
  return {
    version: 'runtime-profile-v2',
    kind: 'gemini-sdk',
    toolGuidance: [
      "Rely on the runtime's advertised tool schema instead of assuming tool names from other runtimes.",
      'Do not invent helper names or wrap nonexistent tools inside Bash.',
    ],
  }
}

function withAugurBundleFixture<T>(fn: () => T): T {
  const root = mkdtempSync(join(tmpdir(), 'augur-bundles-'))
  const previousAugurHome = process.env.AUGUR_HOME
  try {
    const bundlesRoot = join(root, '.generated', 'bundles')
    mkdirSync(join(bundlesRoot, 'skill'), { recursive: true })
    mkdirSync(join(bundlesRoot, 'memory'), { recursive: true })
    mkdirSync(join(bundlesRoot, 'runtime'), { recursive: true })
    writeFileSync(join(bundlesRoot, 'skill', 'core-v1.md'), '# Augur Skill Bundle')
    writeFileSync(join(bundlesRoot, 'memory', 'analyze-selective-v1.md'), '# Augur Analyze Bundle — Selective v1')
    writeFileSync(join(bundlesRoot, 'memory', 'analyze-holistic-v1.md'), '# Augur Analyze Bundle — Holistic v1')
    writeFileSync(join(bundlesRoot, 'runtime', 'analyze-selective-v1.md'), '# Runtime Selective Bundle')
    writeFileSync(join(bundlesRoot, 'runtime', 'analyze-holistic-v1.md'), '# Runtime Holistic Bundle')
    process.env.AUGUR_HOME = root
    return fn()
  } finally {
    if (previousAugurHome === undefined) delete process.env.AUGUR_HOME
    else process.env.AUGUR_HOME = previousAugurHome
    rmSync(root, { recursive: true, force: true })
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
    assert.match(contract.validation?.validatorScript ?? '', /validate\.py$/)
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
  const promptPlan = withAugurBundleFixture(() => buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
  }))

  assert.match(promptPlan.fullPrompt, /Augur Analyze Bundle — Selective v1/)
  assert.match(promptPlan.fullPrompt, /## Memory Bundle/)
  assert.match(promptPlan.dynamicPrompt, /Analyze the repo/)
  assert.ok(promptPlan.cacheablePrefix)
  assert.ok(promptPlan.cacheKey)
})

test('buildPromptPlan defaults to holistic bundle guidance for full analysis when bundle mode is unspecified', () => {
  const promptPlan = withAugurBundleFixture(() => buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    agent_params: {
      analysis_mode: 'full',
    },
  }))

  assert.match(promptPlan.fullPrompt, /Analyze Bundle — Holistic/i)
})

test('buildPromptPlan defaults to selective bundle guidance for incremental analysis when bundle mode is unspecified', () => {
  const promptPlan = withAugurBundleFixture(() => buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    agent_params: {
      analysis_mode: 'incremental',
    },
  }))

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
    workspace: {
      working_dir: '/kord/shared/repos/kordinate',
      output_dir: '/tmp/run',
    },
  })

  assert.match(promptPlan.cacheablePrefix ?? '', /You are Augur/)
  assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Analyze only the auth flow/)
  assert.match(promptPlan.dynamicPrompt, /Analyze only the auth flow/)
  assert.match(promptPlan.dynamicPrompt, /Working directory: `\/kord\/shared\/repos\/kordinate`/)
  assert.match(promptPlan.dynamicPrompt, /Output directory: `\/tmp\/run`/)
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
        starter_files: ['/tmp/blast.json', '/tmp/index.json'],
      },
    },
  })

  assert.doesNotMatch(promptPlan.cacheablePrefix ?? '', /Startup Guidance/)
  assert.match(promptPlan.dynamicPrompt, /## Startup Guidance/)
  assert.match(promptPlan.dynamicPrompt, /Read prepared artifacts before repo exploration\./)
  assert.match(promptPlan.dynamicPrompt, /\/tmp\/blast\.json/)
})

test('buildPromptPlan renders workspace contract and runtime guidance when requested', () => {
  const promptPlan = buildPromptPlan(augurContract(), genericRuntimeProfile(), {
    type: 'request',
    sender: 'agent-a',
    correlation_id: 'corr-1',
    prompt: 'Analyze the repo',
    workspace: {
      working_dir: '/kord/shared/repos/repo',
      output_dir: '/tmp/run',
      agent_root: '/kord/agents/augur-opus/.augur/current',
    },
    resources: {
      validator_script: '/kord/agents/augur-opus/.augur/current/skills/analyze/validator/validate.py',
      concept_catalog_index: '/kord/agents/augur-opus/.augur/current/memory/concepts/README.md',
      framework_catalog_index: '/kord/agents/augur-opus/.augur/current/memory/concepts/frameworks/README.md',
    },
    agent_params: {
      bundle_mode: 'selective',
    },
  })

  assert.match(promptPlan.dynamicPrompt, /Working directory: `\/kord\/shared\/repos\/repo`/)
  assert.match(promptPlan.dynamicPrompt, /Output directory: `\/tmp\/run`/)
  assert.match(promptPlan.dynamicPrompt, /Agent root: `\/kord\/agents\/augur-opus\/\.augur\/current`/)
  assert.match(promptPlan.dynamicPrompt, /Validator script: `\/kord\/agents\/augur-opus\/\.augur\/current\/skills\/analyze\/validator\/validate\.py`/)
  assert.match(promptPlan.dynamicPrompt, /Concept catalog entrypoint: `\/kord\/agents\/augur-opus\/\.augur\/current\/memory\/concepts\/README\.md`/)
  assert.match(promptPlan.dynamicPrompt, /Framework catalog entrypoint: `\/kord\/agents\/augur-opus\/\.augur\/current\/memory\/concepts\/frameworks\/README\.md`/)
  assert.match(promptPlan.dynamicPrompt, /Use only the printed validator command\. Do not discover alternate validator or schema paths\./)
  assert.doesNotMatch(promptPlan.dynamicPrompt, /Grounding summary path:/)
  assert.doesNotMatch(promptPlan.dynamicPrompt, /Write handoff path:/)
})
