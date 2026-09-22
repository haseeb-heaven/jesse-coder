/**
 * UI controller and DOM manipulation for JesseCoder WebApp.
 */

import { ChatMessage, ExecutionResult, ExtractedCode, ServerSettings } from './types';
import { renderMarkdown, escapeHtml } from './markdown';

export interface RawPayload {
  raw: string;
  was_canned?: boolean;
  note?: string;
}

export class UIController {
  // Elements
  private dialogueEl: HTMLElement;
  private promptInputEl: HTMLTextAreaElement;
  private btnSendEl: HTMLButtonElement;
  private autoRunToggleEl: HTMLInputElement;
  private autoRepairToggleEl: HTMLInputElement;
  private retriesSelectEl: HTMLSelectElement;
  private themeToggleBtnEl: HTMLButtonElement;
  private themeSunIconEl: HTMLElement;
  private themeMoonIconEl: HTMLElement;
  private rawToggleBtnEl: HTMLButtonElement;
  private btnResetEl: HTMLButtonElement;
  private modelSelectEl: HTMLSelectElement;
  private statusBadgeEl: HTMLElement;

  // Language pickers
  private langSelectEl: HTMLSelectElement;        // header-level override
  private blockLangOverrideEl: HTMLSelectElement; // per-block override in workbench

  // Code workbench elements
  private codeLangBadgeEl: HTMLElement;
  private codeLineCountEl: HTMLElement;
  private codeContentEl: HTMLElement;
  private btnRunCodeEl: HTMLButtonElement;
  private btnCopyCodeEl: HTMLButtonElement;

  // Execution console elements
  private execStatusBadgeEl: HTMLElement;
  private execTimeBadgeEl: HTMLElement;
  private execCommandBadgeEl: HTMLElement;
  private consoleOutputEl: HTMLElement;
  private btnClearConsoleEl: HTMLButtonElement;

  // Raw viewer modal
  private rawModalEl: HTMLElement;
  private rawContentEl: HTMLElement;
  private rawCannedWarningEl: HTMLElement;
  private rawQualityBadgeEl: HTMLElement;
  private rawStatsBarEl: HTMLElement;
  private rawCharCountEl: HTMLElement;
  private rawHasCodeEl: HTMLElement;
  private rawModelInfoEl: HTMLElement;
  private btnCloseRawEl: HTMLElement;
  private btnCopyRawEl: HTMLButtonElement;

  // Settings modal elements
  private settingsModalEl: HTMLElement;
  private settingsApiKeyEl: HTMLInputElement;
  private btnToggleApiKeyMaskEl: HTMLButtonElement;
  private settingsBaseUrlEl: HTMLInputElement;
  private settingsModelEl: HTMLSelectElement;
  private settingsRetriesEl: HTMLSelectElement;
  private btnVerifyKeyEl: HTMLButtonElement;
  private settingsVerifyStatusEl: HTMLElement;
  private settingsCurrentKeyDisplayEl: HTMLElement;
  private settingsKeyBadgeEl: HTMLElement;
  private btnSaveSettingsEl: HTMLButtonElement;
  private btnCancelSettingsEl: HTMLButtonElement;
  private btnCloseSettingsEl: HTMLButtonElement;
  private btnSettingsEl: HTMLButtonElement;

