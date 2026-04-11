import test from 'node:test'
import assert from 'node:assert/strict'
import { createDiscoveryRegistry } from './discovery-registry.js'
import type { AgentDiscoveryRecord } from './types.js'

function record(input: Partial<AgentDiscoveryRecord> & Pick<AgentDiscoveryRecord, 'name' | 'backend_provider' | 'backend_model'>): AgentDiscoveryRecord {
  return {
    capabilities: [],
    supported_agent_params: [],
    active: input.active ?? true,
    ...input,
  }
}

test('logical discovery groups variants by specialization and chooses a default variant', async () => {
  const registry = createDiscoveryRegistry({
    statePath: '/tmp/kord-api-discovery-registry-test-state.json',
    catalogPath: '/tmp/kord-api-discovery-registry-test-catalog.json',
    ttlMs: 120000,
  })

  await registry.register(record({
    name: 'augur-gpt54',
    specialization: 'augur',
    backend_provider: 'openai',
    backend_model: 'gpt-5.4',
    capabilities: ['Analyze architecture'],
  }))
  await registry.register(record({
    name: 'augur-opus',
    specialization: 'augur',
    backend_provider: 'anthropic',
    backend_model: 'opus',
    capabilities: ['Analyze architecture'],
  }))

  const logical = registry.getLogical('augur')
  assert.ok(logical)
  assert.equal(logical.name, 'augur')
  assert.equal(logical.default_variant, 'augur-opus')
  assert.deepEqual(logical.variants.map(item => item.name), ['augur-opus', 'augur-gpt54'])
})

test('prompt resolution supports logical agent names, explicit variants, and backend_model pinning', async () => {
  const registry = createDiscoveryRegistry({
    statePath: '/tmp/kord-api-discovery-registry-test-state-2.json',
    catalogPath: '/tmp/kord-api-discovery-registry-test-catalog-2.json',
    ttlMs: 120000,
  })

  await registry.register(record({
    name: 'charon-gpt53-codex',
    specialization: 'charon',
    backend_provider: 'openai',
    backend_model: 'gpt-5.3-codex',
  }))
  await registry.register(record({
    name: 'augur-opus',
    specialization: 'augur',
    backend_provider: 'anthropic',
    backend_model: 'opus',
  }))
  await registry.register(record({
    name: 'augur-gpt54',
    specialization: 'augur',
    backend_provider: 'openai',
    backend_model: 'gpt-5.4',
  }))

  assert.equal(registry.resolveTarget('charon')?.name, 'charon-gpt53-codex')
  assert.equal(registry.resolveTarget('augur')?.name, 'augur-opus')
  assert.equal(registry.resolveTarget('augur', { variant: 'augur-gpt54' })?.name, 'augur-gpt54')
  assert.equal(registry.resolveTarget('augur', { backend_model: 'gpt-5.4' })?.name, 'augur-gpt54')
  assert.equal(registry.resolveTarget('charon-gpt53-codex')?.name, 'charon-gpt53-codex')
  assert.equal(registry.resolveTarget('charon', { variant: 'augur-gpt54' }), undefined)
})
