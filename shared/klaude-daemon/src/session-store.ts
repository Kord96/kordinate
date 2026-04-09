import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import type { SessionState } from './types.js'

export class SessionStore {
  constructor(private readonly filePath: string) {}

  async load(): Promise<Map<string, SessionState>> {
    try {
      const raw = await readFile(this.filePath, 'utf8')
      const parsed = JSON.parse(raw) as Record<string, SessionState>
      return new Map(Object.entries(parsed))
    } catch {
      return new Map()
    }
  }

  async save(sessions: Map<string, SessionState>): Promise<void> {
    await mkdir(dirname(this.filePath), { recursive: true })
    const payload = Object.fromEntries(sessions.entries())
    await writeFile(this.filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8')
  }
}
