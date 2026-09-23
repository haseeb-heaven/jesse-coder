/**
 * Main application coordinator for JesseCoder WebApp.
 * Supports dual light/dark themes, self-healing auto-repair execution loops,
 * feedback submission, memory management, and document store/search.
 */

import { UIController } from './ui';
import * as api from './api';
import { ExecutionResult, StreamDoneEvent, SettingsUpdateRequest, TestingTask } from './types';

class JesseCoderApp {
  private ui: UIController;
  private lastRawResponse: string = '';
  private lastUserPrompt: string = '';
  private isProcessing: boolean = false;
  /** Tracks the DOM element of the last finalized assistant message for feedback. */
  private lastAssistantMsgEl: HTMLElement | null = null;
  private lastAssistantMsgId: string = '';

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

    // ── Memory panel ─────────────────────────────────────────────────────────
    const btnMemory = document.getElementById('btn-memory');
    btnMemory?.addEventListener('click', () => {
      this.ui.showMemoryPanel();
      this.loadMemory();
    });

    document.getElementById('btn-close-memory')?.addEventListener('click', () => {
      this.ui.hideMemoryPanel();
    });

    document.getElementById('btn-memory-refresh')?.addEventListener('click', () => {
      this.loadMemory();
    });

    document.getElementById('btn-memory-erase')?.addEventListener('click', async () => {
      if (!confirm('Erase ALL of Jesse\'s memory for this API key? This cannot be undone.')) return;
      try {
        const result = await api.deleteMemory();
        this.ui.showToast(result.status === 'ok' ? '🗑️ Memory erased!' : '⚠️ Memory erase had issues', result.status !== 'ok');
        this.loadMemory();
      } catch (err: any) {
        this.ui.showToast(`Memory erase failed: ${err.message}`, true);
      }
    });

    // ── Docs panel ───────────────────────────────────────────────────────────
    const btnDocs = document.getElementById('btn-documents');
    btnDocs?.addEventListener('click', () => {
      this.ui.showDocsPanel('store');
    });

    document.getElementById('btn-close-docs')?.addEventListener('click', () => {
      this.ui.hideDocsPanel();
    });

