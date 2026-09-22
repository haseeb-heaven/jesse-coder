/**
 * Main application coordinator for JesseCoder WebApp.
 * Supports dual light/dark themes and self-healing auto-repair execution loops.
 */

import { UIController } from './ui';
import * as api from './api';
import { ExecutionResult, StreamDoneEvent } from './types';

class JesseCoderApp {
  private ui: UIController;
  private lastRawResponse: string = '';
  private lastUserPrompt: string = '';
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
          this.lastUserPrompt = '';
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

  private buildRepairPrompt(
    originalPrompt: string,
    failedCode: string,
    language: string,
    execResult: ExecutionResult,
    attempt: number,
    maxRetries: number
  ): string {
    const diagParts: string[] = [];
    if (execResult.exit_code !== undefined && execResult.exit_code !== null) {
      diagParts.push(`Exit Code: ${execResult.exit_code}`);
    }
    if (execResult.timed_out) {
      diagParts.push(`Status: EXECUTION TIMED OUT`);
    }
    if (execResult.stderr && execResult.stderr.trim()) {
      diagParts.push(`Error Output (stderr / Traceback):\n${execResult.stderr.trim()}`);
    }
    if (execResult.stdout && execResult.stdout.trim()) {
      diagParts.push(`Standard Output (stdout):\n${execResult.stdout.trim()}`);
    }
    const diagnostic = diagParts.length > 0 ? diagParts.join('\n\n') : 'Process exited with non-zero status code.';

    return `[SELF-HEALING AUTO-REPAIR - Attempt ${attempt} of ${maxRetries}]
The previously generated code failed during execution. Please analyze the execution failure below, fix the bug, and provide working code.

### Original User Task:
${originalPrompt}

### Previously Generated Code (${language}):
\`\`\`${language}
${failedCode.trim()}
\`\`\`

### Execution Failure Diagnostic:
${diagnostic}

### Instructions:
1. Explain what caused the error in 1-2 concise sentences.
2. Provide the complete, corrected code enclosed in \`\`\`${language} ... \`\`\`.
3. Ensure the fix resolves the specific error and satisfies the original user task.`;
  }

  private async runAutoRepairLoop(
    originalPrompt: string,
    initialCode: string,
    initialLanguage: string,
    initialResult: ExecutionResult,
    model: string
  ): Promise<void> {
    const maxRetries = this.ui.getMaxRetries();
    let currentAttempt = 1;
    let currentCode = initialCode;
    let currentLanguage = initialLanguage;
    let currentResult = initialResult;

    while (currentAttempt <= maxRetries && !currentResult.success) {
      // Find concise summary of error
      const errorLines = (currentResult.stderr || currentResult.stdout || 'Non-zero exit code')
        .trim()
        .split('\n')
        .filter((l) => l.trim().length > 0);
      const errorSummary = errorLines[errorLines.length - 1] || `Exit code ${currentResult.exit_code}`;

      // Append special auto-repair message bubble
      const { contentEl: repairContentEl } = this.ui.appendRepairMessage(
        currentAttempt,
        maxRetries,
        errorSummary
      );

      const repairPrompt = this.buildRepairPrompt(
        originalPrompt,
        currentCode,
        currentLanguage,
        currentResult,
        currentAttempt,
        maxRetries
      );

      let repairAccumulated = '';
      let repairExtractedCode: { code: string; language: string } | null = null;

      try {
        await api.streamChat(
          repairPrompt,
          model,
          (token: string) => {
            repairAccumulated += token;
            this.ui.updateAssistantStream(repairContentEl, repairAccumulated);
          },
          async (doneData: StreamDoneEvent) => {
            this.lastRawResponse = doneData.raw_response;
            if (doneData.extracted_code && doneData.extracted_code.code.trim()) {
              repairExtractedCode = doneData.extracted_code;
            }
          },
          (err: string) => {
            repairAccumulated += `\n\n> ⚠️ **Repair Stream Error:** ${err}`;
            this.ui.finalizeAssistantMessage(repairContentEl, repairAccumulated);
          }
        );

        if (repairExtractedCode) {
          currentCode = (repairExtractedCode as { code: string; language: string }).code;
          currentLanguage = (repairExtractedCode as { code: string; language: string }).language || currentLanguage;
          this.ui.displayExtractedCode(repairExtractedCode);

          // Re-execute fixed code
          this.ui.setExecutingState(true);
          try {
            currentResult = await api.executeCode(currentCode, currentLanguage);
            this.ui.renderExecutionResult(currentResult);
            this.ui.finalizeAssistantMessage(repairContentEl, repairAccumulated, currentResult);

            if (currentResult.success) {
              this.ui.showToast(`✓ Auto-Repair succeeded on attempt ${currentAttempt}!`, false);
              break;
            } else {
              this.ui.showToast(`Repair attempt ${currentAttempt}/${maxRetries} failed (Exit ${currentResult.exit_code}).`, true);
            }
          } catch (execErr: any) {
            this.ui.showToast(`Repair execution error: ${execErr.message}`, true);
          } finally {
            this.ui.setExecutingState(false);
          }
        } else {
          this.ui.finalizeAssistantMessage(
            repairContentEl,
            `${repairAccumulated}\n\n> ⚠️ *No code block found in repair response.*`
          );
          break;
        }
      } catch (streamErr: any) {
        this.ui.showToast(`Repair loop error: ${streamErr.message}`, true);
        break;
      }

      currentAttempt++;
    }

    if (!currentResult.success && currentAttempt > maxRetries) {
      this.ui.showToast(`Auto-repair reached max retries limit (${maxRetries}).`, true);
    }
  }

  private async handleSubmit(): Promise<void> {
    const prompt = this.ui.getPrompt();
    if (!prompt || this.isProcessing) return;

    this.isProcessing = true;
    this.ui.setInputEnabled(false);
    this.ui.clearPrompt();
    this.lastUserPrompt = prompt;

    // Append user message
    this.ui.appendUserMessage(prompt);

    // Append assistant bubble with streaming placeholder
    const { contentEl } = this.ui.appendAssistantMessage();
    let accumulatedText = '';
    let executionResult: ExecutionResult | null = null;
    let extractedCodeBlock: { code: string; language: string } | null = null;

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
            if (data.extracted_code && data.extracted_code.code.trim()) {
              extractedCodeBlock = data.extracted_code;
            }

            // Auto-run if enabled and executable code exists
            if (this.ui.isAutoRunEnabled() && extractedCodeBlock) {
              this.ui.setExecutingState(true);
              try {
                executionResult = await api.executeCode(
                  extractedCodeBlock.code,
                  extractedCodeBlock.language || 'python'
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

            // Finalize initial assistant turn
            this.ui.finalizeAssistantMessage(contentEl, accumulatedText || data.full_text, executionResult);

            // Self-Healing Auto-Repair: trigger if execution failed and auto-repair is enabled
            if (
              executionResult &&
              !executionResult.success &&
              this.ui.isAutoRepairEnabled() &&
              extractedCodeBlock
            ) {
              await this.runAutoRepairLoop(
                prompt,
                extractedCodeBlock.code,
                extractedCodeBlock.language || 'python',
                executionResult,
                model
              );
            }
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

      // If manual execution failed and Auto-Repair is enabled, initiate repair loop
      if (!res.success && this.ui.isAutoRepairEnabled()) {
        const model = this.ui.getSelectedModel();
        const baseTask = this.lastUserPrompt || `Fix execution error in the provided ${currentCode.language} code.`;
        await this.runAutoRepairLoop(
          baseTask,
          currentCode.code,
          currentCode.language,
          res,
          model
        );
      }
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
