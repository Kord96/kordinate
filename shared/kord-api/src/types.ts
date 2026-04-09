export type JobStatus = 'success' | 'error' | 'timeout' | 'cancelled'

export interface ReflectionPayload {
  project: string
  general: string
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

export interface RequestMessage {
  type: 'request'
  sender: string
  correlation_id: string
  prompt: string
  working_dir?: string
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
  session_id?: string
}

export interface ResponseMessage {
  type: 'response'
  sender: string
  correlation_id: string
  status: JobStatus
  output: string
  reflection?: ReflectionPayload
  errors?: string[]
  metadata?: Record<string, unknown>
}

export type AgentMessage = RequestMessage | ResponseMessage

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
