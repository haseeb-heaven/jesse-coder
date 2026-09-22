/**
 * API client module for JesseCoder backend communication.
 * Handles SSE streaming, code execution, context reset, health checks,
 * feedback submission, memory management, and document store/search.
 */

import {
  ExecutionResult,
  FeedbackRating,
  FeedbackResponse,
  HealthStatus,
  MemoryResponse,
  DocumentListResponse,
  DocumentQueryResponse,
  StreamDoneEvent,
  StreamEvent,
} from './types';

const API_BASE = window.location.origin;

export async function fetchHealth(): Promise<HealthStatus> {
  const resp = await fetch(`${API_BASE}/api/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed: ${resp.statusText}`);
  }
  return resp.json();
}

export async function resetConversation(): Promise<void> {
  const resp = await fetch(`${API_BASE}/api/reset`, { method: 'POST' });
  if (!resp.ok) {
    throw new Error(`Reset failed: ${resp.statusText}`);
  }
}

export async function switchModel(model: string): Promise<string> {
  const resp = await fetch(`${API_BASE}/api/model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model }),
  });
  if (!resp.ok) {
    throw new Error(`Failed to switch model: ${resp.statusText}`);
  }
  const data = await resp.json();
  return data.model;
}

export async function executeCode(
  code: string,
  language: string = 'python',
  timeout: number = 15.0
): Promise<ExecutionResult> {
  const resp = await fetch(`${API_BASE}/api/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, timeout }),
  });

  if (!resp.ok) {
    throw new Error(`Execution request failed: ${resp.statusText}`);
  }
  return resp.json();
}

export interface RawApiPayload {
  raw: string;
  was_canned: boolean;
  note?: string;
  char_count?: number;
}

export async function getRawResponse(): Promise<RawApiPayload> {
  const resp = await fetch(`${API_BASE}/api/raw`);
  if (!resp.ok) {
    return { raw: '', was_canned: false };
  }
  const data = await resp.json();
  return {
    raw: data.raw || '',
    was_canned: !!data.was_canned,
    note: data.note || '',
    char_count: data.char_count || 0,
  };
}

// ---------------------------------------------------------------------------
// Feedback — let jesse-prod learn from right/wrong answers
// ---------------------------------------------------------------------------

export async function submitFeedback(
  messageId: string,
  rating: FeedbackRating,
  correction?: string
): Promise<FeedbackResponse> {
  const body: Record<string, unknown> = { message_id: messageId, rating };
  if (correction && correction.trim()) body.correction = correction.trim();
  const resp = await fetch(`${API_BASE}/api/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  // Feedback always returns gracefully (degraded if API doesn't support it)
  return resp.json();
}

// ---------------------------------------------------------------------------
// Memory — view and erase what Jesse remembers
// ---------------------------------------------------------------------------

export async function getMemory(): Promise<MemoryResponse> {
  const resp = await fetch(`${API_BASE}/api/memory`);
  return resp.json();
}

export async function deleteMemory(): Promise<MemoryResponse> {
  const resp = await fetch(`${API_BASE}/api/memory`, { method: 'DELETE' });
  return resp.json();
}

// ---------------------------------------------------------------------------
// Documents — store, list, and search
// ---------------------------------------------------------------------------

export async function storeDocument(
  title: string,
  content: string,
  metadata?: Record<string, unknown>
): Promise<DocumentListResponse> {
  const resp = await fetch(`${API_BASE}/api/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, metadata }),
  });
  return resp.json();
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const resp = await fetch(`${API_BASE}/api/documents`);
  return resp.json();
}

export async function queryDocuments(
  query: string,
  topK: number = 5
): Promise<DocumentQueryResponse> {
  const resp = await fetch(`${API_BASE}/api/documents/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  });
  return resp.json();
}

// ---------------------------------------------------------------------------
// Chat streaming (SSE)
// ---------------------------------------------------------------------------

export async function streamChat(
  prompt: string,
  model: string,
  onToken: (token: string) => void,
  onDone: (data: StreamDoneEvent) => Promise<void> | void,
  onError: (errorMsg: string) => Promise<void> | void
): Promise<void> {
  let doneOrErrorReceived = false;

  try {
    const response = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model }),
    });

    if (!response.ok) {
      const errText = await response.text();
      await onError(`Server error (${response.status}): ${errText}`);
      return;
    }

    if (!response.body) {
      await onError('No response stream body available.');
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    const processLine = async (line: string): Promise<void> => {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith('data: ')) return;

      const jsonStr = trimmed.substring(6).trim();
      try {
        const eventData: StreamEvent = JSON.parse(jsonStr);
        if (eventData.event === 'token') {
          onToken(eventData.token);
        } else if (eventData.event === 'done') {
          doneOrErrorReceived = true;
          await onDone(eventData);
        } else if (eventData.event === 'error') {
          doneOrErrorReceived = true;
          await onError(eventData.message);
        }
      } catch (e) {
        console.warn('Failed to parse SSE line:', jsonStr, e);
      }
    };

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        await processLine(line);
      }
    }

    // Process any remaining bytes in the buffer
    if (buffer.trim()) {
      await processLine(buffer);
    }

    // If stream closed without explicit done/error, trigger fallback done event
    if (!doneOrErrorReceived) {
      await onDone({
        event: 'done',
        full_text: '',
        extracted_code: null,
        raw_response: '',
      });
    }
  } catch (err: any) {
    await onError(`Network/Stream error: ${err?.message || err}`);
  }
}
