import assert from 'node:assert/strict'
import test from 'node:test'
import type { AgentContract, RequestMessage } from '../types.js'

function requestCommandText(message: RequestMessage): string {
  return typeof message.raw_prompt === 'string' && message.raw_prompt.trim()
    ? message.raw_prompt
    : message.prompt
}

function validateRequestContract(contract: AgentContract, message: RequestMessage): string | undefined {
  if (contract.requiresWorkingDirectory && !message.working_dir) {
    return 'working_dir is required for this agent'
  }
  const acceptedPrefixes = Array.isArray(contract.acceptedRequestPrefixes)
    ? contract.acceptedRequestPrefixes.filter(prefix => typeof prefix === 'string' && prefix.trim().length > 0)
    : []
  if (acceptedPrefixes.length > 0) {
    const text = requestCommandText(message).trim()
    if (!acceptedPrefixes.some(prefix => text.startsWith(prefix))) {
      return `request does not match an accepted agent skill/command (${acceptedPrefixes.join(', ')})`
    }
  }
  return undefined
}

test('validateRequestContract rejects requests that do not map to accepted agent commands', () => {
  const contract: AgentContract = {
    name: 'augur-opus',
    specialization: 'augur',
    description: 'Architecture analysis agent',
    capabilities: ['Analyze repositories'],
    acceptedRequestPrefixes: ['/analyze'],
    supportedAgentParams: [],
    requiresWorkingDirectory: true,
  }

  const invalidMessage: RequestMessage = {
    type: 'request',
    sender: 'tester',
    correlation_id: 'corr-1',
    prompt: 'Please audit the current state of augur',
    working_dir: '/kord/shared/repos/kordinate',
  }

  assert.match(
    validateRequestContract(contract, invalidMessage) ?? '',
    /does not match an accepted agent skill\/command/,
  )
})

test('validateRequestContract accepts requests that map to declared agent commands', () => {
  const contract: AgentContract = {
    name: 'augur-opus',
    specialization: 'augur',
    description: 'Architecture analysis agent',
    capabilities: ['Analyze repositories'],
    acceptedRequestPrefixes: ['/analyze', '/design'],
    supportedAgentParams: [],
    requiresWorkingDirectory: true,
  }

  const validMessage: RequestMessage = {
    type: 'request',
    sender: 'tester',
    correlation_id: 'corr-2',
    prompt: '/analyze --full',
    working_dir: '/kord/shared/repos/kordinate',
  }

  assert.equal(validateRequestContract(contract, validMessage), undefined)
})
