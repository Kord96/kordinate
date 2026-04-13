import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'

type CompletedRequestRecord = {
  correlation_id: string
  completed_at: string
  status: string
}

export class CompletedRequestStore {
  constructor(
    private readonly filePath: string,
    private readonly maxEntries = 1000,
  ) {}

  async load(): Promise<Map<string, CompletedRequestRecord>> {
    try {
      const raw = await readFile(this.filePath, 'utf8')
      const parsed = JSON.parse(raw) as CompletedRequestRecord[]
      return new Map(parsed.map(record => [record.correlation_id, record]))
    } catch {
      return new Map()
    }
  }

  async save(records: Map<string, CompletedRequestRecord>): Promise<void> {
    await mkdir(dirname(this.filePath), { recursive: true })
    const payload = [...records.values()]
      .sort((a, b) => a.completed_at.localeCompare(b.completed_at))
      .slice(-this.maxEntries)
    await writeFile(this.filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8')
  }
}

export type { CompletedRequestRecord }
