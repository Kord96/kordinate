import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
export class CompletedRequestStore {
    filePath;
    maxEntries;
    constructor(filePath, maxEntries = 1000) {
        this.filePath = filePath;
        this.maxEntries = maxEntries;
    }
    async load() {
        try {
            const raw = await readFile(this.filePath, 'utf8');
            const parsed = JSON.parse(raw);
            return new Map(parsed.map(record => [record.correlation_id, record]));
        }
        catch {
            return new Map();
        }
    }
    async save(records) {
        await mkdir(dirname(this.filePath), { recursive: true });
        const payload = [...records.values()]
            .sort((a, b) => a.completed_at.localeCompare(b.completed_at))
            .slice(-this.maxEntries);
        await writeFile(this.filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
    }
}
