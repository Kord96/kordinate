import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export interface IdentityMetadata {
  name: string
  description?: string
  capabilities: string[]
}

const moduleDir = dirname(fileURLToPath(import.meta.url))

function candidateIdentityPaths(specialization: string): string[] {
  return [
    join('/app/agents', specialization, 'IDENTITY.md'),
    join(moduleDir, '..', '..', '..', 'agents', specialization, 'IDENTITY.md'),
  ]
}

function parseFrontmatter(markdown: string): Record<string, string> {
  const lines = markdown.split('\n')
  if (lines[0]?.trim() !== '---') return {}
  const result: Record<string, string> = {}
  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i]
    if (line.trim() === '---') break
    const match = /^([A-Za-z0-9_]+):\s*(.+?)\s*$/.exec(line)
    if (match) result[match[1]] = match[2]
  }
  return result
}

function parseCapabilities(markdown: string): string[] {
  const lines = markdown.split('\n')
  const start = lines.findIndex(line => line.trim() === '## Capabilities')
  if (start === -1) return []
  const values: string[] = []
  for (let i = start + 1; i < lines.length; i += 1) {
    const trimmed = lines[i].trim()
    if (trimmed.startsWith('## ')) break
    if (trimmed.startsWith('- ')) values.push(trimmed.slice(2).trim())
  }
  return values
}

export function loadIdentityMetadata(specialization: string): IdentityMetadata {
  for (const identityPath of candidateIdentityPaths(specialization)) {
    if (!existsSync(identityPath)) continue
    try {
      const markdown = readFileSync(identityPath, 'utf8')
      const frontmatter = parseFrontmatter(markdown)
      return {
        name: frontmatter.name ?? specialization,
        description: frontmatter.description,
        capabilities: parseCapabilities(markdown),
      }
    } catch {
      continue
    }
  }
  return {
    name: specialization,
    capabilities: [],
  }
}
