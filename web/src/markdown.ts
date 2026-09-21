/**
 * Lightweight and safe markdown renderer with code block handling.
 */

export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function renderMarkdown(markdown: string): string {
  if (!markdown) return '';

  const codeBlocks: string[] = [];
  // Extract code blocks first to protect formatting
  let processed = markdown.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (_match, lang, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
    const safeLang = escapeHtml(lang || 'text');
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

  // Headers
  processed = processed
    .replace(/^### (.*$)/gim, '<h3 class="text-base font-bold text-cyan-300 mt-4 mb-2 tracking-wide">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-lg font-bold text-cyan-200 mt-5 mb-2.5 tracking-wide">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-xl font-extrabold text-cyan-100 mt-6 mb-3 tracking-wide border-b border-slate-800 pb-1">$1</h1>');

  // Bold & Italic
  processed = processed
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-200 font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-slate-300 italic">$1</em>');

  // Inline code
  processed = processed.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-800/80 text-cyan-300 font-mono text-xs border border-slate-700/50">$1</code>');

  // Horizontal rules
  processed = processed.replace(/^---$/gim, '<hr class="my-4 border-slate-800" />');

  // Bullet points
  processed = processed.replace(/^\s*[-*]\s+(.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-1">$1</li>');

  // Paragraph breaks
  processed = processed.replace(/\n\n+/g, '<br/><br/>');

  // Restore code blocks
  codeBlocks.forEach((block, idx) => {
    processed = processed.replace(`__CODE_BLOCK_${idx}__`, block);
  });

  return processed;
}