  constructor() {
    this.dialogueEl         = document.getElementById('dialogue-stream') as HTMLElement;
    this.promptInputEl      = document.getElementById('prompt-input') as HTMLTextAreaElement;
    this.btnSendEl          = document.getElementById('btn-send') as HTMLButtonElement;
    this.autoRunToggleEl    = document.getElementById('auto-run-toggle') as HTMLInputElement;
    this.autoRepairToggleEl = document.getElementById('auto-repair-toggle') as HTMLInputElement;
    this.retriesSelectEl    = document.getElementById('retries-select') as HTMLSelectElement;
    this.themeToggleBtnEl   = document.getElementById('btn-theme-toggle') as HTMLButtonElement;
    this.themeSunIconEl     = document.getElementById('theme-sun-icon') as HTMLElement;
    this.themeMoonIconEl    = document.getElementById('theme-moon-icon') as HTMLElement;
    this.rawToggleBtnEl     = document.getElementById('btn-toggle-raw') as HTMLButtonElement;
    this.btnResetEl         = document.getElementById('btn-reset') as HTMLButtonElement;
    this.modelSelectEl      = document.getElementById('model-select') as HTMLSelectElement;
    this.statusBadgeEl      = document.getElementById('status-badge') as HTMLElement;

    this.langSelectEl         = document.getElementById('lang-select') as HTMLSelectElement;
    this.blockLangOverrideEl  = document.getElementById('block-lang-override') as HTMLSelectElement;

    this.codeLangBadgeEl   = document.getElementById('code-lang-badge') as HTMLElement;
    this.codeLineCountEl   = document.getElementById('code-line-count') as HTMLElement;
    this.codeContentEl     = document.getElementById('code-content') as HTMLElement;
    this.btnRunCodeEl      = document.getElementById('btn-run-code') as HTMLButtonElement;
    this.btnCopyCodeEl     = document.getElementById('btn-copy-code') as HTMLButtonElement;

    this.execStatusBadgeEl  = document.getElementById('exec-status-badge') as HTMLElement;
    this.execTimeBadgeEl    = document.getElementById('exec-time-badge') as HTMLElement;
    this.execCommandBadgeEl = document.getElementById('exec-command-badge') as HTMLElement;
    this.consoleOutputEl    = document.getElementById('console-output') as HTMLElement;
    this.btnClearConsoleEl  = document.getElementById('btn-clear-console') as HTMLButtonElement;

    this.rawModalEl         = document.getElementById('raw-modal') as HTMLElement;
    this.rawContentEl       = document.getElementById('raw-content') as HTMLElement;
    this.rawCannedWarningEl = document.getElementById('raw-canned-warning') as HTMLElement;
    this.rawQualityBadgeEl  = document.getElementById('raw-quality-badge') as HTMLElement;
    this.rawStatsBarEl      = document.getElementById('raw-stats-bar') as HTMLElement;
    this.rawCharCountEl     = document.getElementById('raw-char-count') as HTMLElement;
    this.rawHasCodeEl       = document.getElementById('raw-has-code') as HTMLElement;
    this.rawModelInfoEl     = document.getElementById('raw-model-info') as HTMLElement;
    this.btnCloseRawEl      = document.getElementById('btn-close-raw') as HTMLButtonElement;
    this.btnCopyRawEl       = document.getElementById('btn-copy-raw') as HTMLButtonElement;

    this.settingsModalEl            = document.getElementById('settings-modal') as HTMLElement;
    this.settingsApiKeyEl           = document.getElementById('settings-api-key') as HTMLInputElement;
    this.btnToggleApiKeyMaskEl      = document.getElementById('btn-toggle-api-key-mask') as HTMLButtonElement;
    this.settingsBaseUrlEl          = document.getElementById('settings-base-url') as HTMLInputElement;
    this.settingsModelEl            = document.getElementById('settings-model') as HTMLSelectElement;
    this.settingsRetriesEl          = document.getElementById('settings-retries') as HTMLSelectElement;
    this.btnVerifyKeyEl             = document.getElementById('btn-verify-key') as HTMLButtonElement;
    this.settingsVerifyStatusEl     = document.getElementById('settings-verify-status') as HTMLElement;
    this.settingsCurrentKeyDisplayEl= document.getElementById('settings-current-key-display') as HTMLElement;
    this.settingsKeyBadgeEl         = document.getElementById('settings-key-badge') as HTMLElement;
    this.btnSaveSettingsEl          = document.getElementById('btn-save-settings') as HTMLButtonElement;
    this.btnCancelSettingsEl        = document.getElementById('btn-cancel-settings') as HTMLButtonElement;
    this.btnCloseSettingsEl         = document.getElementById('btn-close-settings') as HTMLButtonElement;
    this.btnSettingsEl              = document.getElementById('btn-settings') as HTMLButtonElement;

    this.initEventListeners();
    this.initTheme();
  }

