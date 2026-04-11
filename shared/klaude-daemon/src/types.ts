export type MessageType = 'request' | 'response'
export type JobStatus = 'success' | 'error' | 'timeout' | 'cancelled'

export interface ReflectionPayload {
  project: string
  general: string
}

export interface RuntimeRequest {
  prompt: string
  raw_prompt?: string
  working_dir?: string
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
  session_id?: string
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
  agent_profile?: string
  backend_provider?: string
  backend_runtime?: string
  backend_model?: string
  task_id?: string
  correlation_id: string
  working_dir?: string
  captured_at?: string
  reflection: ReflectionPayload
}

export interface SessionState {
  key: string
  providerSessionId?: string
  lastCorrelationId?: string
}

export interface AgentProfile {
  name?: string
  description?: string
  capabilities?: string[]
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
  name: string
  capabilities: string[]
  backend_provider: string
  backend_model: string
  supported_agent_params: string[]
  active: boolean
  specialization?: string
  runtime?: string
  health_url?: string
  last_seen_at?: string
  request_topic?: string
  default_working_dir?: string
  registered_at?: string
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