    // Tab switching
    document.querySelectorAll('.docs-tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        const tab = btn.getAttribute('data-docs-tab') || 'store';
        this.ui.switchDocsTab(tab);
        if (tab === 'list') this.loadDocsList();
      });
    });

    // Store document
    document.getElementById('btn-doc-store')?.addEventListener('click', async () => {
      const titleInput = document.getElementById('doc-title-input') as HTMLInputElement;
      const contentInput = document.getElementById('doc-content-input') as HTMLTextAreaElement;
      const title = titleInput?.value.trim();
      const content = contentInput?.value.trim();
      if (!title || !content) {
        this.ui.showDocStoreResult('⚠️ Title and content are required.', true);
        return;
      }
      try {
        const result = await api.storeDocument(title, content);
        const ok = result.status === 'ok';
        this.ui.showDocStoreResult(
          ok ? `✅ Document "${title}" stored successfully!` : `⚠️ Store may have issues: ${result.detail}`,
          !ok
        );
        if (ok) { titleInput.value = ''; contentInput.value = ''; }
      } catch (err: any) {
        this.ui.showDocStoreResult(`❌ Error: ${err.message}`, true);
      }
    });

    // List documents (refresh)
    document.getElementById('btn-docs-refresh')?.addEventListener('click', () => {
      this.loadDocsList();
    });

    // Search documents
    document.getElementById('btn-doc-search')?.addEventListener('click', () => {
      this.handleDocSearch();
    });
    const docQueryInput = document.getElementById('doc-query-input') as HTMLInputElement;
    docQueryInput?.addEventListener('keydown', (e: KeyboardEvent) => {
      if (e.key === 'Enter') this.handleDocSearch();
    });

    // ── Settings modal ────────────────────────────────────────────────────────
    const btnSettings = document.getElementById('btn-settings');
    btnSettings?.addEventListener('click', async () => {
      await this.openSettings();
    });

    document.getElementById('btn-save-settings')?.addEventListener('click', async () => {
      await this.handleSaveSettings();
    });

    document.getElementById('btn-verify-key')?.addEventListener('click', async () => {
      await this.handleVerifyKey();
    });

    // ── BYOK (Bring Your Own Key) Banner & Badge Click ────────────────────────
    document.getElementById('btn-byok-settings')?.addEventListener('click', async () => {
      await this.openSettings();
    });

    document.getElementById('btn-byok-dismiss')?.addEventListener('click', () => {
      this.ui.hideByokBanner();
    });

    document.getElementById('status-badge')?.addEventListener('click', async () => {
      const storedKey = api.getStoredApiKey();
      if (!storedKey) {
        await this.openSettings();
      }
    });

    // ── Benchmarks & Automated Testing Suite ──────────────────────────────────
    document.getElementById('btn-benchmarks')?.addEventListener('click', async () => {
      await this.openBenchmarks();
    });

    document.querySelectorAll('.bench-tab').forEach((tab) => {
      tab.addEventListener('click', async (e) => {
        const target = (e.currentTarget as HTMLElement).getAttribute('data-bench-tab');
        if (target) {
          this.ui.setBenchmarksTab(target);
          if (target === 'tasks') {
            await this.loadBenchmarkTasks();
          } else if (target === 'reports') {
            await this.loadBenchmarkReports();
          }
        }
      });
    });

    document.getElementById('bench-dataset-select')?.addEventListener('change', async () => {
      await this.syncBenchmarkTaskDropdown();
    });

    document.getElementById('bench-difficulty-select')?.addEventListener('change', async () => {
      await this.syncBenchmarkTaskDropdown();
    });

    document.getElementById('bench-language-select')?.addEventListener('change', async () => {
      await this.syncBenchmarkTaskDropdown();
    });

    document.getElementById('bench-explore-dataset')?.addEventListener('change', async () => {
      await this.loadBenchmarkTasks();
    });

    document.getElementById('bench-explore-difficulty')?.addEventListener('change', async () => {
      await this.loadBenchmarkTasks();
    });

    document.getElementById('btn-run-benchmark')?.addEventListener('click', async () => {
      await this.handleRunBenchmark();
    });

    document.getElementById('btn-refresh-reports')?.addEventListener('click', async () => {
      await this.loadBenchmarkReports();
    });

    document.getElementById('bench-reports-select')?.addEventListener('change', async (e) => {
      const filename = (e.target as HTMLSelectElement).value;
      if (filename) {
        await this.loadBenchmarkReportContent(filename);
      }
    });
  }

  private async checkBackendHealth(): Promise<void> {
    try {
      const storedKey = api.getStoredApiKey();
      const health = await api.fetchHealth();
      if (health.model) {
        this.ui.setSelectedModel(health.model);
      }
      if (storedKey || health.has_api_key) {
        this.ui.setStatus(`ONLINE: ${health.model}`, 'online');
        this.ui.hideByokBanner();
      } else {
        this.ui.setStatus('BYOK: Key Required', 'byok');
        this.ui.showByokBanner();
      }
    } catch {
      this.ui.setStatus('DISCONNECTED', 'offline');
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

    const storedKey = api.getStoredApiKey();
    if (!storedKey) {
      this.ui.showToast('🔑 Jesse API Key Required: Please enter your key in Settings (⚙️) to start coding.', true);
      await this.openSettings();
      return;
    }

    this.isProcessing = true;
    this.ui.setInputEnabled(false);
    this.ui.clearPrompt();
    this.lastUserPrompt = prompt;

    // Append user message
    this.ui.appendUserMessage(prompt);

    // Append assistant bubble with streaming placeholder
    const { contentEl, msgId } = this.ui.appendAssistantMessage();
    let accumulatedText = '';
    let executionResult: ExecutionResult | null = null;
    let extractedCodeBlock: { code: string; language: string } | null = null;
    this.lastAssistantMsgId = msgId;

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

            // Inject 👍/👎 feedback buttons
            const bubbleEl = contentEl.closest('.assistant-turn') as HTMLElement | null;
            if (bubbleEl) {
              this.ui.addFeedbackButtons(
                contentEl,
                () => { this.handleFeedback(msgId, bubbleEl, 'thumbs_up'); },
                () => {
                  this.ui.showFeedbackModal(
                    (correction: string) => { this.handleFeedback(msgId, bubbleEl, 'thumbs_down', correction || undefined); },
                    () => { this.ui.showToast('Feedback cancelled.'); }
                  );
                }
              );
            }

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

  // --------------------------------------------------------------------------
  // Memory helpers
  // --------------------------------------------------------------------------

  private async loadMemory(): Promise<void> {
    const contentEl = document.getElementById('memory-content');
    if (contentEl) contentEl.innerHTML = '<span class="text-slate-400 italic animate-pulse">Loading...</span>';
    try {
      const result = await api.getMemory();
      this.ui.renderMemoryContent(result.data ?? result, result.status === 'degraded');
    } catch (err: any) {
      this.ui.renderMemoryContent(`Failed to load memory: ${err.message}`, true);
    }
  }

  // --------------------------------------------------------------------------
  // Document helpers
  // --------------------------------------------------------------------------

  private async loadDocsList(): Promise<void> {
    const el = document.getElementById('docs-list-content');
    if (el) el.innerHTML = '<span class="text-slate-400 italic animate-pulse">Loading...</span>';
    try {
      const result = await api.listDocuments();
      this.ui.renderDocsList(result.data ?? result, result.status === 'degraded');
    } catch (err: any) {
      this.ui.renderDocsList(`Failed to load documents: ${err.message}`, true);
    }
  }

  private async handleDocSearch(): Promise<void> {
    const queryInput = document.getElementById('doc-query-input') as HTMLInputElement;
    const topKSelect = document.getElementById('doc-topk-select') as HTMLSelectElement;
    const query = queryInput?.value.trim();
    if (!query) {
      this.ui.showToast('Please enter a search query.', true);
      return;
    }
    const topK = parseInt(topKSelect?.value || '5', 10);
    const resultsEl = document.getElementById('doc-search-results');
    if (resultsEl) resultsEl.innerHTML = '<span class="text-slate-400 italic animate-pulse">Searching...</span>';
    try {
      const result = await api.queryDocuments(query, topK);
      this.ui.renderDocSearchResults(result.data ?? result, result.status === 'degraded');
    } catch (err: any) {
      this.ui.renderDocSearchResults(`Search failed: ${err.message}`, true);
    }
  }

  // --------------------------------------------------------------------------
  // Feedback helper — called from feedback buttons on assistant bubbles
  // --------------------------------------------------------------------------

  private async handleFeedback(
    msgId: string,
    msgEl: HTMLElement,
    rating: 'thumbs_up' | 'thumbs_down',
    correction?: string
  ): Promise<void> {
    try {
      await api.submitFeedback(msgId, rating, correction);
      if (rating === 'thumbs_up') {
        this.ui.showToast('👍 Thanks! jesse-prod learned from this.');
      } else {
        this.ui.showToast(
          correction ? '👎 Correction submitted — jesse-prod will improve!' : '👎 Marked as wrong.'
        );
      }
    } catch (err: any) {
      this.ui.showToast(`Feedback failed: ${err.message}`, true);
    }
  }

  // --------------------------------------------------------------------------
  // Settings & Configuration helpers
  // --------------------------------------------------------------------------

  private async openSettings(): Promise<void> {
    try {
      const settings = await api.getSettings();
      const storedKey = api.getStoredApiKey();
      if (storedKey && (!settings.has_api_key || !settings.api_key_masked)) {
        settings.has_api_key = true;
        settings.api_key_masked = storedKey.length > 8
          ? `${storedKey.slice(0, 8)}${'•'.repeat(8)}${storedKey.slice(-4)}`
          : '•'.repeat(storedKey.length);
      }
      this.ui.populateSettings(settings, this.ui.getMaxRetries());
      this.ui.showSettingsModal();
    } catch (err: any) {
      this.ui.showToast(`Failed to load settings: ${err.message}`, true);
    }
  }

  private async handleVerifyKey(): Promise<void> {
    const form = this.ui.getSettingsFormValues();
    const endpointLabel = form.baseUrl || 'configured endpoint';
    this.ui.setVerifyStatus(`Connecting to ${endpointLabel}...`, 'loading');

    try {
      const result = await api.verifySettings(form.apiKey || undefined, form.baseUrl || undefined);
      if (result.valid) {
        const modelsCount = result.models ? result.models.length : 0;
        this.ui.setVerifyStatus(`✅ Valid (${modelsCount} models accessible)`, 'success');
      } else {
        this.ui.setVerifyStatus(`❌ Invalid: ${result.error || 'Connection failed'}`, 'error');
      }
    } catch (err: any) {
      this.ui.setVerifyStatus(`❌ Error: ${err.message}`, 'error');
    }
  }

  private async handleSaveSettings(): Promise<void> {
    const form = this.ui.getSettingsFormValues();
    const saveBtn = document.getElementById('btn-save-settings') as HTMLButtonElement;
    if (saveBtn) {
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<span>Saving...</span>';
    }

    try {
      if (form.apiKey && form.apiKey.trim()) {
        api.setStoredApiKey(form.apiKey.trim());
      }

      const updateReq: SettingsUpdateRequest = {
        api_key: form.apiKey || undefined,
        base_url: form.baseUrl || undefined,
        model: form.model || undefined,
      };

      const updated = await api.updateSettings(updateReq);

      if (form.retries) {
        this.ui.setRetries(form.retries);
      }
      if (form.model) {
        this.ui.setSelectedModel(form.model);
      }

      this.ui.hideSettingsModal();

      if (updated.is_vercel || updated.byok_mode) {
        this.ui.showToast('✅ Key saved locally in browser! (Bring Your Own Key mode)');
      } else if (updated.saved_to_env) {
        this.ui.showToast('✅ Settings saved to .env & active session!');
      } else {
        this.ui.showToast('✅ Settings updated for active session!');
      }

      await this.checkBackendHealth();
    } catch (err: any) {
      this.ui.showToast(`Failed to save settings: ${err.message}`, true);
    } finally {
      if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<span>💾 Save Settings</span>';
      }
    }
  }

  // --------------------------------------------------------------------------
  // Benchmarks & Automated Testing Coordinators
  // --------------------------------------------------------------------------

  private async openBenchmarks(): Promise<void> {
    this.ui.showBenchmarksModal();
    this.ui.setBenchmarksTab('run');
    await this.syncBenchmarkTaskDropdown();
  }

  private async syncBenchmarkTaskDropdown(): Promise<void> {
    const sel = document.getElementById('bench-dataset-select') as HTMLSelectElement | null;
    const diffSel = document.getElementById('bench-difficulty-select') as HTMLSelectElement | null;
    const languageSel = document.getElementById('bench-language-select') as HTMLSelectElement | null;
    const dataset = sel?.value || 'task_bug_issues.json';
    const difficulty = diffSel?.value || undefined;
    const language = languageSel?.value || undefined;
    try {
      const tasks = await api.fetchTestingTasks(dataset, language, difficulty);
      this.ui.populateBenchmarkTaskFilters(tasks);
    } catch (err: any) {
      console.warn('Failed to populate task filter dropdown:', err);
    }
  }

  private async loadBenchmarkTasks(): Promise<void> {
    const sel = document.getElementById('bench-explore-dataset') as HTMLSelectElement | null;
    const diffSel = document.getElementById('bench-explore-difficulty') as HTMLSelectElement | null;
    const dataset = sel?.value || 'task_bug_issues.json';
    const difficulty = diffSel?.value || undefined;
    try {
      const tasks = await api.fetchTestingTasks(dataset, undefined, difficulty);
      this.ui.renderExploreTasks(tasks, (task) => this.handleLoadTaskIntoChat(task));
    } catch (err: any) {
      this.ui.showToast(`Failed to load tasks: ${err.message}`, true);
    }
  }

  private handleLoadTaskIntoChat(task: TestingTask): void {
    let prompt = '';
    const desc = (task as any).task || task.description || '';
    if (task.buggy_code) {
      prompt = `Fix the bug in the following ${task.language} code so that it produces the expected output.

Buggy Code:
\`\`\`${task.language}
${task.buggy_code.trim()}
\`\`\`

${task.buggy_output ? `Buggy Output:\n${task.buggy_output.trim()}\n\n` : ''}Expected Output:
${task.expected_output.trim()}`;
    } else {
      prompt = `${desc}

${task.input ? `Input:\n${task.input.trim()}\n\n` : ''}Expected Output:
${task.expected_output.trim()}`;
    }

    this.ui.setPrompt(prompt);
    if (task.language) {
      this.ui.setLanguage(task.language);
    }
    this.ui.hideBenchmarksModal();
    this.ui.showToast(`🚀 Loaded "${task.title}" (${task.language}) into Chat & Editor!`);
  }

  private async handleRunBenchmark(): Promise<void> {
    const datasetSel = document.getElementById('bench-dataset-select') as HTMLSelectElement | null;
    const diffSel = document.getElementById('bench-difficulty-select') as HTMLSelectElement | null;
    const modelSel = document.getElementById('bench-model-select') as HTMLSelectElement | null;
    const taskFilter = document.getElementById('bench-task-filter') as HTMLSelectElement | null;
    const retriesSel = document.getElementById('bench-retries-select') as HTMLSelectElement | null;
    const repairToggle = document.getElementById('bench-repair-toggle') as HTMLInputElement | null;
    const trainToggle = document.getElementById('bench-train-toggle') as HTMLInputElement | null;
    const strictToggle = document.getElementById('bench-strict-output-toggle') as HTMLInputElement | null;
    const languageSel = document.getElementById('bench-language-select') as HTMLSelectElement | null;

    const dataset = datasetSel?.value || 'task_bug_issues.json';
    const difficulty = diffSel?.value || undefined;
    const model = modelSel?.value || 'jesse-prod';
    const taskId = taskFilter?.value || undefined;
    const retriesValue = parseInt(retriesSel?.value || '5', 10);
    const retries = Number.isFinite(retriesValue) ? retriesValue : 5;
    const repair = repairToggle ? repairToggle.checked : true;
    const trainModel = trainToggle ? trainToggle.checked : false;

    this.ui.setBenchmarkRunning(true);
    const diffLabel = difficulty ? ` [${difficulty.toUpperCase()}]` : '';
    this.ui.showToast(`▶ Running benchmark on ${dataset}${diffLabel}...`, false);

    try {
      const resp = await api.runTestingBenchmark({
        dataset,
        model,
        task_id: taskId,
        difficulty,
        retries,
        repair,
        train_model: trainModel,
        strict_output: strictToggle?.checked || false,
        language: languageSel?.value || undefined,
      });

      this.ui.renderBenchmarkResults(resp);
      const passed = resp.primary_data.passed;
      const total = resp.primary_data.total;
      const pct = (resp.primary_data.pass_rate_pct || 0).toFixed(1);
      this.ui.showToast(`✔ Benchmark finished: ${passed}/${total} Passed (${pct}%)`);
    } catch (err: any) {
      this.ui.showToast(`❌ Benchmark execution error: ${err.message}`, true);
    } finally {
      this.ui.setBenchmarkRunning(false);
    }
  }

  private async loadBenchmarkReports(): Promise<void> {
    try {
      const reports = await api.fetchTestingReports();
      this.ui.renderReportsList(reports);
      if (reports.length > 0) {
        await this.loadBenchmarkReportContent(reports[0].filename);
      }
    } catch (err: any) {
      this.ui.showToast(`Failed to load reports: ${err.message}`, true);
    }
  }

  private async loadBenchmarkReportContent(filename: string): Promise<void> {
    try {
      const detail = await api.fetchTestingReportContent(filename);
      this.ui.renderReportContent(detail.content, detail.type);
    } catch (err: any) {
      this.ui.showToast(`Failed to load report content: ${err.message}`, true);
    }
  }
}

// Initialize when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  new JesseCoderApp();
});
