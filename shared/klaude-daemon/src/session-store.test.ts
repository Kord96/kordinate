import assert from 'node:assert/strict'
import test from 'node:test'
import { mkdtemp } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { SessionStore } from './session-store.js'
import type { SessionState } from './types.js'

test('SessionStore saves and loads sender session mappings', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'klaude-daemon-'))
  const filePath = join(dir, 'sessions.json')
  const store = new SessionStore(filePath)
  const sessions = new Map<string, SessionState>([
    ['agent-a', { key: 'agent-a', providerSessionId: 'thread-1', lastCorrelationId: 'corr-1' }],
  ])

  await store.save(sessions)
  const loaded = await store.load()

  assert.deepEqual(loaded.get('agent-a'), {
    key: 'agent-a',
    providerSessionId: 'thread-1',
    lastCorrelationId: 'corr-1',
  })
})
