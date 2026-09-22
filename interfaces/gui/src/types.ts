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
  showRaw: boolean;
  model: string;
  temperature: number;
}
