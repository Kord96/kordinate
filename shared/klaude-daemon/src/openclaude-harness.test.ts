import assert from 'node:assert/strict'
import test from 'node:test'
import { loadDaemonConfig } from './config.js'

test('loadDaemonConfig supports deepseek through openclaude harness', () => {
  const previous = { ...process.env }
  process.env.DAEMON_PROVIDER = 'deepseek'
  process.env.DAEMON_RUNTIME = 'openclaude-harness'
  process.env.DAEMON_MODEL = 'deepseek-chat'
  process.env.BACKEND_API_KEY = 'deepseek-key'

  const config = loadDaemonConfig()

  assert.deepEqual(config.executionProfile, {
    provider: 'deepseek',
    runtime: 'openclaude-harness',
    model: 'deepseek-chat',
    apiKey: 'deepseek-key',
    baseUrl: 'https://api.deepseek.com/v1',
    homeDirectory: undefined,
    workingDirectory: undefined,
  })

  process.env = previous
})
