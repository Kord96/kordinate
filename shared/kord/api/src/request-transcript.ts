import type { ProgressMessage, RequestTranscriptEvent, ResponseMessage } from './types.js'

export function summarizeValue(value: unknown, maxLength = 240): string | undefined {
  if (typeof value === 'string') {
    const normalized = value.replace(/\s+/g, ' ').trim()
    if (!normalized) return undefined
    return normalized.length <= maxLength ? normalized : `${normalized.slice(0, maxLength - 3)}...`
  }
  if (value === null || value === undefined) return undefined
  try {
    return summarizeValue(JSON.stringify(value), maxLength)
  } catch {
    return summarizeValue(String(value), maxLength)
  }
}

function extractToolName(payload: Record<string, unknown> | null | undefined): string | undefined {
  if (!payload) return undefined
  if (typeof payload.tool_name === 'string' && payload.tool_name.trim()) return payload.tool_name.trim()
  const message = payload.message
  if (message && typeof message === 'object' && !Array.isArray(message)) {
    const content = (message as { content?: unknown }).content
    if (Array.isArray(content)) {
      const toolUse = content.find(item => item && typeof item === 'object' && (item as { type?: unknown }).type === 'tool_use') as { name?: unknown } | undefined
      if (typeof toolUse?.name === 'string' && toolUse.name.trim()) return toolUse.name.trim()
    }
  }
  if (typeof payload.tool === 'string' && payload.tool.trim()) return payload.tool.trim()
  return undefined
}

function extractAgentMessage(payload: Record<string, unknown> | null | undefined): string | undefined {
  if (!payload) return undefined
  if (typeof payload.message === 'string') return summarizeValue(payload.message)
  const rawMessage = payload.message
  if (rawMessage && typeof rawMessage === 'object' && !Array.isArray(rawMessage)) {
    const content = (rawMessage as { content?: unknown }).content
    if (Array.isArray(content)) {
      for (const item of content) {
        if (!item || typeof item !== 'object') continue
        const text = (item as { text?: unknown }).text
        if (typeof text === 'string' && text.trim()) return summarizeValue(text)
      }
    }
  }
  const result = payload.result
  if (typeof result === 'string' && result.trim()) return summarizeValue(result)
  const text = payload.text
  if (typeof text === 'string' && text.trim()) return summarizeValue(text)
  return undefined
}

function isLowSignalToolName(toolName: string): boolean {
  return ['Read', 'Glob', 'Grep', 'Bash', 'find', 'read_file', 'list_dir'].includes(toolName)
}

export function coalesceTranscriptEvent(previous: RequestTranscriptEvent | undefined, next: RequestTranscriptEvent): boolean {
  if (!previous) return false
  return previous.type === next.type
    && previous.tool_name === next.tool_name
    && previous.message === next.message
    && previous.status === next.status
    && previous.error === next.error
}

export function buildTranscriptEventFromGateway(requestId: string, eventRecord: Record<string, unknown>): RequestTranscriptEvent | undefined {
  const event = typeof eventRecord.event === 'string' ? eventRecord.event : undefined
  const at = typeof eventRecord.timestamp === 'string' ? eventRecord.timestamp : new Date().toISOString()
  const agent = typeof eventRecord.resolved_agent === 'string'
    ? eventRecord.resolved_agent
    : typeof eventRecord.agent === 'string'
      ? eventRecord.agent
      : undefined
  if (event === 'request_received') {
    return { type: 'request.accepted', at, request_id: requestId, agent }
  }
  if (event === 'prompt_published') {
    return {
      type: 'request.routed',
      at,
      request_id: requestId,
      agent,
      topic: typeof eventRecord.topic === 'string' ? eventRecord.topic : null,
    }
  }
  if (event === 'prompt_timeout') {
    return {
      type: 'request.timed_out',
      at,
      request_id: requestId,
      agent,
      timeout_ms: typeof eventRecord.timeout_ms === 'number' ? eventRecord.timeout_ms : null,
      agent_may_continue: true,
      status: 'timed_out',
    }
  }
  if (event === 'request_error') {
    return {
      type: 'request.failed',
      at,
      request_id: requestId,
      agent,
      error: typeof eventRecord.error === 'string' ? eventRecord.error : 'request failed',
      status: 'error',
    }
  }
  return undefined
}

export function buildTranscriptEventFromProgress(message: ProgressMessage): RequestTranscriptEvent | undefined {
  const requestId = message.correlation_id
  const at = message.timestamp
  const payload = (message.event.payload && typeof message.event.payload === 'object' && !Array.isArray(message.event.payload))
    ? message.event.payload as Record<string, unknown>
    : undefined
  const kind = message.event.kind
  const runtime = message.event.runtime ?? null
  const model = message.event.model ?? null
  const sessionId = message.event.session_id ?? null

  if (kind === 'runtime.stream.start') {
    return {
      type: 'agent.started',
      at,
      request_id: requestId,
      runtime,
      model,
      session_id: sessionId,
      message: summarizeValue(payload?.prompt_preview) ?? null,
    }
  }
  if (kind === 'runtime.stream.complete') {
    return {
      type: 'agent.update',
      at,
      request_id: requestId,
      runtime,
      model,
      session_id: sessionId,
      message: 'agent runtime completed',
    }
  }
  if (kind === 'runtime.stream.error') {
    return {
      type: 'request.failed',
      at,
      request_id: requestId,
      runtime,
      model,
      session_id: sessionId,
      error: summarizeValue(payload?.error) ?? 'runtime stream error',
      status: 'error',
    }
  }

  const toolName = extractToolName(payload)
  if (toolName) {
    const isFinish = kind === 'tool_result'
      || kind === 'item.completed'
      || kind === 'item.updated'
      || kind === 'harness_tool_progress'
    if (isLowSignalToolName(toolName)) {
      if (isFinish) return undefined
      return {
        type: 'agent.update',
        at,
        request_id: requestId,
        runtime,
        model,
        session_id: sessionId,
        message: 'agent is gathering context',
      }
    }
    return {
      type: isFinish ? 'tool.finished' : 'tool.started',
      at,
      request_id: requestId,
      runtime,
      model,
      session_id: sessionId,
      tool_name: toolName,
      message: extractAgentMessage(payload) ?? summarizeValue(payload) ?? null,
    }
  }

  const content = extractAgentMessage(payload)
  if (content) {
    return {
      type: kind === 'result' ? 'result.partial' : 'agent.update',
      at,
      request_id: requestId,
      runtime,
      model,
      session_id: sessionId,
      message: content,
    }
  }
  return undefined
}

export function buildFinalTranscriptEvent(requestId: string, agent: string, status: ResponseMessage['status'] | 'timed_out', output: string): RequestTranscriptEvent {
  return {
    type: 'result.final',
    at: new Date().toISOString(),
    request_id: requestId,
    agent,
    status,
    message: summarizeValue(output, 400) ?? null,
  }
}
