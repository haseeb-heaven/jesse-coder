/**
 * TypeScript Type Definitions for JesseCoder WebApp.
 */

export type Role = 'user' | 'assistant' | 'system';

export interface ExtractedCode {
  code: string;
  language: string;
}

export interface ExecutionResult {
  success: boolean;
  exit_code: number;
  stdout: string;
  stderr: string;
  execution_time_ms: number;
  timed_out: boolean;
  command: string[];
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  extractedCode?: ExtractedCode | null;
  executionResult?: ExecutionResult | null;
  rawResponse?: string;
  repairAttempt?: number;
  maxRetries?: number;
}

export interface StreamTokenEvent {
  event: 'token';
  token: string;
}

export interface StreamDoneEvent {
  event: 'done';
  full_text: string;
  extracted_code: ExtractedCode | null;
  raw_response: string;
}

export interface StreamErrorEvent {
  event: 'error';
  message: string;
}

export type StreamEvent = StreamTokenEvent | StreamDoneEvent | StreamErrorEvent;

export interface HealthStatus {
  status: string;
  model: string;
  base_url: string;
  history_count: number;
  has_last_code: boolean;
  has_last_execution: boolean;
}

export interface AppSettings {
  autoRun: boolean;
  autoRepair: boolean;
  maxRetries: number;
  showRaw: boolean;
  model: string;
  temperature: number;
  theme: 'dark' | 'light';
}

export interface AutoRepairAttempt {
  attempt: number;
  maxRetries: number;
  failedCode: string;
  language: string;
  diagnostic: string;
}

// ---------------------------------------------------------------------------
// Feedback (jesse-prod learning)
// ---------------------------------------------------------------------------

export type FeedbackRating = 'thumbs_up' | 'thumbs_down';

export interface FeedbackRequest {
  message_id: string;
  rating: FeedbackRating;
  correction?: string;
  model?: string;
}

export interface FeedbackResponse {
  status: string;
  detail: unknown;
}

// ---------------------------------------------------------------------------
// Memory
// ---------------------------------------------------------------------------

export interface MemoryFact {
  key?: string;
  value?: string;
  fact?: string;
  [key: string]: unknown;
}

export interface MemoryResponse {
  status: string;
  data: unknown;
  detail?: string;
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export interface JesseDocument {
  id?: string;
  title: string;
  content?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface DocumentListResponse {
  status: string;
  data: unknown;
  detail?: string;
}

export interface DocumentQueryResult {
  id?: string;
  title?: string;
  content?: string;
  score?: number;
  [key: string]: unknown;
}

export interface DocumentQueryResponse {
  status: string;
  data: unknown;
  detail?: string;
}

// ---------------------------------------------------------------------------
// Settings & Configuration
// ---------------------------------------------------------------------------

export interface ServerSettings {
  has_api_key: boolean;
  api_key_masked: string;
  base_url: string;
  model: string;
  is_vercel: boolean;
  saved_to_env?: boolean;
}

export interface SettingsUpdateRequest {
  api_key?: string;
  base_url?: string;
  model?: string;
}

export interface VerifyConnectionResponse {
  valid: boolean;
  models?: string[];
  error?: string;
}

// ---------------------------------------------------------------------------
// Benchmarks & Automated Testing
// ---------------------------------------------------------------------------

export interface TestingDataset {
  id: string;
  name: string;
  description: string;
  filename: string;
  task_count: number;
  mode: string;
}

export interface TestingTask {
  id: string;
  title: string;
  description: string;
  language: string;
  mode?: string;
  buggy_code?: string;
  buggy_output?: string;
  expected_output: string;
  input?: string;
  exact_code?: string;
  fixed_code?: string;
}

export interface TestingRunParams {
  dataset?: string;
  task_id?: string;
  model?: string;
  retries?: number;
  repair?: boolean;
  train_model?: boolean;
  strict_output?: boolean;
  language?: string;
}

export interface TestingTaskResult {
  task_id: string;
  title: string;
  language: string;
  mode?: string;
  status: 'PASS' | 'FAIL' | 'PASSED' | 'FAILED';
  passed_on_attempt: number;
  total_attempts: number;
  duration_sec: number;
  actual_output?: string;
  expected_output?: string;
  extracted_code?: string;
  error?: string;
  initial_passed?: boolean;
}

export interface TestingModelEvaluation {
  model: string;
  total: number;
  passed: number;
  failed: number;
  passed_initial: number;
  passed_on_retry: number;
  pass_rate_pct: number;
  total_duration_sec: number;
  results: TestingTaskResult[];
}

export interface TestingRunResponse {
  status: string;
  dataset: string;
  tasks_count: number;
  models: string[];
  primary_model: string;
  primary_data: TestingModelEvaluation;
  all_models_data?: TestingModelEvaluation[];
  primary_json_path: string;
  primary_md_path: string;
  comp_json_path?: string | null;
  comp_md_path?: string | null;
}

export interface TestingReportSummary {
  filename: string;
  type: 'markdown' | 'json';
  size_bytes: number;
  modified: string;
}

export interface TestingReportDetail {
  status: string;
  filename: string;
  type: 'markdown' | 'json';
  content: string;
}


