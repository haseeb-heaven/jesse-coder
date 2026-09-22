"use strict";
(() => {
  // src/markdown.ts
  function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
  function renderMarkdown(markdown) {
    if (!markdown)
      return "";
    const codeBlocks = [];
    let processed = markdown.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_match, lang, code) => {
      const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
      const safeLang = escapeHtml(lang || "text");
      const safeCode = escapeHtml(code.trim());
      const blockHtml = `
      <div class="code-block-wrapper my-3 rounded-lg border border-slate-700/80 bg-slate-950/80 overflow-hidden shadow-md">
        <div class="code-header flex items-center justify-between px-3 py-1.5 bg-slate-900 border-b border-slate-800 text-xs font-mono text-cyan-400">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-cyan-400 inline-block animate-pulse"></span>
            ${safeLang}
          </span>
          <button class="copy-code-btn px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 transition text-[11px]" data-code="${encodeURIComponent(code.trim())}">
            Copy
          </button>
        </div>
        <pre class="p-3 text-xs md:text-sm font-mono text-slate-200 overflow-x-auto leading-relaxed"><code>${safeCode}</code></pre>
      </div>
    `;
      codeBlocks.push(blockHtml);
      return placeholder;
    });
    processed = processed.replace(/^### (.*$)/gim, '<h3 class="text-base font-bold text-cyan-300 mt-4 mb-2 tracking-wide">$1</h3>').replace(/^## (.*$)/gim, '<h2 class="text-lg font-bold text-cyan-200 mt-5 mb-2.5 tracking-wide">$1</h2>').replace(/^# (.*$)/gim, '<h1 class="text-xl font-extrabold text-cyan-100 mt-6 mb-3 tracking-wide border-b border-slate-800 pb-1">$1</h1>');
    processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-200 font-semibold">$1</strong>').replace(/\*(.*?)\*/g, '<em class="text-slate-300 italic">$1</em>');
    processed = processed.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-800/80 text-cyan-300 font-mono text-xs border border-slate-700/50">$1</code>');
    processed = processed.replace(/^---$/gim, '<hr class="my-4 border-slate-800" />');
    processed = processed.replace(/^\s*[-*]\s+(.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-1">$1</li>');
    processed = processed.replace(/\n\n+/g, "<br/><br/>");
    codeBlocks.forEach((block, idx) => {
      processed = processed.replace(`__CODE_BLOCK_${idx}__`, block);
    });
    return processed;
  }

  // src/ui.ts
  var UIController = class {
    constructor() {
      this.dialogueEl = document.getElementById("dialogue-stream");
      this.promptInputEl = document.getElementById("prompt-input");
      this.btnSendEl = document.getElementById("btn-send");
      this.autoRunToggleEl = document.getElementById("auto-run-toggle");
      this.autoRepairToggleEl = document.getElementById("auto-repair-toggle");
      this.retriesSelectEl = document.getElementById("retries-select");
      this.themeToggleBtnEl = document.getElementById("btn-theme-toggle");
      this.themeSunIconEl = document.getElementById("theme-sun-icon");
      this.themeMoonIconEl = document.getElementById("theme-moon-icon");
      this.rawToggleBtnEl = document.getElementById("btn-toggle-raw");
      this.btnResetEl = document.getElementById("btn-reset");
      this.modelSelectEl = document.getElementById("model-select");
      this.statusBadgeEl = document.getElementById("status-badge");
      this.langSelectEl = document.getElementById("lang-select");
      this.blockLangOverrideEl = document.getElementById("block-lang-override");
      this.codeLangBadgeEl = document.getElementById("code-lang-badge");
      this.codeLineCountEl = document.getElementById("code-line-count");
      this.codeContentEl = document.getElementById("code-content");
      this.btnRunCodeEl = document.getElementById("btn-run-code");
      this.btnCopyCodeEl = document.getElementById("btn-copy-code");
      this.execStatusBadgeEl = document.getElementById("exec-status-badge");
      this.execTimeBadgeEl = document.getElementById("exec-time-badge");
      this.execCommandBadgeEl = document.getElementById("exec-command-badge");
      this.consoleOutputEl = document.getElementById("console-output");
      this.btnClearConsoleEl = document.getElementById("btn-clear-console");
      this.rawModalEl = document.getElementById("raw-modal");
      this.rawContentEl = document.getElementById("raw-content");
      this.rawCannedWarningEl = document.getElementById("raw-canned-warning");
      this.rawQualityBadgeEl = document.getElementById("raw-quality-badge");
      this.rawStatsBarEl = document.getElementById("raw-stats-bar");
      this.rawCharCountEl = document.getElementById("raw-char-count");
      this.rawHasCodeEl = document.getElementById("raw-has-code");
      this.rawModelInfoEl = document.getElementById("raw-model-info");
      this.btnCloseRawEl = document.getElementById("btn-close-raw");
      this.btnCopyRawEl = document.getElementById("btn-copy-raw");
      this.initEventListeners();
      this.initTheme();
    }
    initEventListeners() {
      this.promptInputEl.addEventListener("input", () => {
        this.promptInputEl.style.height = "auto";
        this.promptInputEl.style.height = `${Math.min(this.promptInputEl.scrollHeight, 200)}px`;
      });
      this.themeToggleBtnEl?.addEventListener("click", () => {
        this.toggleTheme();
      });
      this.btnClearConsoleEl.addEventListener("click", () => {
        this.clearConsole();
      });
      this.btnCopyCodeEl.addEventListener("click", () => {
        const code = this.codeContentEl.textContent || "";
        if (code) {
          navigator.clipboard.writeText(code);
          this.showToast("Code copied to clipboard!");
        }
      });
      this.btnCopyRawEl.addEventListener("click", () => {
        const raw = this.rawContentEl.textContent || "";
        if (raw) {
          navigator.clipboard.writeText(raw);
          this.showToast("Raw API payload copied!");
        }
      });
      this.btnCloseRawEl.addEventListener("click", () => {
        this.hideRawModal();
      });
      this.rawModalEl.addEventListener("click", (e) => {
        if (e.target === this.rawModalEl)
          this.hideRawModal();
      });
      this.blockLangOverrideEl.addEventListener("change", () => {
        const val = this.blockLangOverrideEl.value;
        if (val !== "auto") {
          this.langSelectEl.value = val;
        }
      });
      this.langSelectEl.addEventListener("change", () => {
        const val = this.langSelectEl.value;
        this.blockLangOverrideEl.value = val !== "auto" ? val : "auto";
        const current = this.codeContentEl.textContent || "";
        if (current && !current.startsWith("# No code") && val !== "auto") {
          this.codeLangBadgeEl.textContent = val.toUpperCase();
        }
      });
      document.addEventListener("click", (e) => {
        const target = e.target;
        if (target && target.classList.contains("copy-code-btn")) {
          const encoded = target.getAttribute("data-code");
          if (encoded) {
            navigator.clipboard.writeText(decodeURIComponent(encoded));
            target.textContent = "Copied!";
            setTimeout(() => {
              target.textContent = "Copy";
            }, 2e3);
          }
        }
      });
    }
    getTheme() {
      return document.documentElement.classList.contains("dark") ? "dark" : "light";
    }
    setTheme(theme) {
      if (theme === "dark") {
        document.documentElement.classList.add("dark");
        this.themeSunIconEl?.classList.remove("hidden");
        this.themeMoonIconEl?.classList.add("hidden");
      } else {
        document.documentElement.classList.remove("dark");
        this.themeSunIconEl?.classList.add("hidden");
        this.themeMoonIconEl?.classList.remove("hidden");
      }
      try {
        localStorage.setItem("theme", theme);
      } catch {
      }
    }
    toggleTheme() {
      const nextTheme = this.getTheme() === "dark" ? "light" : "dark";
      this.setTheme(nextTheme);
      this.showToast(`Switched to ${nextTheme === "dark" ? "Dark" : "Light"} theme`);
    }
    initTheme() {
      let saved = null;
      try {
        saved = localStorage.getItem("theme");
      } catch {
        saved = null;
      }
      if (saved === "light" || saved === "dark") {
        this.setTheme(saved);
      } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
        this.setTheme("light");
      } else {
        this.setTheme("dark");
      }
    }
    isAutoRepairEnabled() {
      return this.autoRepairToggleEl ? this.autoRepairToggleEl.checked : false;
    }
    getMaxRetries() {
      const val = this.retriesSelectEl ? parseInt(this.retriesSelectEl.value, 10) : 3;
      return isNaN(val) ? 3 : Math.max(1, Math.min(val, 10));
    }
    appendRepairMessage(attempt, maxRetries, reason) {
      const msgId = `msg-repair-${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const div = document.createElement("div");
      div.id = msgId;
      div.className = "chat-turn repair-turn flex flex-col items-start my-4 animate-fadeIn";
      div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-amber-500 font-mono">
        <span class="flex items-center gap-1.5 font-bold">
          <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          Auto-Repair (Attempt ${attempt}/${maxRetries})
        </span>
        <span>\u2022</span>
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
      const contentEl = div.querySelector(".markdown-body");
      return { msgId, contentEl };
    }
    getPrompt() {
      return this.promptInputEl.value.trim();
    }
    clearPrompt() {
      this.promptInputEl.value = "";
      this.promptInputEl.style.height = "auto";
    }
    setInputEnabled(enabled) {
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
    isAutoRunEnabled() {
      return this.autoRunToggleEl.checked;
    }
    getSelectedModel() {
      return this.modelSelectEl.value;
    }
    setSelectedModel(model) {
      if (this.modelSelectEl) {
        this.modelSelectEl.value = model;
      }
    }
    setStatus(text, isOnline) {
      this.statusBadgeEl.innerHTML = `
      <span class="inline-block w-2 h-2 rounded-full ${isOnline ? "bg-emerald-400 animate-pulse" : "bg-rose-500"} mr-1.5"></span>
      <span>${text}</span>
    `;
    }
    appendUserMessage(prompt) {
      const msgId = `msg-user-${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const div = document.createElement("div");
      div.id = msgId;
      div.className = "chat-turn user-turn flex flex-col items-end my-4 animate-fadeIn";
      div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-slate-500 dark:text-slate-400 font-mono">
        <span>You</span>
        <span>\u2022</span>
        <span>${timeStr}</span>
      </div>
      <div class="user-bubble max-w-2xl px-4 py-3 rounded-2xl bg-cyan-950/60 border border-cyan-700/60 text-cyan-100 text-sm md:text-base shadow-lg backdrop-blur-sm">
        ${escapeHtml(prompt).replace(/\n/g, "<br/>")}
      </div>
    `;
      this.dialogueEl.appendChild(div);
      this.scrollToBottom();
      return msgId;
    }
    appendAssistantMessage() {
      const msgId = `msg-assistant-${Date.now()}`;
      const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const div = document.createElement("div");
      div.id = msgId;
      div.className = "chat-turn assistant-turn flex flex-col items-start my-4 animate-fadeIn";
      div.innerHTML = `
      <div class="flex items-center gap-2 mb-1 text-xs text-cyan-600 dark:text-cyan-400 font-mono">
        <span class="flex items-center gap-1.5 font-bold">
          <span class="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 animate-ping"></span>
          JesseCoder
        </span>
        <span>\u2022</span>
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
      const contentEl = div.querySelector(".markdown-body");
      return { msgId, contentEl };
    }
    updateAssistantStream(contentEl, text) {
      contentEl.innerHTML = renderMarkdown(text) + '<span class="streaming-cursor inline-block w-2 h-4 bg-cyan-500 dark:bg-cyan-400 animate-pulse ml-1 align-middle"></span>';
      this.scrollToBottom();
    }
    finalizeAssistantMessage(contentEl, text, execResult) {
      let html = renderMarkdown(text);
      if (execResult) {
        html += this.createInlineExecutionCard(execResult);
      }
      contentEl.innerHTML = html;
      this.scrollToBottom();
    }
    createInlineExecutionCard(res) {
      const statusBg = res.success ? "bg-emerald-950/70 border-emerald-700/60" : "bg-rose-950/70 border-rose-700/60";
      const statusText = res.success ? "text-emerald-400" : "text-rose-400";
      const badge = res.success ? "\u2714 EXECUTION SUCCESS" : "\u2716 EXECUTION FAILED";
      return `
      <div class="inline-exec-card my-4 p-3 rounded-lg border ${statusBg} text-xs font-mono shadow-inner">
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <span class="font-bold ${statusText}">${badge} (Exit ${res.exit_code})</span>
          <span class="text-slate-400">${res.execution_time_ms} ms</span>
        </div>
        ${res.stdout ? `<div class="mt-2 text-emerald-200 font-mono whitespace-pre-wrap">${escapeHtml(res.stdout)}</div>` : ""}
        ${res.stderr ? `<div class="mt-2 text-rose-300 font-mono whitespace-pre-wrap">${escapeHtml(res.stderr)}</div>` : ""}
      </div>
    `;
    }
    displayExtractedCode(codeBlock) {
      if (!codeBlock || !codeBlock.code.trim()) {
        this.codeLangBadgeEl.textContent = "NONE";
        this.codeLineCountEl.textContent = "0 lines";
        this.codeContentEl.textContent = "# No code extracted yet.\n# Send a coding prompt to generate code here.";
        this.btnRunCodeEl.disabled = true;
        this.btnCopyCodeEl.disabled = true;
        return;
      }
      const lines = codeBlock.code.trim().split("\n").length;
      const detectedLang = codeBlock.language || "python";
      const overrideLang = this.langSelectEl.value;
      const effectiveLang = overrideLang && overrideLang !== "auto" ? overrideLang : detectedLang;
      this.codeLangBadgeEl.textContent = effectiveLang.toUpperCase();
      this.codeLineCountEl.textContent = `${lines} line${lines === 1 ? "" : "s"}`;
      this.codeContentEl.textContent = codeBlock.code.trim();
      this.btnRunCodeEl.disabled = false;
      this.btnCopyCodeEl.disabled = false;
      if (overrideLang === "auto") {
        const opt = this.blockLangOverrideEl.querySelector(`option[value="${detectedLang}"]`);
        if (opt)
          this.blockLangOverrideEl.value = detectedLang;
      }
    }
    getCurrentCode() {
      const code = this.codeContentEl.textContent || "";
      if (!code || code.startsWith("# No code"))
        return null;
      const headerLang = this.langSelectEl.value;
      const blockLang = this.blockLangOverrideEl.value;
      let language = "python";
      if (headerLang && headerLang !== "auto") {
        language = headerLang;
      } else if (blockLang && blockLang !== "auto") {
        language = blockLang;
      } else {
        language = this.codeLangBadgeEl.textContent?.toLowerCase().replace(/\s/g, "") || "python";
      }
      return { code, language };
    }
    setExecutingState(isExecuting) {
      if (isExecuting) {
        this.btnRunCodeEl.disabled = true;
        this.btnRunCodeEl.innerHTML = `
        <svg class="w-3 h-3 animate-spin mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        <span>Running\u2026</span>
      `;
        this.execStatusBadgeEl.textContent = "RUNNING \u23F3";
        this.execStatusBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800";
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
    renderExecutionResult(res) {
      if (res.success) {
        this.execStatusBadgeEl.textContent = `SUCCESS (0)`;
        this.execStatusBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-700/80";
      } else {
        this.execStatusBadgeEl.textContent = `FAILED (${res.exit_code})`;
        this.execStatusBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-700/80";
      }
      this.execTimeBadgeEl.textContent = `${res.execution_time_ms} ms`;
      this.execTimeBadgeEl.classList.remove("hidden");
      if (res.command && res.command.length > 0) {
        this.execCommandBadgeEl.textContent = res.command.join(" ");
        this.execCommandBadgeEl.classList.remove("hidden");
      }
      let output = "";
      if (res.stdout) {
        output += `<span class="text-emerald-300">${escapeHtml(res.stdout)}</span>`;
      }
      if (res.stderr) {
        if (output)
          output += "\n";
        output += `<span class="text-rose-400">${escapeHtml(res.stderr)}</span>`;
      }
      if (!res.stdout && !res.stderr) {
        output = '<span class="text-slate-500 italic">[Process completed with no console output]</span>';
      }
      this.consoleOutputEl.innerHTML = output;
      this.consoleOutputEl.scrollTop = this.consoleOutputEl.scrollHeight;
    }
    clearConsole() {
      this.consoleOutputEl.innerHTML = '<span class="text-slate-400 dark:text-slate-600 font-mono text-xs italic">Console ready. Click [Run] or enable Auto-Run.</span>';
      this.execStatusBadgeEl.textContent = "IDLE";
      this.execStatusBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700";
      this.execTimeBadgeEl.classList.add("hidden");
      this.execCommandBadgeEl.classList.add("hidden");
    }
    showRawModal(payload) {
      const isObj = typeof payload === "object" && payload !== null;
      const rawText = isObj ? payload.raw : payload;
      const wasCanned = isObj ? !!payload.was_canned : false;
      this.rawContentEl.textContent = rawText || "No raw response recorded yet. Send a prompt first.";
      if (wasCanned) {
        this.rawCannedWarningEl.classList.remove("hidden");
        this.rawQualityBadgeEl.textContent = "CANNED / BENCHMARK";
        this.rawQualityBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono border bg-amber-950 border-amber-700 text-amber-300";
        this.rawQualityBadgeEl.classList.remove("hidden");
      } else {
        this.rawCannedWarningEl.classList.add("hidden");
        if (rawText && rawText.length > 10) {
          this.rawQualityBadgeEl.textContent = "LIVE RESPONSE";
          this.rawQualityBadgeEl.className = "px-2 py-0.5 rounded text-[10px] font-mono border bg-emerald-950 border-emerald-700 text-emerald-300";
          this.rawQualityBadgeEl.classList.remove("hidden");
        } else {
          this.rawQualityBadgeEl.classList.add("hidden");
        }
      }
      if (rawText) {
        const charCount = rawText.length;
        const hasCode = /```/.test(rawText) || /def |class |function |import /.test(rawText);
        this.rawCharCountEl.textContent = `${charCount.toLocaleString()} chars`;
        this.rawHasCodeEl.textContent = hasCode ? "\u27E8/\u27E9 Contains code blocks" : "\u2014 No code blocks";
        this.rawHasCodeEl.className = hasCode ? "text-cyan-600" : "text-slate-600";
        this.rawModelInfoEl.textContent = "jesse.solidsf.com/api/v1";
        this.rawStatsBarEl.classList.remove("hidden");
      } else {
        this.rawStatsBarEl.classList.add("hidden");
      }
      this.rawModalEl.classList.remove("hidden");
    }
    hideRawModal() {
      this.rawModalEl.classList.add("hidden");
    }
    clearDialogue() {
      this.dialogueEl.innerHTML = `
      <div id="welcome-message" class="text-center py-10 px-4">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800/80 mb-4 shadow-xl">
          <span class="text-3xl text-cyan-600 dark:text-cyan-400 font-mono">\u26A1</span>
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
    showToast(message, isError = false) {
      const toast = document.createElement("div");
      toast.className = `fixed bottom-6 right-6 px-4 py-2.5 rounded-xl border text-xs font-mono shadow-2xl z-50 transition-all duration-300 transform translate-y-2 opacity-0 ${isError ? "bg-rose-950 border-rose-700 text-rose-200" : "bg-slate-900 border-cyan-600/80 text-cyan-200"}`;
      toast.textContent = message;
      document.body.appendChild(toast);
      requestAnimationFrame(() => {
        toast.classList.remove("translate-y-2", "opacity-0");
      });
      setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-2");
        setTimeout(() => toast.remove(), 300);
      }, 2500);
    }
    scrollToBottom() {
      this.dialogueEl.scrollTop = this.dialogueEl.scrollHeight;
    }
    addFeedbackButtons(msgEl, onThumbsUp, onThumbsDown) {
      if (msgEl.querySelector(".feedback-actions"))
        return;
      const actionsBar = document.createElement("div");
      actionsBar.className = "feedback-actions flex items-center gap-2 mt-2 ml-1";
      actionsBar.innerHTML = `
      <span class="text-[10px] font-mono text-slate-400 dark:text-slate-600">Was this helpful?</span>
      <button class="btn-thumbs-up px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/60 hover:bg-emerald-200 dark:hover:bg-emerald-900 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-400 text-[11px] font-mono transition" title="Good answer \u2014 teach jesse-prod">\u{1F44D}</button>
      <button class="btn-thumbs-down px-2 py-0.5 rounded bg-rose-100 dark:bg-rose-950/60 hover:bg-rose-200 dark:hover:bg-rose-900 border border-rose-300 dark:border-rose-700/60 text-rose-700 dark:text-rose-400 text-[11px] font-mono transition" title="Wrong answer \u2014 correct jesse-prod">\u{1F44E}</button>
    `;
      const thumbsUp = actionsBar.querySelector(".btn-thumbs-up");
      const thumbsDown = actionsBar.querySelector(".btn-thumbs-down");
      thumbsUp.addEventListener("click", () => {
        thumbsUp.textContent = "\u2713 Thanks!";
        thumbsUp.disabled = true;
        thumbsDown.disabled = true;
        onThumbsUp();
      });
      thumbsDown.addEventListener("click", () => {
        thumbsDown.textContent = "\u2192 Correcting...";
        thumbsDown.disabled = true;
        thumbsUp.disabled = true;
        onThumbsDown();
      });
      const bubble = msgEl.closest(".assistant-turn");
      if (bubble) {
        bubble.appendChild(actionsBar);
      }
    }
    showFeedbackModal(onSubmit, onCancel) {
      const modal = document.getElementById("feedback-modal");
      const input = document.getElementById("feedback-correction-input");
      const btnSubmit = document.getElementById("btn-feedback-submit");
      const btnCancel = document.getElementById("btn-feedback-cancel");
      const btnClose = document.getElementById("btn-close-feedback");
      input.value = "";
      modal.classList.remove("hidden");
      input.focus();
      const doSubmit = () => {
        const correction = input.value.trim();
        modal.classList.add("hidden");
        cleanup();
        onSubmit(correction);
      };
      const doCancel = () => {
        modal.classList.add("hidden");
        cleanup();
        onCancel();
      };
      const cleanup = () => {
        btnSubmit.removeEventListener("click", doSubmit);
        btnCancel.removeEventListener("click", doCancel);
        btnClose.removeEventListener("click", doCancel);
      };
      btnSubmit.addEventListener("click", doSubmit);
      btnCancel.addEventListener("click", doCancel);
      btnClose.addEventListener("click", doCancel);
    }
    showMemoryPanel() {
      const modal = document.getElementById("memory-modal");
      modal.classList.remove("hidden");
    }
    hideMemoryPanel() {
      const modal = document.getElementById("memory-modal");
      modal.classList.add("hidden");
    }
    renderMemoryContent(data, isError = false) {
      const el = document.getElementById("memory-content");
      if (isError) {
        el.innerHTML = `<span class="text-rose-400">\u26A0\uFE0F ${escapeHtml(String(data))}</span>`;
        return;
      }
      if (!data || Array.isArray(data) && data.length === 0) {
        el.innerHTML = '<span class="text-slate-400 italic">No memory stored yet.</span>';
        return;
      }
      if (Array.isArray(data)) {
        const items = data.map((fact, i) => {
          const text = fact.value ?? fact.fact ?? fact.content ?? JSON.stringify(fact);
          return `<div class="flex gap-2 py-1 border-b border-slate-100 dark:border-slate-800">
          <span class="text-violet-400 shrink-0">${i + 1}.</span>
          <span class="text-slate-700 dark:text-slate-300">${escapeHtml(String(text))}</span>
        </div>`;
        }).join("");
        el.innerHTML = items || '<span class="text-slate-400 italic">No memory stored yet.</span>';
      } else {
        el.textContent = JSON.stringify(data, null, 2);
      }
    }
    showDocsPanel(activeTab = "store") {
      const modal = document.getElementById("docs-modal");
      modal.classList.remove("hidden");
      this.switchDocsTab(activeTab);
    }
    hideDocsPanel() {
      const modal = document.getElementById("docs-modal");
      modal.classList.add("hidden");
    }
    switchDocsTab(tabName) {
      document.querySelectorAll(".docs-tab").forEach((btn) => {
        const b = btn;
        const isActive = b.getAttribute("data-docs-tab") === tabName;
        b.className = isActive ? "docs-tab px-4 py-2.5 text-xs font-mono font-bold border-b-2 border-emerald-500 text-emerald-600 dark:text-emerald-400 transition" : "docs-tab px-4 py-2.5 text-xs font-mono font-bold border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition";
      });
      document.querySelectorAll(".docs-tab-panel").forEach((panel) => {
        panel.classList.add("hidden");
      });
      const active = document.getElementById(`docs-tab-${tabName}`);
      if (active) {
        active.classList.remove("hidden");
        active.classList.add("flex-1", "overflow-auto");
      }
    }
    renderDocsList(data, isError = false) {
      const el = document.getElementById("docs-list-content");
      if (isError) {
        el.innerHTML = `<span class="text-rose-400">\u26A0\uFE0F ${escapeHtml(String(data))}</span>`;
        return;
      }
      const docs = Array.isArray(data) ? data : data?.documents ?? data?.data ?? [];
      if (!Array.isArray(docs) || docs.length === 0) {
        el.innerHTML = '<span class="text-slate-400 italic">No documents stored yet.</span>';
        return;
      }
      el.innerHTML = docs.map((doc) => `
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
        <div class="font-bold text-emerald-600 dark:text-emerald-400">${escapeHtml(String(doc.title ?? "(untitled)"))}</div>
        ${doc.id ? `<div class="text-slate-400 text-[10px] mt-0.5">ID: ${escapeHtml(String(doc.id))}</div>` : ""}
        ${doc.created_at ? `<div class="text-slate-400 text-[10px]">${escapeHtml(String(doc.created_at))}</div>` : ""}
      </div>
    `).join("");
    }
    renderDocSearchResults(data, isError = false) {
      const el = document.getElementById("doc-search-results");
      if (isError) {
        el.innerHTML = `<span class="text-rose-400">\u26A0\uFE0F ${escapeHtml(String(data))}</span>`;
        return;
      }
      const results = Array.isArray(data) ? data : data?.results ?? data?.data ?? [];
      if (!Array.isArray(results) || results.length === 0) {
        el.innerHTML = '<span class="text-slate-400 italic">No matching documents found.</span>';
        return;
      }
      el.innerHTML = results.map((r, i) => `
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-emerald-900/40">
        <div class="flex items-center justify-between mb-1">
          <span class="font-bold text-emerald-600 dark:text-emerald-400">${i + 1}. ${escapeHtml(String(r.title ?? "(untitled)"))}</span>
          ${r.score !== void 0 ? `<span class="text-[10px] text-slate-400 font-mono">score: ${Number(r.score).toFixed(3)}</span>` : ""}
        </div>
        ${r.content ? `<p class="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed line-clamp-3">${escapeHtml(String(r.content).slice(0, 300))}${String(r.content).length > 300 ? "..." : ""}</p>` : ""}
      </div>
    `).join("");
    }
    showDocStoreResult(message, isError = false) {
      const el = document.getElementById("doc-store-result");
      el.classList.remove("hidden");
      el.className = `mt-2 p-3 rounded-lg border text-xs font-mono ${isError ? "bg-rose-50 dark:bg-rose-950/40 border-rose-300 dark:border-rose-700 text-rose-700 dark:text-rose-300" : "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700 text-emerald-700 dark:text-emerald-300"}`;
      el.textContent = message;
      setTimeout(() => el.classList.add("hidden"), 4e3);
    }
  };

  // src/api.ts
  var API_BASE = window.location.origin;
  async function fetchHealth() {
    const resp = await fetch(`${API_BASE}/api/health`);
    if (!resp.ok) {
      throw new Error(`Health check failed: ${resp.statusText}`);
    }
    return resp.json();
  }
  async function resetConversation() {
    const resp = await fetch(`${API_BASE}/api/reset`, { method: "POST" });
    if (!resp.ok) {
      throw new Error(`Reset failed: ${resp.statusText}`);
    }
  }
  async function switchModel(model) {
    const resp = await fetch(`${API_BASE}/api/model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model })
    });
    if (!resp.ok) {
      throw new Error(`Failed to switch model: ${resp.statusText}`);
    }
    const data = await resp.json();
    return data.model;
  }
  async function executeCode(code, language = "python", timeout = 15) {
    const resp = await fetch(`${API_BASE}/api/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language, timeout })
    });
    if (!resp.ok) {
      throw new Error(`Execution request failed: ${resp.statusText}`);
    }
    return resp.json();
  }
  async function getRawResponse() {
    const resp = await fetch(`${API_BASE}/api/raw`);
    if (!resp.ok) {
      return { raw: "", was_canned: false };
    }
    const data = await resp.json();
    return {
      raw: data.raw || "",
      was_canned: !!data.was_canned,
      note: data.note || "",
      char_count: data.char_count || 0
    };
  }
  async function submitFeedback(messageId, rating, correction) {
    const body = { message_id: messageId, rating };
    if (correction && correction.trim())
      body.correction = correction.trim();
    const resp = await fetch(`${API_BASE}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    return resp.json();
  }
  async function getMemory() {
    const resp = await fetch(`${API_BASE}/api/memory`);
    return resp.json();
  }
  async function deleteMemory() {
    const resp = await fetch(`${API_BASE}/api/memory`, { method: "DELETE" });
    return resp.json();
  }
  async function storeDocument(title, content, metadata) {
    const resp = await fetch(`${API_BASE}/api/documents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, content, metadata })
    });
    return resp.json();
  }
  async function listDocuments() {
    const resp = await fetch(`${API_BASE}/api/documents`);
    return resp.json();
  }
  async function queryDocuments(query, topK = 5) {
    const resp = await fetch(`${API_BASE}/api/documents/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK })
    });
    return resp.json();
  }
  async function streamChat(prompt, model, onToken, onDone, onError) {
    let doneOrErrorReceived = false;
    try {
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, model })
      });
      if (!response.ok) {
        const errText = await response.text();
        await onError(`Server error (${response.status}): ${errText}`);
        return;
      }
      if (!response.body) {
        await onError("No response stream body available.");
        return;
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      const processLine = async (line) => {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data: "))
          return;
        const jsonStr = trimmed.substring(6).trim();
        try {
          const eventData = JSON.parse(jsonStr);
          if (eventData.event === "token") {
            onToken(eventData.token);
          } else if (eventData.event === "done") {
            doneOrErrorReceived = true;
            await onDone(eventData);
          } else if (eventData.event === "error") {
            doneOrErrorReceived = true;
            await onError(eventData.message);
          }
        } catch (e) {
          console.warn("Failed to parse SSE line:", jsonStr, e);
        }
      };
      while (true) {
        const { done, value } = await reader.read();
        if (done)
          break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          await processLine(line);
        }
      }
      if (buffer.trim()) {
        await processLine(buffer);
      }
      if (!doneOrErrorReceived) {
        await onDone({
          event: "done",
          full_text: "",
          extracted_code: null,
          raw_response: ""
        });
      }
    } catch (err) {
      await onError(`Network/Stream error: ${err?.message || err}`);
    }
  }

  // src/app.ts
  var JesseCoderApp = class {
    constructor() {
      this.lastRawResponse = "";
      this.lastUserPrompt = "";
      this.isProcessing = false;
      this.lastAssistantMsgEl = null;
      this.lastAssistantMsgId = "";
      this.ui = new UIController();
      this.bindEvents();
      this.checkBackendHealth();
    }
    bindEvents() {
      const btnSend = document.getElementById("btn-send");
      const promptInput = document.getElementById("prompt-input");
      const btnRunCode = document.getElementById("btn-run-code");
      const btnToggleRaw = document.getElementById("btn-toggle-raw");
      const btnReset = document.getElementById("btn-reset");
      const chipButtons = document.querySelectorAll(".prompt-chip");
      btnSend?.addEventListener("click", () => {
        this.handleSubmit();
      });
      promptInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.handleSubmit();
        }
      });
      btnRunCode?.addEventListener("click", () => {
        this.handleExecuteCode();
      });
      btnToggleRaw?.addEventListener("click", async () => {
        try {
          const rawData = await getRawResponse();
          this.lastRawResponse = rawData.raw;
          this.ui.showRawModal(rawData.raw || "(no response yet \u2014 send a prompt first)");
        } catch {
          this.ui.showRawModal("Failed to fetch raw API response.");
        }
      });
      btnReset?.addEventListener("click", async () => {
        this.isProcessing = false;
        this.ui.setInputEnabled(true);
        if (confirm("Reset conversation context? This clears history and current session.")) {
          try {
            await resetConversation();
            this.ui.clearDialogue();
            this.lastRawResponse = "";
            this.lastUserPrompt = "";
            this.ui.showToast("Conversation context reset.");
          } catch (err) {
            this.ui.showToast(`Reset failed: ${err.message}`, true);
          }
        }
      });
      chipButtons.forEach((chip) => {
        chip.addEventListener("click", () => {
          const text = chip.getAttribute("data-prompt") || chip.textContent || "";
          promptInput.value = text.trim();
          promptInput.style.height = "auto";
          promptInput.style.height = `${Math.min(promptInput.scrollHeight, 200)}px`;
          promptInput.focus();
        });
      });
      const modelSelect = document.getElementById("model-select");
      modelSelect?.addEventListener("change", async () => {
        const selectedModel = modelSelect.value;
        try {
          await switchModel(selectedModel);
          this.ui.setStatus(`ONLINE: ${selectedModel}`, true);
          this.ui.showToast(`Switched active model to ${selectedModel}`);
        } catch (err) {
          this.ui.showToast(`Model switch failed: ${err.message}`, true);
        }
      });
      document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "e") {
          e.preventDefault();
          this.handleExecuteCode();
        }
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "r") {
          e.preventDefault();
          btnToggleRaw?.dispatchEvent(new MouseEvent("click"));
        }
      });
      const btnMemory = document.getElementById("btn-memory");
      btnMemory?.addEventListener("click", () => {
        this.ui.showMemoryPanel();
        this.loadMemory();
      });
      document.getElementById("btn-close-memory")?.addEventListener("click", () => {
        this.ui.hideMemoryPanel();
      });
      document.getElementById("btn-memory-refresh")?.addEventListener("click", () => {
        this.loadMemory();
      });
      document.getElementById("btn-memory-erase")?.addEventListener("click", async () => {
        if (!confirm("Erase ALL of Jesse's memory for this API key? This cannot be undone."))
          return;
        try {
          const result = await deleteMemory();
          this.ui.showToast(result.status === "ok" ? "\u{1F5D1}\uFE0F Memory erased!" : "\u26A0\uFE0F Memory erase had issues", result.status !== "ok");
          this.loadMemory();
        } catch (err) {
          this.ui.showToast(`Memory erase failed: ${err.message}`, true);
        }
      });
      const btnDocs = document.getElementById("btn-documents");
      btnDocs?.addEventListener("click", () => {
        this.ui.showDocsPanel("store");
      });
      document.getElementById("btn-close-docs")?.addEventListener("click", () => {
        this.ui.hideDocsPanel();
      });
      document.querySelectorAll(".docs-tab").forEach((btn) => {
        btn.addEventListener("click", () => {
          const tab = btn.getAttribute("data-docs-tab") || "store";
          this.ui.switchDocsTab(tab);
          if (tab === "list")
            this.loadDocsList();
        });
      });
      document.getElementById("btn-doc-store")?.addEventListener("click", async () => {
        const titleInput = document.getElementById("doc-title-input");
        const contentInput = document.getElementById("doc-content-input");
        const title = titleInput?.value.trim();
        const content = contentInput?.value.trim();
        if (!title || !content) {
          this.ui.showDocStoreResult("\u26A0\uFE0F Title and content are required.", true);
          return;
        }
        try {
          const result = await storeDocument(title, content);
          const ok = result.status === "ok";
          this.ui.showDocStoreResult(ok ? `\u2705 Document "${title}" stored successfully!` : `\u26A0\uFE0F Store may have issues: ${result.detail}`, !ok);
          if (ok) {
            titleInput.value = "";
            contentInput.value = "";
          }
        } catch (err) {
          this.ui.showDocStoreResult(`\u274C Error: ${err.message}`, true);
        }
      });
      document.getElementById("btn-docs-refresh")?.addEventListener("click", () => {
        this.loadDocsList();
      });
      document.getElementById("btn-doc-search")?.addEventListener("click", () => {
        this.handleDocSearch();
      });
      const docQueryInput = document.getElementById("doc-query-input");
      docQueryInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter")
          this.handleDocSearch();
      });
    }
    async checkBackendHealth() {
      try {
        const health = await fetchHealth();
        this.ui.setStatus(`ONLINE: ${health.model}`, true);
        if (health.model) {
          this.ui.setSelectedModel(health.model);
        }
      } catch {
        this.ui.setStatus("DISCONNECTED", false);
      }
    }
    buildRepairPrompt(originalPrompt, failedCode, language, execResult, attempt, maxRetries) {
      const diagParts = [];
      if (execResult.exit_code !== void 0 && execResult.exit_code !== null) {
        diagParts.push(`Exit Code: ${execResult.exit_code}`);
      }
      if (execResult.timed_out) {
        diagParts.push(`Status: EXECUTION TIMED OUT`);
      }
      if (execResult.stderr && execResult.stderr.trim()) {
        diagParts.push(`Error Output (stderr / Traceback):
${execResult.stderr.trim()}`);
      }
      if (execResult.stdout && execResult.stdout.trim()) {
        diagParts.push(`Standard Output (stdout):
${execResult.stdout.trim()}`);
      }
      const diagnostic = diagParts.length > 0 ? diagParts.join("\n\n") : "Process exited with non-zero status code.";
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
    async runAutoRepairLoop(originalPrompt, initialCode, initialLanguage, initialResult, model) {
      const maxRetries = this.ui.getMaxRetries();
      let currentAttempt = 1;
      let currentCode = initialCode;
      let currentLanguage = initialLanguage;
      let currentResult = initialResult;
      while (currentAttempt <= maxRetries && !currentResult.success) {
        const errorLines = (currentResult.stderr || currentResult.stdout || "Non-zero exit code").trim().split("\n").filter((l) => l.trim().length > 0);
        const errorSummary = errorLines[errorLines.length - 1] || `Exit code ${currentResult.exit_code}`;
        const { contentEl: repairContentEl } = this.ui.appendRepairMessage(currentAttempt, maxRetries, errorSummary);
        const repairPrompt = this.buildRepairPrompt(originalPrompt, currentCode, currentLanguage, currentResult, currentAttempt, maxRetries);
        let repairAccumulated = "";
        let repairExtractedCode = null;
        try {
          await streamChat(repairPrompt, model, (token) => {
            repairAccumulated += token;
            this.ui.updateAssistantStream(repairContentEl, repairAccumulated);
          }, async (doneData) => {
            this.lastRawResponse = doneData.raw_response;
            if (doneData.extracted_code && doneData.extracted_code.code.trim()) {
              repairExtractedCode = doneData.extracted_code;
            }
          }, (err) => {
            repairAccumulated += `

> \u26A0\uFE0F **Repair Stream Error:** ${err}`;
            this.ui.finalizeAssistantMessage(repairContentEl, repairAccumulated);
          });
          if (repairExtractedCode) {
            currentCode = repairExtractedCode.code;
            currentLanguage = repairExtractedCode.language || currentLanguage;
            this.ui.displayExtractedCode(repairExtractedCode);
            this.ui.setExecutingState(true);
            try {
              currentResult = await executeCode(currentCode, currentLanguage);
              this.ui.renderExecutionResult(currentResult);
              this.ui.finalizeAssistantMessage(repairContentEl, repairAccumulated, currentResult);
              if (currentResult.success) {
                this.ui.showToast(`\u2713 Auto-Repair succeeded on attempt ${currentAttempt}!`, false);
                break;
              } else {
                this.ui.showToast(`Repair attempt ${currentAttempt}/${maxRetries} failed (Exit ${currentResult.exit_code}).`, true);
              }
            } catch (execErr) {
              this.ui.showToast(`Repair execution error: ${execErr.message}`, true);
            } finally {
              this.ui.setExecutingState(false);
            }
          } else {
            this.ui.finalizeAssistantMessage(repairContentEl, `${repairAccumulated}

> \u26A0\uFE0F *No code block found in repair response.*`);
            break;
          }
        } catch (streamErr) {
          this.ui.showToast(`Repair loop error: ${streamErr.message}`, true);
          break;
        }
        currentAttempt++;
      }
      if (!currentResult.success && currentAttempt > maxRetries) {
        this.ui.showToast(`Auto-repair reached max retries limit (${maxRetries}).`, true);
      }
    }
    async handleSubmit() {
      const prompt = this.ui.getPrompt();
      if (!prompt || this.isProcessing)
        return;
      this.isProcessing = true;
      this.ui.setInputEnabled(false);
      this.ui.clearPrompt();
      this.lastUserPrompt = prompt;
      this.ui.appendUserMessage(prompt);
      const { contentEl, msgId } = this.ui.appendAssistantMessage();
      let accumulatedText = "";
      let executionResult = null;
      let extractedCodeBlock = null;
      this.lastAssistantMsgId = msgId;
      try {
        const model = this.ui.getSelectedModel();
        await streamChat(prompt, model, (token) => {
          accumulatedText += token;
          this.ui.updateAssistantStream(contentEl, accumulatedText);
        }, async (data) => {
          try {
            this.lastRawResponse = data.raw_response;
            this.ui.displayExtractedCode(data.extracted_code);
            if (data.extracted_code && data.extracted_code.code.trim()) {
              extractedCodeBlock = data.extracted_code;
            }
            if (this.ui.isAutoRunEnabled() && extractedCodeBlock) {
              this.ui.setExecutingState(true);
              try {
                executionResult = await executeCode(extractedCodeBlock.code, extractedCodeBlock.language || "python");
                this.ui.renderExecutionResult(executionResult);
                this.ui.showToast(executionResult.success ? "Auto-execution succeeded!" : "Auto-execution failed with errors.", !executionResult.success);
              } catch (execErr) {
                this.ui.showToast(`Execution error: ${execErr.message}`, true);
              } finally {
                this.ui.setExecutingState(false);
              }
            }
            this.ui.finalizeAssistantMessage(contentEl, accumulatedText || data.full_text, executionResult);
            const bubbleEl = contentEl.closest(".assistant-turn");
            if (bubbleEl) {
              this.ui.addFeedbackButtons(contentEl, () => {
                this.handleFeedback(msgId, bubbleEl, "thumbs_up");
              }, () => {
                this.ui.showFeedbackModal((correction) => {
                  this.handleFeedback(msgId, bubbleEl, "thumbs_down", correction || void 0);
                }, () => {
                  this.ui.showToast("Feedback cancelled.");
                });
              });
            }
            if (executionResult && !executionResult.success && this.ui.isAutoRepairEnabled() && extractedCodeBlock) {
              await this.runAutoRepairLoop(prompt, extractedCodeBlock.code, extractedCodeBlock.language || "python", executionResult, model);
            }
          } catch (finalizeErr) {
            console.error("Error finalizing message:", finalizeErr);
          }
        }, (errorMessage) => {
          this.ui.finalizeAssistantMessage(contentEl, `${accumulatedText}

> \u26A0\uFE0F **Error:** ${errorMessage}`);
          this.ui.showToast(`Error: ${errorMessage}`, true);
        });
      } catch (streamErr) {
        this.ui.showToast(`Stream error: ${streamErr.message}`, true);
      } finally {
        this.isProcessing = false;
        this.ui.setInputEnabled(true);
      }
    }
    async handleExecuteCode() {
      const currentCode = this.ui.getCurrentCode();
      if (!currentCode || !currentCode.code.trim()) {
        this.ui.showToast("No executable code available to run.", true);
        return;
      }
      this.ui.setExecutingState(true);
      try {
        const res = await executeCode(currentCode.code, currentCode.language);
        this.ui.renderExecutionResult(res);
        this.ui.showToast(res.success ? `Execution SUCCESS (Exit ${res.exit_code})` : `Execution FAILED (Exit ${res.exit_code})`, !res.success);
        if (!res.success && this.ui.isAutoRepairEnabled()) {
          const model = this.ui.getSelectedModel();
          const baseTask = this.lastUserPrompt || `Fix execution error in the provided ${currentCode.language} code.`;
          await this.runAutoRepairLoop(baseTask, currentCode.code, currentCode.language, res, model);
        }
      } catch (err) {
        this.ui.showToast(`Execution error: ${err.message}`, true);
      } finally {
        this.ui.setExecutingState(false);
      }
    }
    async loadMemory() {
      const contentEl = document.getElementById("memory-content");
      if (contentEl)
        contentEl.innerHTML = '<span class="text-slate-400 italic animate-pulse">Loading...</span>';
      try {
        const result = await getMemory();
        this.ui.renderMemoryContent(result.data ?? result, result.status === "degraded");
      } catch (err) {
        this.ui.renderMemoryContent(`Failed to load memory: ${err.message}`, true);
      }
    }
    async loadDocsList() {
      const el = document.getElementById("docs-list-content");
      if (el)
        el.innerHTML = '<span class="text-slate-400 italic animate-pulse">Loading...</span>';
      try {
        const result = await listDocuments();
        this.ui.renderDocsList(result.data ?? result, result.status === "degraded");
      } catch (err) {
        this.ui.renderDocsList(`Failed to load documents: ${err.message}`, true);
      }
    }
    async handleDocSearch() {
      const queryInput = document.getElementById("doc-query-input");
      const topKSelect = document.getElementById("doc-topk-select");
      const query = queryInput?.value.trim();
      if (!query) {
        this.ui.showToast("Please enter a search query.", true);
        return;
      }
      const topK = parseInt(topKSelect?.value || "5", 10);
      const resultsEl = document.getElementById("doc-search-results");
      if (resultsEl)
        resultsEl.innerHTML = '<span class="text-slate-400 italic animate-pulse">Searching...</span>';
      try {
        const result = await queryDocuments(query, topK);
        this.ui.renderDocSearchResults(result.data ?? result, result.status === "degraded");
      } catch (err) {
        this.ui.renderDocSearchResults(`Search failed: ${err.message}`, true);
      }
    }
    async handleFeedback(msgId, msgEl, rating, correction) {
      try {
        await submitFeedback(msgId, rating, correction);
        if (rating === "thumbs_up") {
          this.ui.showToast("\u{1F44D} Thanks! jesse-prod learned from this.");
        } else {
          this.ui.showToast(correction ? "\u{1F44E} Correction submitted \u2014 jesse-prod will improve!" : "\u{1F44E} Marked as wrong.");
        }
      } catch (err) {
        this.ui.showToast(`Feedback failed: ${err.message}`, true);
      }
    }
  };
  window.addEventListener("DOMContentLoaded", () => {
    new JesseCoderApp();
  });
})();
