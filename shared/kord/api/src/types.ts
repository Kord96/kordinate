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

export interface ResponseExecutorMetadata {
  name: string
  specialization?: string
  provider: string
  model: string
}

export interface ResponseTimesMetadata {
  gateway_received_at: string
  daemon_started_at: string
  daemon_completed_at: string
}

export interface ResponseMetricsMetadata {
  queue_wait_seconds?: number
  elapsed_seconds?: number
  cpu_time_seconds?: number
  peak_rss_mb?: number
  input_tokens?: number
  cached_input_tokens?: number
  output_tokens?: number
  estimated_cost_usd?: number
}

export interface ResponseTelemetryMetadata {
  request_id: string
  status: JobStatus
  error?: string | null
  executor: ResponseExecutorMetadata
  times: ResponseTimesMetadata
  metrics: ResponseMetricsMetadata
}

export interface ResponseMetadata {
  timing: ResponseTimingMetadata
  usage?: ResponseUsageMetadata
  telemetry?: ResponseTelemetryMetadata
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

export interface RequestTranscriptEvent {
  type:
    | 'request.accepted'
    | 'request.routed'
    | 'agent.started'
    | 'agent.update'
    | 'tool.started'
    | 'tool.finished'
    | 'result.partial'
    | 'result.final'
    | 'request.timed_out'
    | 'request.failed'
  at: string
  request_id: string
  agent?: string
  runtime?: string | null
  model?: string | null
  session_id?: string | null
  topic?: string | null
  tool_name?: string | null
  message?: string | null
  status?: JobStatus | 'timed_out' | null
  error?: string | null
  timeout_ms?: number | null
  agent_may_continue?: boolean | null
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