  private initEventListeners(): void {
    // Auto-expand textarea
    this.promptInputEl.addEventListener('input', () => {
      this.promptInputEl.style.height = 'auto';
      this.promptInputEl.style.height = `${Math.min(this.promptInputEl.scrollHeight, 200)}px`;
    });

    // Theme toggle button
    this.themeToggleBtnEl?.addEventListener('click', () => {
      this.toggleTheme();
    });

    // Clear console button
    this.btnClearConsoleEl.addEventListener('click', () => {
      this.clearConsole();
    });

    // Copy extracted code
    this.btnCopyCodeEl.addEventListener('click', () => {
      const code = this.codeContentEl.textContent || '';
      if (code) {
        navigator.clipboard.writeText(code);
        this.showToast('Code copied to clipboard!');
      }
    });

    // Copy raw response
    this.btnCopyRawEl.addEventListener('click', () => {
      const raw = this.rawContentEl.textContent || '';
      if (raw) {
        navigator.clipboard.writeText(raw);
        this.showToast('Raw API payload copied!');
      }
    });

    // Close raw modal
    this.btnCloseRawEl.addEventListener('click', () => {
      this.hideRawModal();
    });

    // Close raw modal on backdrop click
    this.rawModalEl.addEventListener('click', (e) => {
      if (e.target === this.rawModalEl) this.hideRawModal();
    });

    // Close settings modal
    this.btnCloseSettingsEl?.addEventListener('click', () => {
      this.hideSettingsModal();
    });
    this.btnCancelSettingsEl?.addEventListener('click', () => {
      this.hideSettingsModal();
    });
    this.settingsModalEl?.addEventListener('click', (e) => {
      if (e.target === this.settingsModalEl) this.hideSettingsModal();
    });

    // Toggle API key mask
    this.btnToggleApiKeyMaskEl?.addEventListener('click', () => {
      this.toggleApiKeyMask();
    });

    // Sync block-lang-override → header lang-select when user picks in workbench
    this.blockLangOverrideEl.addEventListener('change', () => {
      const val = this.blockLangOverrideEl.value;
      if (val !== 'auto') {
        this.langSelectEl.value = val;
      }
    });

    // Sync header lang-select → block-lang-override
    this.langSelectEl.addEventListener('change', () => {
      const val = this.langSelectEl.value;
      this.blockLangOverrideEl.value = val !== 'auto' ? val : 'auto';
      // Update badge if code is loaded
      const current = this.codeContentEl.textContent || '';
      if (current && !current.startsWith('# No code') && val !== 'auto') {
        this.codeLangBadgeEl.textContent = val.toUpperCase();
      }
    });

    // Delegate copy buttons inside rendered markdown
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (target && target.classList.contains('copy-code-btn')) {
        const encoded = target.getAttribute('data-code');
        if (encoded) {
          navigator.clipboard.writeText(decodeURIComponent(encoded));
          target.textContent = 'Copied!';
          setTimeout(() => { target.textContent = 'Copy'; }, 2000);
        }
      }
    });
  }

  // --- Theme Management ---

  public getTheme(): 'dark' | 'light' {
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  }

  public setTheme(theme: 'dark' | 'light'): void {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      this.themeSunIconEl?.classList.remove('hidden');
      this.themeMoonIconEl?.classList.add('hidden');
    } else {
      document.documentElement.classList.remove('dark');
      this.themeSunIconEl?.classList.add('hidden');
      this.themeMoonIconEl?.classList.remove('hidden');
    }
    try {
      localStorage.setItem('theme', theme);
    } catch {
      // localStorage may fail in some environments
    }
  }

  public toggleTheme(): void {
    const nextTheme = this.getTheme() === 'dark' ? 'light' : 'dark';
    this.setTheme(nextTheme);
    this.showToast(`Switched to ${nextTheme === 'dark' ? 'Dark' : 'Light'} theme`);
  }

  public initTheme(): void {
    let saved: string | null = null;
    try {
      saved = localStorage.getItem('theme');
    } catch {
      saved = null;
    }

    if (saved === 'light' || saved === 'dark') {
      this.setTheme(saved as 'dark' | 'light');
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      this.setTheme('light');
    } else {
      this.setTheme('dark');
    }
  }

  // --- Auto-Repair & Retries ---

  public isAutoRepairEnabled(): boolean {
    return this.autoRepairToggleEl ? this.autoRepairToggleEl.checked : false;
  }

  public getMaxRetries(): number {
    const val = this.retriesSelectEl ? parseInt(this.retriesSelectEl.value, 10) : 3;
    return isNaN(val) ? 3 : Math.max(1, Math.min(val, 10));
  }

  public appendRepairMessage(attempt: number, maxRetries: number, reason: string): { msgId: string; contentEl: HTMLElement } {
    const msgId = `msg-repair-${Date.now()}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const div = document.createElement('div');
    div.id = msgId;
    div.className = 'chat-turn repair-turn flex flex-col items-start my-4 animate-fadeIn';
    div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-amber-500 font-mono">
        <span class="flex items-center gap-1.5 font-bold">
          <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          Auto-Repair (Attempt ${attempt}/${maxRetries})
        </span>
        <span>•</span>
        <span>${timeStr}</span>
      </div>
      <div class="repair-bubble w-full max-w-3xl px-5 py-4 rounded-2xl bg-amber-950/40 dark:bg-amber-950/40 border border-amber-600/60 dark:border-amber-600/60 text-slate-800 dark:text-slate-200 text-sm md:text-base shadow-xl backdrop-blur-md">
        <div class="mb-2 text-xs font-mono text-amber-700 dark:text-amber-300 flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <span class="truncate">Diagnosing error: ${escapeHtml(reason)}</span>
        </div>
        <div class="markdown-body leading-relaxed">
          <span class="streaming-cursor inline-block w-2 h-4 bg-amber-500 dark:bg-amber-400 animate-pulse align-middle"></span>
        </div>
      </div>
    `;
    this.dialogueEl.appendChild(div);
    this.scrollToBottom();
    const contentEl = div.querySelector('.markdown-body') as HTMLElement;
    return { msgId, contentEl };
  }

  // --- Input & General Controls ---

  public getPrompt(): string {
    return this.promptInputEl.value.trim();
  }

  public clearPrompt(): void {
    this.promptInputEl.value = '';
    this.promptInputEl.style.height = 'auto';
  }

  public setInputEnabled(enabled: boolean): void {
    this.promptInputEl.disabled = !enabled;
    this.btnSendEl.disabled = !enabled;
    if (enabled) {
      this.btnSendEl.innerHTML = `
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/>
        </svg>
        <span>Send</span>
      `;
      this.promptInputEl.focus();
    } else {
      this.btnSendEl.innerHTML = `
        <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Processing...</span>
      `;
    }
  }

  public isAutoRunEnabled(): boolean {
    return this.autoRunToggleEl.checked;
  }

  public getSelectedModel(): string {
    return this.modelSelectEl.value;
  }

  public setSelectedModel(model: string): void {
    if (this.modelSelectEl) {
      this.modelSelectEl.value = model;
    }
  }

  public setStatus(text: string, isOnline: boolean): void {
    this.statusBadgeEl.innerHTML = `
      <span class="inline-block w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'} mr-1.5"></span>
      <span>${text}</span>
    `;
  }

  public appendUserMessage(prompt: string): string {
    const msgId = `msg-user-${Date.now()}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const div = document.createElement('div');
    div.id = msgId;
    div.className = 'chat-turn user-turn flex flex-col items-end my-4 animate-fadeIn';
    div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-slate-500 dark:text-slate-400 font-mono">
        <span>You</span>
        <span>•</span>
        <span>${timeStr}</span>
      </div>
      <div class="user-bubble max-w-2xl px-4 py-3 rounded-2xl bg-cyan-950/60 border border-cyan-700/60 text-cyan-100 text-sm md:text-base shadow-lg backdrop-blur-sm">
        ${escapeHtml(prompt).replace(/\n/g, '<br/>')}
      </div>
    `;
    this.dialogueEl.appendChild(div);
    this.scrollToBottom();
    return msgId;
  }

  public appendAssistantMessage(): { msgId: string; contentEl: HTMLElement } {
    const msgId = `msg-assistant-${Date.now()}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const div = document.createElement('div');
    div.id = msgId;
    div.className = 'chat-turn assistant-turn flex flex-col items-start my-4 animate-fadeIn';
    div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-cyan-600 dark:text-cyan-400 font-mono">
        <span class="flex items-center gap-1.5 font-bold">
          <span class="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 animate-ping"></span>
          JesseCoder
        </span>
        <span>•</span>
        <span>${timeStr}</span>
      </div>
      <div class="assistant-bubble w-full max-w-3xl px-5 py-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-slate-800 dark:text-slate-200 text-sm md:text-base shadow-xl backdrop-blur-md">
        <div class="markdown-body leading-relaxed">
          <span class="streaming-cursor inline-block w-2 h-4 bg-cyan-500 dark:bg-cyan-400 animate-pulse align-middle"></span>
        </div>
      </div>
    `;
    this.dialogueEl.appendChild(div);
    this.scrollToBottom();
    const contentEl = div.querySelector('.markdown-body') as HTMLElement;
    return { msgId, contentEl };
  }

  public updateAssistantStream(contentEl: HTMLElement, text: string): void {
    contentEl.innerHTML = renderMarkdown(text) + '<span class="streaming-cursor inline-block w-2 h-4 bg-cyan-500 dark:bg-cyan-400 animate-pulse ml-1 align-middle"></span>';
    this.scrollToBottom();
  }

  public finalizeAssistantMessage(contentEl: HTMLElement, text: string, execResult?: ExecutionResult | null): void {
    let html = renderMarkdown(text);
    if (execResult) {
      html += this.createInlineExecutionCard(execResult);
    }
    contentEl.innerHTML = html;
    this.scrollToBottom();
  }

  public createInlineExecutionCard(res: ExecutionResult): string {
    const statusBg = res.success ? 'bg-emerald-950/70 border-emerald-700/60' : 'bg-rose-950/70 border-rose-700/60';
    const statusText = res.success ? 'text-emerald-400' : 'text-rose-400';
    const badge = res.success ? '✔ EXECUTION SUCCESS' : '✖ EXECUTION FAILED';

    return `
      <div class="inline-exec-card my-4 p-3 rounded-lg border ${statusBg} text-xs font-mono shadow-inner">
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <span class="font-bold ${statusText}">${badge} (Exit ${res.exit_code})</span>
          <span class="text-slate-400">${res.execution_time_ms} ms</span>
        </div>
        ${res.stdout ? `<div class="mt-2 text-emerald-200 font-mono whitespace-pre-wrap">${escapeHtml(res.stdout)}</div>` : ''}
        ${res.stderr ? `<div class="mt-2 text-rose-300 font-mono whitespace-pre-wrap">${escapeHtml(res.stderr)}</div>` : ''}
      </div>
    `;
  }

  public displayExtractedCode(codeBlock: ExtractedCode | null): void {
    if (!codeBlock || !codeBlock.code.trim()) {
      this.codeLangBadgeEl.textContent = 'NONE';
      this.codeLineCountEl.textContent = '0 lines';
      this.codeContentEl.textContent = '# No code extracted yet.\n# Send a coding prompt to generate code here.';
      this.btnRunCodeEl.disabled = true;
      this.btnCopyCodeEl.disabled = true;
      return;
    }

    const lines   = codeBlock.code.trim().split('\n').length;
    const detectedLang = codeBlock.language || 'python';

    // Only update badge if user hasn't manually overridden
    const overrideLang = this.langSelectEl.value;
    const effectiveLang = (overrideLang && overrideLang !== 'auto') ? overrideLang : detectedLang;

    this.codeLangBadgeEl.textContent = effectiveLang.toUpperCase();
    this.codeLineCountEl.textContent = `${lines} line${lines === 1 ? '' : 's'}`;
    this.codeContentEl.textContent   = codeBlock.code.trim();
    this.btnRunCodeEl.disabled  = false;
    this.btnCopyCodeEl.disabled = false;

    // Sync block override dropdown to detected lang if header is 'auto'
    if (overrideLang === 'auto') {
      const opt = this.blockLangOverrideEl.querySelector(`option[value="${detectedLang}"]`);
      if (opt) this.blockLangOverrideEl.value = detectedLang;
    }
  }

  /** Returns code + resolved language, honoring user's language picker override. */
  public getCurrentCode(): { code: string; language: string } | null {
    const code = this.codeContentEl.textContent || '';
    if (!code || code.startsWith('# No code')) return null;

    // Priority: header lang-select > block-override > badge text
    const headerLang = this.langSelectEl.value;
    const blockLang  = this.blockLangOverrideEl.value;
    let language = 'python';

    if (headerLang && headerLang !== 'auto') {
      language = headerLang;
    } else if (blockLang && blockLang !== 'auto') {
      language = blockLang;
    } else {
      language = this.codeLangBadgeEl.textContent?.toLowerCase().replace(/\s/g, '') || 'python';
    }

    return { code, language };
  }

  public setExecutingState(isExecuting: boolean): void {
    if (isExecuting) {
      this.btnRunCodeEl.disabled = true;
      this.btnRunCodeEl.innerHTML = `
        <svg class="w-3 h-3 animate-spin mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Running…</span>
      `;
      this.execStatusBadgeEl.textContent = 'RUNNING ⏳';
      this.execStatusBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800';
    } else {
      this.btnRunCodeEl.disabled = false;
      this.btnRunCodeEl.innerHTML = `
        <svg class="w-3 h-3 text-slate-950" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
        </svg>
        <span>Run</span>
      `;
    }
  }

  public renderExecutionResult(res: ExecutionResult): void {
    if (res.success) {
      this.execStatusBadgeEl.textContent = `SUCCESS (0)`;
      this.execStatusBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-700/80';
    } else {
      this.execStatusBadgeEl.textContent = `FAILED (${res.exit_code})`;
      this.execStatusBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-700/80';
    }

    this.execTimeBadgeEl.textContent = `${res.execution_time_ms} ms`;
    this.execTimeBadgeEl.classList.remove('hidden');

    if (res.command && res.command.length > 0) {
      this.execCommandBadgeEl.textContent = res.command.join(' ');
      this.execCommandBadgeEl.classList.remove('hidden');
    }

    let output = '';
    if (res.stdout) {
      output += `<span class="text-emerald-300">${escapeHtml(res.stdout)}</span>`;
    }
    if (res.stderr) {
      if (output) output += '\n';
      output += `<span class="text-rose-400">${escapeHtml(res.stderr)}</span>`;
    }
    if (!res.stdout && !res.stderr) {
      output = '<span class="text-slate-500 italic">[Process completed with no console output]</span>';
    }

    this.consoleOutputEl.innerHTML = output;
    this.consoleOutputEl.scrollTop = this.consoleOutputEl.scrollHeight;
  }

  public clearConsole(): void {
    this.consoleOutputEl.innerHTML = '<span class="text-slate-400 dark:text-slate-600 font-mono text-xs italic">Console ready. Click [Run] or enable Auto-Run.</span>';
    this.execStatusBadgeEl.textContent = 'IDLE';
    this.execStatusBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700';
    this.execTimeBadgeEl.classList.add('hidden');
    this.execCommandBadgeEl.classList.add('hidden');
  }

  /**
   * Show RAW API modal with canned-response banner when needed.
   * Accepts either a plain string (legacy) or a RawPayload object.
   */
  public showRawModal(payload: RawPayload | string): void {
    const isObj = typeof payload === 'object' && payload !== null;
    const rawText   = isObj ? (payload as RawPayload).raw   : (payload as string);
    const wasCanned = isObj ? !!(payload as RawPayload).was_canned : false;

    // Content
    this.rawContentEl.textContent = rawText || 'No raw response recorded yet. Send a prompt first.';

    // Canned warning banner
    if (wasCanned) {
      this.rawCannedWarningEl.classList.remove('hidden');
      this.rawQualityBadgeEl.textContent = 'CANNED / BENCHMARK';
      this.rawQualityBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono border bg-amber-950 border-amber-700 text-amber-300';
      this.rawQualityBadgeEl.classList.remove('hidden');
    } else {
      this.rawCannedWarningEl.classList.add('hidden');
      if (rawText && rawText.length > 10) {
        this.rawQualityBadgeEl.textContent = 'LIVE RESPONSE';
        this.rawQualityBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono border bg-emerald-950 border-emerald-700 text-emerald-300';
        this.rawQualityBadgeEl.classList.remove('hidden');
      } else {
        this.rawQualityBadgeEl.classList.add('hidden');
      }
    }

    // Stats bar
    if (rawText) {
      const charCount = rawText.length;
      const hasCode   = /```/.test(rawText) || /def |class |function |import /.test(rawText);
      this.rawCharCountEl.textContent  = `${charCount.toLocaleString()} chars`;
      this.rawHasCodeEl.textContent    = hasCode ? '⟨/⟩ Contains code blocks' : '— No code blocks';
      this.rawHasCodeEl.className      = hasCode ? 'text-cyan-600' : 'text-slate-600';
      this.rawModelInfoEl.textContent  = 'jesse.my/api/v1';
      this.rawStatsBarEl.classList.remove('hidden');
    } else {
      this.rawStatsBarEl.classList.add('hidden');
    }

    this.rawModalEl.classList.remove('hidden');
  }

  public hideRawModal(): void {
    this.rawModalEl.classList.add('hidden');
  }

  public clearDialogue(): void {
    this.dialogueEl.innerHTML = `
      <div id="welcome-message" class="text-center py-10 px-4">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800/80 mb-4 shadow-xl">
          <span class="text-3xl text-cyan-600 dark:text-cyan-400 font-mono">⚡</span>
        </div>
        <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-wide">JesseCoder Intelligence Console</h2>
        <p class="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mt-2">
          Real-time coding agent with isolated subprocess execution, self-healing retries, and live Jesse API streaming.
        </p>
      </div>
    `;
    this.clearConsole();
    this.displayExtractedCode(null);
  }

  public showToast(message: string, isError: boolean = false): void {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 px-4 py-2.5 rounded-xl border text-xs font-mono shadow-2xl z-50 transition-all duration-300 transform translate-y-2 opacity-0 ${
      isError ? 'bg-rose-950 border-rose-700 text-rose-200' : 'bg-slate-900 border-cyan-600/80 text-cyan-200'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  private scrollToBottom(): void {
    this.dialogueEl.scrollTop = this.dialogueEl.scrollHeight;
  }

  // --------------------------------------------------------------------------
  // Feedback buttons — injected into assistant message bubbles after finalize
  // --------------------------------------------------------------------------

  /**
   * Adds 👍/👎 feedback buttons to a finalized assistant message bubble.
   * Returns the message element ID so the caller can track which message is rated.
   */
  public addFeedbackButtons(msgEl: HTMLElement, onThumbsUp: () => void, onThumbsDown: () => void): void {
    // Avoid duplicate buttons
    if (msgEl.querySelector('.feedback-actions')) return;

    const actionsBar = document.createElement('div');
    actionsBar.className = 'feedback-actions flex items-center gap-2 mt-2 ml-1';
    actionsBar.innerHTML = `
      <span class="text-[10px] font-mono text-slate-400 dark:text-slate-600">Was this helpful?</span>
      <button class="btn-thumbs-up px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/60 hover:bg-emerald-200 dark:hover:bg-emerald-900 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-400 text-[11px] font-mono transition" title="Good answer — teach jesse-prod">👍</button>
      <button class="btn-thumbs-down px-2 py-0.5 rounded bg-rose-100 dark:bg-rose-950/60 hover:bg-rose-200 dark:hover:bg-rose-900 border border-rose-300 dark:border-rose-700/60 text-rose-700 dark:text-rose-400 text-[11px] font-mono transition" title="Wrong answer — correct jesse-prod">👎</button>
    `;

    const thumbsUp = actionsBar.querySelector('.btn-thumbs-up') as HTMLButtonElement;
    const thumbsDown = actionsBar.querySelector('.btn-thumbs-down') as HTMLButtonElement;

    thumbsUp.addEventListener('click', () => {
      thumbsUp.textContent = '✓ Thanks!';
      thumbsUp.disabled = true;
      thumbsDown.disabled = true;
      onThumbsUp();
    });

    thumbsDown.addEventListener('click', () => {
      thumbsDown.textContent = '→ Correcting...';
      thumbsDown.disabled = true;
      thumbsUp.disabled = true;
      onThumbsDown();
    });

    // Append after the bubble div
    const bubble = msgEl.closest('.assistant-turn') as HTMLElement;
    if (bubble) {
      bubble.appendChild(actionsBar);
    }
  }

  // --------------------------------------------------------------------------
  // Feedback Correction Modal
  // --------------------------------------------------------------------------

  public showFeedbackModal(onSubmit: (correction: string) => void, onCancel: () => void): void {
    const modal = document.getElementById('feedback-modal') as HTMLElement;
    const input = document.getElementById('feedback-correction-input') as HTMLTextAreaElement;
    const btnSubmit = document.getElementById('btn-feedback-submit') as HTMLButtonElement;
    const btnCancel = document.getElementById('btn-feedback-cancel') as HTMLButtonElement;
    const btnClose = document.getElementById('btn-close-feedback') as HTMLButtonElement;

    input.value = '';
    modal.classList.remove('hidden');
    input.focus();

    const doSubmit = () => {
      const correction = input.value.trim();
      modal.classList.add('hidden');
      cleanup();
      onSubmit(correction);
    };

    const doCancel = () => {
      modal.classList.add('hidden');
      cleanup();
      onCancel();
    };

    const cleanup = () => {
      btnSubmit.removeEventListener('click', doSubmit);
      btnCancel.removeEventListener('click', doCancel);
      btnClose.removeEventListener('click', doCancel);
    };

    btnSubmit.addEventListener('click', doSubmit);
    btnCancel.addEventListener('click', doCancel);
    btnClose.addEventListener('click', doCancel);
  }

  // --------------------------------------------------------------------------
  // Memory Panel
  // --------------------------------------------------------------------------

  public showMemoryPanel(): void {
    const modal = document.getElementById('memory-modal') as HTMLElement;
    modal.classList.remove('hidden');
  }

  public hideMemoryPanel(): void {
    const modal = document.getElementById('memory-modal') as HTMLElement;
    modal.classList.add('hidden');
  }

  public renderMemoryContent(data: unknown, isError: boolean = false): void {
    const el = document.getElementById('memory-content') as HTMLElement;
    if (isError) {
      el.innerHTML = `<span class="text-rose-400">⚠️ ${escapeHtml(String(data))}</span>`;
      return;
    }
    if (!data || (Array.isArray(data) && data.length === 0)) {
      el.innerHTML = '<span class="text-slate-400 italic">No memory stored yet.</span>';
      return;
    }
    // Pretty-print JSON, or render as a list if it's an array
    if (Array.isArray(data)) {
      const items = (data as Record<string, unknown>[]).map((fact, i) => {
        const text = fact.value ?? fact.fact ?? fact.content ?? JSON.stringify(fact);
        return `<div class="flex gap-2 py-1 border-b border-slate-100 dark:border-slate-800">
          <span class="text-violet-400 shrink-0">${i + 1}.</span>
          <span class="text-slate-700 dark:text-slate-300">${escapeHtml(String(text))}</span>
        </div>`;
      }).join('');
      el.innerHTML = items || '<span class="text-slate-400 italic">No memory stored yet.</span>';
    } else {
      el.textContent = JSON.stringify(data, null, 2);
    }
  }

  // --------------------------------------------------------------------------
  // Documents Panel
  // --------------------------------------------------------------------------

  public showDocsPanel(activeTab: string = 'store'): void {
    const modal = document.getElementById('docs-modal') as HTMLElement;
    modal.classList.remove('hidden');
    this.switchDocsTab(activeTab);
  }

  public hideDocsPanel(): void {
    const modal = document.getElementById('docs-modal') as HTMLElement;
    modal.classList.add('hidden');
  }

  public switchDocsTab(tabName: string): void {
    // Update tab button styles
    document.querySelectorAll('.docs-tab').forEach((btn) => {
      const b = btn as HTMLButtonElement;
      const isActive = b.getAttribute('data-docs-tab') === tabName;
      b.className = isActive
        ? 'docs-tab px-4 py-2.5 text-xs font-mono font-bold border-b-2 border-emerald-500 text-emerald-600 dark:text-emerald-400 transition'
        : 'docs-tab px-4 py-2.5 text-xs font-mono font-bold border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition';
    });
    // Show/hide panels
    document.querySelectorAll('.docs-tab-panel').forEach((panel) => {
      (panel as HTMLElement).classList.add('hidden');
    });
    const active = document.getElementById(`docs-tab-${tabName}`);
    if (active) {
      active.classList.remove('hidden');
      active.classList.add('flex-1', 'overflow-auto');
    }
  }

  public renderDocsList(data: unknown, isError: boolean = false): void {
    const el = document.getElementById('docs-list-content') as HTMLElement;
    if (isError) {
      el.innerHTML = `<span class="text-rose-400">⚠️ ${escapeHtml(String(data))}</span>`;
      return;
    }
    const docs = Array.isArray(data) ? data : ((data as Record<string, unknown>)?.documents ?? (data as Record<string, unknown>)?.data ?? []);
    if (!Array.isArray(docs) || docs.length === 0) {
      el.innerHTML = '<span class="text-slate-400 italic">No documents stored yet.</span>';
      return;
    }
    el.innerHTML = (docs as Record<string, unknown>[]).map((doc) => `
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
        <div class="font-bold text-emerald-600 dark:text-emerald-400">${escapeHtml(String(doc.title ?? '(untitled)'))}</div>
        ${doc.id ? `<div class="text-slate-400 text-[10px] mt-0.5">ID: ${escapeHtml(String(doc.id))}</div>` : ''}
        ${doc.created_at ? `<div class="text-slate-400 text-[10px]">${escapeHtml(String(doc.created_at))}</div>` : ''}
      </div>
    `).join('');
  }

  public renderDocSearchResults(data: unknown, isError: boolean = false): void {
    const el = document.getElementById('doc-search-results') as HTMLElement;
    if (isError) {
      el.innerHTML = `<span class="text-rose-400">⚠️ ${escapeHtml(String(data))}</span>`;
      return;
    }
    const results = Array.isArray(data) ? data : ((data as Record<string, unknown>)?.results ?? (data as Record<string, unknown>)?.data ?? []);
    if (!Array.isArray(results) || results.length === 0) {
      el.innerHTML = '<span class="text-slate-400 italic">No matching documents found.</span>';
      return;
    }
    el.innerHTML = (results as Record<string, unknown>[]).map((r, i) => `
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-emerald-900/40">
        <div class="flex items-center justify-between mb-1">
          <span class="font-bold text-emerald-600 dark:text-emerald-400">${i + 1}. ${escapeHtml(String(r.title ?? '(untitled)'))}</span>
          ${r.score !== undefined ? `<span class="text-[10px] text-slate-400 font-mono">score: ${Number(r.score).toFixed(3)}</span>` : ''}
        </div>
        ${r.content ? `<p class="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed line-clamp-3">${escapeHtml(String(r.content).slice(0, 300))}${String(r.content).length > 300 ? '...' : ''}</p>` : ''}
      </div>
    `).join('');
  }

  public showDocStoreResult(message: string, isError: boolean = false): void {
    const el = document.getElementById('doc-store-result') as HTMLElement;
    el.classList.remove('hidden');
    el.className = `mt-2 p-3 rounded-lg border text-xs font-mono ${
      isError
        ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-700 text-rose-700 dark:text-rose-300'
        : 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300'
    }`;
    el.textContent = message;
    setTimeout(() => el.classList.add('hidden'), 4000);
  }

  // --------------------------------------------------------------------------
  // Settings & Configuration Modal
  // --------------------------------------------------------------------------

  public showSettingsModal(): void {
    this.settingsModalEl?.classList.remove('hidden');
  }

  public hideSettingsModal(): void {
    this.settingsModalEl?.classList.add('hidden');
  }

  public populateSettings(settings: ServerSettings, currentRetries?: number): void {
    if (this.settingsBaseUrlEl) {
      this.settingsBaseUrlEl.value = settings.base_url || 'https://jesse.my/api/v1';
    }
    if (this.settingsModelEl && settings.model) {
      this.settingsModelEl.value = settings.model;
    }
    if (this.settingsRetriesEl && currentRetries !== undefined) {
      this.settingsRetriesEl.value = String(currentRetries);
    }
    if (this.settingsApiKeyEl) {
      this.settingsApiKeyEl.value = '';
      this.settingsApiKeyEl.type = 'password';
    }
    if (this.btnToggleApiKeyMaskEl) {
      this.btnToggleApiKeyMaskEl.textContent = '👁️ Show';
    }
    if (this.settingsCurrentKeyDisplayEl) {
      this.settingsCurrentKeyDisplayEl.textContent = settings.has_api_key
        ? (settings.api_key_masked || 'jesse_live_••••')
        : 'No API key configured';
    }
    if (this.settingsKeyBadgeEl) {
      if (settings.has_api_key) {
        this.settingsKeyBadgeEl.textContent = 'Configured';
        this.settingsKeyBadgeEl.className = 'px-1.5 py-0.5 rounded text-[10px] bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400 font-mono font-medium';
      } else {
        this.settingsKeyBadgeEl.textContent = 'Unset';
        this.settingsKeyBadgeEl.className = 'px-1.5 py-0.5 rounded text-[10px] bg-rose-100 dark:bg-rose-950/80 text-rose-700 dark:text-rose-400 font-mono font-medium';
      }
    }
    this.setVerifyStatus('', 'idle');
  }

  public toggleApiKeyMask(): void {
    if (!this.settingsApiKeyEl || !this.btnToggleApiKeyMaskEl) return;
    const isMasked = this.settingsApiKeyEl.type === 'password';
    this.settingsApiKeyEl.type = isMasked ? 'text' : 'password';
    this.btnToggleApiKeyMaskEl.textContent = isMasked ? '🙈 Hide' : '👁️ Show';
  }

  public getSettingsFormValues(): { apiKey: string; baseUrl: string; model: string; retries: number } {
    const apiKey = this.settingsApiKeyEl?.value.trim() || '';
    const baseUrl = this.settingsBaseUrlEl?.value.trim() || '';
    const model = this.settingsModelEl?.value || 'jesse-prod';
    const retries = parseInt(this.settingsRetriesEl?.value || '3', 10) || 3;
    return { apiKey, baseUrl, model, retries };
  }

  public setVerifyStatus(message: string, state: 'loading' | 'success' | 'error' | 'idle'): void {
    if (!this.settingsVerifyStatusEl) return;
    this.settingsVerifyStatusEl.textContent = message;
    if (state === 'loading') {
      this.settingsVerifyStatusEl.className = 'text-[10px] font-mono text-amber-500 animate-pulse';
    } else if (state === 'success') {
      this.settingsVerifyStatusEl.className = 'text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold';
    } else if (state === 'error') {
      this.settingsVerifyStatusEl.className = 'text-[10px] font-mono text-rose-600 dark:text-rose-400 font-bold';
    } else {
      this.settingsVerifyStatusEl.className = 'text-[10px] font-mono text-slate-500';
    }
  }

  public setRetries(retries: number): void {
    const val = String(retries);
    if (this.retriesSelectEl) {
      this.retriesSelectEl.value = val;
    }
    if (this.settingsRetriesEl) {
      this.settingsRetriesEl.value = val;
    }
  }
}
