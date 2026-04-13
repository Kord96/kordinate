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

export interface ResponseUsageMetadata {
  input_tokens?: number
  cached_input_tokens?: number
  output_tokens?: number
  cache_write_tokens?: number
  estimated_cost?: number
}

export interface ResponseMetadata {
  timing: ResponseTimingMetadata
  usage?: ResponseUsageMetadata
  gateway_timing?: {
    started_at: string
    completed_at: string
    total_ms: number
  }
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

export interface ProgressEventPayload {
  source: 'agent-daemon' | 'provider' | 'gateway'
  kind: string
  sequence?: number
  runtime?: string
  model?: string
  session_id?: string
  structured_log_path?: string
  payload?: Record<string, unknown>
}

export interface ProgressMessage {
  type: 'progress'
  sender: string
  correlation_id: string
  timestamp: string
  event: ProgressEventPayload
}

export type AgentMessage = RequestMessage | ResponseMessage | ProgressMessage

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

export interface AgentVariantSummary {
  name: string
  backend_provider: string
  backend_model: string
  active: boolean
  runtime?: string
}

export interface LogicalAgentRecord {
  name: string
  capabilities: string[]
  backend_provider?: string
  backend_model?: string
  supported_agent_params: string[]
  active: boolean
  default_variant?: string
  variants: AgentVariantSummary[]
}
