/**
 * UI controller and DOM manipulation for JesseCoder WebApp.
 */

import { ChatMessage, ExecutionResult, ExtractedCode } from './types';
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

  constructor() {
    this.dialogueEl        = document.getElementById('dialogue-stream') as HTMLElement;
    this.promptInputEl     = document.getElementById('prompt-input') as HTMLTextAreaElement;
    this.btnSendEl         = document.getElementById('btn-send') as HTMLButtonElement;
    this.autoRunToggleEl   = document.getElementById('auto-run-toggle') as HTMLInputElement;
    this.rawToggleBtnEl    = document.getElementById('btn-toggle-raw') as HTMLButtonElement;
    this.btnResetEl        = document.getElementById('btn-reset') as HTMLButtonElement;
    this.modelSelectEl     = document.getElementById('model-select') as HTMLSelectElement;
    this.statusBadgeEl     = document.getElementById('status-badge') as HTMLElement;

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

    this.initEventListeners();
  }

  private initEventListeners(): void {
    // Auto-expand textarea
    this.promptInputEl.addEventListener('input', () => {
      this.promptInputEl.style.height = 'auto';
      this.promptInputEl.style.height = `${Math.min(this.promptInputEl.scrollHeight, 200)}px`;
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
        <span>Streaming...</span>
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
      <div class="flex items-center gap-2 mb-1 text-xs text-slate-400 font-mono">
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
      <div class="flex items-center gap-2 mb-1 text-xs text-cyan-400 font-mono">
        <span class="flex items-center gap-1.5 font-bold">
          <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
          JesseCoder
        </span>
        <span>•</span>
        <span>${timeStr}</span>
      </div>
      <div class="assistant-bubble w-full max-w-3xl px-5 py-4 rounded-2xl bg-slate-900/90 border border-slate-800 text-slate-200 text-sm md:text-base shadow-xl backdrop-blur-md">
        <div class="markdown-body leading-relaxed">
          <span class="streaming-cursor inline-block w-2 h-4 bg-cyan-400 animate-pulse align-middle"></span>
        </div>
      </div>
    `;
    this.dialogueEl.appendChild(div);
    this.scrollToBottom();
    const contentEl = div.querySelector('.markdown-body') as HTMLElement;
    return { msgId, contentEl };
  }

  public updateAssistantStream(contentEl: HTMLElement, text: string): void {
    contentEl.innerHTML = renderMarkdown(text) + '<span class="streaming-cursor inline-block w-2 h-4 bg-cyan-400 animate-pulse ml-1 align-middle"></span>';
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
    this.consoleOutputEl.innerHTML = '<span class="text-slate-600 font-mono text-xs italic">Console ready. Click [Run] or enable Auto-Run.</span>';
    this.execStatusBadgeEl.textContent = 'IDLE';
    this.execStatusBadgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700';
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
      this.rawModelInfoEl.textContent  = 'jesse.solidsf.com/api/v1';
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
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-950/60 border border-cyan-800/80 mb-4 shadow-xl">
          <span class="text-3xl text-cyan-400 font-mono">⚡</span>
        </div>
        <h2 class="text-xl font-bold text-slate-100 tracking-wide">JesseCoder Intelligence Console</h2>
        <p class="text-sm text-slate-400 max-w-md mx-auto mt-2">
          Real-time coding agent with isolated subprocess execution and live Jesse API streaming.
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
}
