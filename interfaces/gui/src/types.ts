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
