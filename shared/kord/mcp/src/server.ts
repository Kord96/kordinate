import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'

const baseUrl = process.env.KORD_API_URL ?? process.env.KORD_GATEWAY_URL ?? 'http://kord-api.kord.svc.cluster.local:9091'
const apiKey = process.env.KORD_API_KEY ?? ''

type Json = Record<string, unknown>

function authHeaders(): Record<string, string> {
  return apiKey ? { 'x-api-key': apiKey } : {}
}

async function getJson(path: string): Promise<unknown> {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: authHeaders(),
  })
  const payload = await response.json()
  if (!response.ok) {
    throw new Error(typeof payload?.error === 'string' ? payload.error : `kord api request failed: ${response.status}`)
  }
  return payload
}

function withQuery(path: string, params: Record<string, string | boolean | undefined>): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) continue
    if (typeof value === 'boolean') {
      if (value) query.set(key, '1')
      continue
    }
    query.set(key, value)
  }
  const suffix = query.size ? `?${query.toString()}` : ''
  return `${path}${suffix}`
}

async function postJson(path: string, body: Json): Promise<unknown> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  })
  const payload = await response.json()
  if (!response.ok) {
    throw new Error(typeof payload?.error === 'string' ? payload.error : `kord api request failed: ${response.status}`)
  }
  return payload
}

function asStructuredContent(payload: unknown): Json {
  if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
    return payload as Json
  }
  return { value: payload }
}

function textResult(payload: unknown, isError = false) {
  return {
    content: [{ type: 'text' as const, text: JSON.stringify(payload, null, 2) }],
    structuredContent: asStructuredContent(payload),
    ...(isError ? { isError: true } : {}),
  }
}

const server = new McpServer({
  name: 'kord',
  version: '0.1.0',
})

server.registerTool(
  'list_agents',
  {
    title: 'List Agents',
    description: 'List logical agents or explicit deployment variants available through kord.',
    inputSchema: {
      variants: z.boolean().optional().default(false),
      verbose: z.boolean().optional().default(false),
    },
  },
  async ({ variants = false, verbose = false }) => {
    try {
      const query = new URLSearchParams()
      if (variants) query.set('view', 'variants')
      if (verbose) query.set('verbose', '1')
      const suffix = query.size ? `?${query.toString()}` : ''
      const payload = await getJson(`/agents${suffix}`)
      return textResult(payload)
    } catch (error) {
      return textResult({ error: error instanceof Error ? error.message : String(error) }, true)
    }
  },
)

server.registerTool(
  'get_agent',
  {
    title: 'Get Agent',
    description: 'Get one logical agent or explicit deployment variant from kord discovery.',
    inputSchema: {
      name: z.string().min(1),
      variant_view: z.boolean().optional().default(false),
      verbose: z.boolean().optional().default(false),
    },
  },
  async ({ name, variant_view = false, verbose = false }) => {
    try {
      const query = new URLSearchParams()
      if (variant_view) query.set('view', 'variants')
      if (verbose) query.set('verbose', '1')
      const suffix = query.size ? `?${query.toString()}` : ''
      const payload = await getJson(`/agents/${encodeURIComponent(name)}${suffix}`)
      return textResult(payload)
    } catch (error) {
      return textResult({ error: error instanceof Error ? error.message : String(error) }, true)
    }
  },
)

server.registerTool(
  'delegate',
  {
    title: 'Delegate',
    description: 'Send a task to a logical agent or explicit variant through kord.',
    inputSchema: {
      agent: z.string().min(1),
      prompt: z.string().min(1),
      working_dir: z.string().optional(),
      timeout_ms: z.number().int().positive().optional(),
      reflect: z.boolean().optional(),
      reflection_prompt: z.string().optional(),
      session_id: z.string().optional(),
      variant: z.string().optional(),
      backend_model: z.string().optional(),
      async: z.boolean().optional(),
      verbose: z.boolean().optional(),
    },
  },
  async ({ agent, prompt, working_dir, timeout_ms, reflect, reflection_prompt, session_id, variant, backend_model, async = false, verbose = false }) => {
    try {
      const body: Json = { prompt, async }
      if (working_dir) body.working_dir = working_dir
      if (timeout_ms !== undefined) body.timeout_ms = timeout_ms
      if (reflect !== undefined) body.reflect = reflect
      if (reflection_prompt) body.reflection_prompt = reflection_prompt
      if (session_id) body.session_id = session_id
      if (variant) body.variant = variant
      if (backend_model) body.backend_model = backend_model
      if (verbose) body.verbose = true
      const payload = await postJson(`/agents/${encodeURIComponent(agent)}/prompt`, body)
      return textResult(payload)
    } catch (error) {
      return textResult({ error: error instanceof Error ? error.message : String(error) }, true)
    }
  },
)

server.registerTool(
  'get_request',
  {
    title: 'Get Request',
    description: 'Fetch the current status of one async kord request.',
    inputSchema: {
      request_id: z.string().min(1),
      verbose: z.boolean().optional(),
    },
  },
  async ({ request_id, verbose = false }) => {
    try {
      const payload = await getJson(withQuery(`/requests/${encodeURIComponent(request_id)}`, { verbose }))
      return textResult(payload)
    } catch (error) {
      return textResult({ error: error instanceof Error ? error.message : String(error) }, true)
    }
  },
)

const transport = new StdioServerTransport()
await server.connect(transport)
