import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
export class SessionStore {
    filePath;
    constructor(filePath) {
        this.filePath = filePath;
    }
    async load() {
        try {
            const raw = await readFile(this.filePath, 'utf8');
            const parsed = JSON.parse(raw);
            return new Map(Object.entries(parsed));
        }
        catch {
            return new Map();
        }
    }
    async save(sessions) {
        await mkdir(dirname(this.filePath), { recursive: true });
        const payload = Object.fromEntries(sessions.entries());
        await writeFile(this.filePath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
    }
}
