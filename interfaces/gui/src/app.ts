/**
 * Main application coordinator for JesseCoder WebApp.
 */

import { UIController } from './ui';
import * as api from './api';
import { ExecutionResult, StreamDoneEvent } from './types';

class JesseCoderApp {
  private ui: UIController;
  private lastRawResponse: string = '';
  private isProcessing: boolean = false;

  constructor() {
    this.ui = new UIController();
    this.bindEvents();
    this.checkBackendHealth();
  }

  private bindEvents(): void {
    const btnSend = document.getElementById('btn-send');
    const promptInput = document.getElementById('prompt-input') as HTMLTextAreaElement;
    const btnRunCode = document.getElementById('btn-run-code');
    const btnToggleRaw = document.getElementById('btn-toggle-raw');
    const btnReset = document.getElementById('btn-reset');
    const chipButtons = document.querySelectorAll('.prompt-chip');

    // Send on button click
    btnSend?.addEventListener('click', () => {
      this.handleSubmit();
    });

    // Send on Enter (unless Shift is held)
    promptInput?.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.handleSubmit();
      }
    });

    // Run code button
    btnRunCode?.addEventListener('click', () => {
      this.handleExecuteCode();
    });

    // Toggle RAW response
    btnToggleRaw?.addEventListener('click', async () => {
      try {
        const rawData = await api.getRawResponse();
        this.lastRawResponse = rawData.raw;
        this.ui.showRawModal(rawData.raw || '(no response yet — send a prompt first)');
      } catch {
        this.ui.showRawModal('Failed to fetch raw API response.');
      }
    });

    // Reset conversation
    btnReset?.addEventListener('click', async () => {
      this.isProcessing = false;
      this.ui.setInputEnabled(true);
      if (confirm('Reset conversation context? This clears history and current session.')) {
        try {
          await api.resetConversation();
          this.ui.clearDialogue();
          this.lastRawResponse = '';
          this.ui.showToast('Conversation context reset.');
        } catch (err: any) {
          this.ui.showToast(`Reset failed: ${err.message}`, true);
        }
      }
    });

    // Quick prompt chips
    chipButtons.forEach((chip) => {
      chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-prompt') || chip.textContent || '';
        promptInput.value = text.trim();
        promptInput.style.height = 'auto';
        promptInput.style.height = `${Math.min(promptInput.scrollHeight, 200)}px`;
        promptInput.focus();
      });
    });

    // Model selection dropdown
    const modelSelect = document.getElementById('model-select') as HTMLSelectElement;
    modelSelect?.addEventListener('change', async () => {
      const selectedModel = modelSelect.value;
      try {
        await api.switchModel(selectedModel);
        this.ui.setStatus(`ONLINE: ${selectedModel}`, true);
        this.ui.showToast(`Switched active model to ${selectedModel}`);
      } catch (err: any) {
        this.ui.showToast(`Model switch failed: ${err.message}`, true);
      }
    });

    // Keyboard shortcuts: Ctrl+E = execute code, Ctrl+R = RAW modal
    document.addEventListener('keydown', (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'e') {
        e.preventDefault();
        this.handleExecuteCode();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r') {
        e.preventDefault();
        btnToggleRaw?.dispatchEvent(new MouseEvent('click'));
      }
    });
  }

  private async checkBackendHealth(): Promise<void> {
    try {
      const health = await api.fetchHealth();
      this.ui.setStatus(`ONLINE: ${health.model}`, true);
      if (health.model) {
        this.ui.setSelectedModel(health.model);
      }
    } catch {
      this.ui.setStatus('DISCONNECTED', false);
    }
  }

  private async handleSubmit(): Promise<void> {
    const prompt = this.ui.getPrompt();
    if (!prompt || this.isProcessing) return;

    this.isProcessing = true;
    this.ui.setInputEnabled(false);
    this.ui.clearPrompt();

    // Append user message
    this.ui.appendUserMessage(prompt);

    // Append assistant bubble with streaming placeholder
    const { contentEl } = this.ui.appendAssistantMessage();
    let accumulatedText = '';
    let executionResult: ExecutionResult | null = null;

    try {
      const model = this.ui.getSelectedModel();

      await api.streamChat(
        prompt,
        model,
        // onToken chunk
        (token: string) => {
          accumulatedText += token;
          this.ui.updateAssistantStream(contentEl, accumulatedText);
        },
        // onDone
        async (data: StreamDoneEvent) => {
          try {
            this.lastRawResponse = data.raw_response;
            this.ui.displayExtractedCode(data.extracted_code);

            // Auto-run if enabled and executable code exists
            if (this.ui.isAutoRunEnabled() && data.extracted_code && data.extracted_code.code.trim()) {
              this.ui.setExecutingState(true);
              try {
                executionResult = await api.executeCode(
                  data.extracted_code.code,
                  data.extracted_code.language || 'python'
                );
                this.ui.renderExecutionResult(executionResult);
                this.ui.showToast(
                  executionResult.success ? 'Auto-execution succeeded!' : 'Auto-execution failed with errors.',
                  !executionResult.success
                );
              } catch (execErr: any) {
                this.ui.showToast(`Execution error: ${execErr.message}`, true);
              } finally {
                this.ui.setExecutingState(false);
              }
            }

            // Finalize assistant turn with code and inline execution card
            this.ui.finalizeAssistantMessage(contentEl, accumulatedText || data.full_text, executionResult);
          } catch (finalizeErr: any) {
            console.error('Error finalizing message:', finalizeErr);
          }
        },
        // onError
        (errorMessage: string) => {
          this.ui.finalizeAssistantMessage(
            contentEl,
            `${accumulatedText}\n\n> ⚠️ **Error:** ${errorMessage}`
          );
          this.ui.showToast(`Error: ${errorMessage}`, true);
        }
      );
    } catch (streamErr: any) {
      this.ui.showToast(`Stream error: ${streamErr.message}`, true);
    } finally {
      // Guaranteed release so next inputs and follow-ups are always enabled
      this.isProcessing = false;
      this.ui.setInputEnabled(true);
    }
  }

  private async handleExecuteCode(): Promise<void> {
    const currentCode = this.ui.getCurrentCode();
    if (!currentCode || !currentCode.code.trim()) {
      this.ui.showToast('No executable code available to run.', true);
      return;
    }

    this.ui.setExecutingState(true);
    try {
      const res = await api.executeCode(currentCode.code, currentCode.language);
      this.ui.renderExecutionResult(res);
      this.ui.showToast(
        res.success ? `Execution SUCCESS (Exit ${res.exit_code})` : `Execution FAILED (Exit ${res.exit_code})`,
        !res.success
      );
    } catch (err: any) {
      this.ui.showToast(`Execution error: ${err.message}`, true);
    } finally {
      this.ui.setExecutingState(false);
    }
  }
}

// Initialize when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  new JesseCoderApp();
});
