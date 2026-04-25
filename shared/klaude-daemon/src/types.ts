export type MessageType = 'request' | 'response' | 'progress'
export type JobStatus = 'success' | 'error' | 'timeout' | 'cancelled'

export interface ReflectionPayload {
  project: string
  general: string
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

export type ProgressReporter = (event: ProgressEventPayload) => void | Promise<void>

export interface PromptPlan {
  fullPrompt: string
  dynamicPrompt: string
  cacheablePrefix?: string
  cacheKey?: string
  cacheStrategy?: 'provider' | 'session'
}

export interface RuntimeRequest {
  prompt: string
  raw_prompt?: string
  promptPlan?: PromptPlan
  working_dir?: string
  workspace?: WorkspaceContract
  resources?: AgentResourceContract
  timeout_ms?: number
  reflect?: boolean
  reflection_prompt?: string
  agent_params?: Record<string, unknown>
  session_id?: string
  progress?: ProgressReporter
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

export interface ProgressMessage {
  type: 'progress'
  sender: string
  correlation_id: string
  timestamp: string
  event: ProgressEventPayload
}

export type AgentMessage = RequestMessage | ResponseMessage | ProgressMessage

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
  promptCacheKey?: string
}

export interface ValidationContract {
  required: boolean
  validatorScript: string
  maxAttempts?: number
  finalizeScript?: string
}

export interface WorkflowContract {
  analysisContextScript?: string
  repairPromptScript?: string
}

export interface BundleRefs {
  memory?: string
  skill?: string
  runtime?: string
}

export interface WorkspaceContract {
  working_dir: string
  output_dir: string
  agent_root?: string
}

export interface AgentResourceContract {
  validator_script?: string
  concept_catalog_index?: string
  framework_catalog_index?: string
}

export interface AgentContract {
  version?: string
  name: string
  specialization: string
  description?: string
  capabilities: string[]
  acceptedRequestPrefixes?: string[]
  promptPrefix?: string
  defaultReflectionPrompt?: string
  supportedAgentParams: string[]
  requiresWorkingDirectory: boolean
  bundleRefs?: BundleRefs
  workflow?: WorkflowContract
  validation?: ValidationContract
}

export interface RuntimeProfile {
  version?: string
  kind: string
  promptPreamble?: string
  toolGuidance?: string[]
  runArtifactGuidance?: string[]
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
  timing?: ResponseTimingMetadata
  usage?: ResponseUsageMetadata
  telemetry?: ResponseTelemetryMetadata
  artifacts?: {
    root?: string
    files?: Record<string, string>
    schemas?: Record<string, string>
  }
  validation?: {
    required: boolean
    passed: boolean
    attempts: number
    token?: string
    target_dir?: string
  }
}
