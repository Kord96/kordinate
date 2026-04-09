export type MessageType = 'request' | 'response'
export type JobStatus = 'success' | 'error' | 'timeout' | 'cancelled'

export interface ReflectionPayload {
  project: string
  general: string
}

export interface RuntimeRequest {
  prompt: string
  working_dir?: string
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
}

export interface RuntimeResult {
  status: JobStatus
  output: string
  reflection?: ReflectionPayload
  errors?: string[]
  metadata?: ResponseMetadata
}

export interface RequestMessage extends RuntimeRequest {
  type: 'request'
  sender: string
  correlation_id: string
}

export interface ResponseMessage extends RuntimeResult {
  type: 'response'
  sender: string
  correlation_id: string
}

export type AgentMessage = RequestMessage | ResponseMessage

export interface ReflectionEvent {
  agent: string
  task_id?: string
  correlation_id: string
  reflection: ReflectionPayload
}

export interface SessionState {
  key: string
  providerSessionId?: string
  lastCorrelationId?: string
}

export interface AgentProfile {
  promptPrefix?: string
  defaultReflectionPrompt?: string
  supportedAgentParams?: string[]
}

export interface ProviderSessionAdapter {
  startOrResumeWarmSession(session: SessionState): Promise<SessionState>
  executePrompt(session: SessionState, request: RuntimeRequest): Promise<{ session: SessionState; result: RuntimeResult }>
  interruptActiveExecution(session: SessionState): Promise<void>
}

export interface AgentDiscoveryRecord {
  agent: string
  profile: string
  provider: string
  runtime: string
  model: string
  request_topic: string
  reply_mode: 'sender-topic'
  working_dir_supported: boolean
  request_schema: {
    required: string[]
    optional: string[]
  }
  request_example: RequestMessage
  health_url?: string
  working_directory?: string
  supported_agent_params?: string[]
  registered_at: string
  last_seen_at: string
  active?: boolean
  discovery_source?: 'catalog' | 'runtime' | 'catalog+runtime'
}

export interface ResponseTimingMetadata {
  received_at: string
  started_at: string
  completed_at: string
  total_ms: number
  session_prepare_ms: number
  execute_prompt_ms: number
  persist_sessions_ms: number
  publish_response_ms: number
}

export interface ResponseMetadata {
  timing: ResponseTimingMetadata
}
