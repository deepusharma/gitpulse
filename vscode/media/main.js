(function () {
  "use strict";

  const vscode = acquireVsCodeApi();

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const generateBtn = /** @type {HTMLButtonElement} */ (document.getElementById("generate-btn"));
  const contentEl   = /** @type {HTMLElement} */ (document.getElementById("content"));
  const reposEl     = /** @type {HTMLElement} */ (document.getElementById("repos-section"));

  // ── State ─────────────────────────────────────────────────────────────────
  /** @type {{ apiUrl: string; username: string; repos: string[] } | null} */
  let cfg = null;

  // ── Bootstrap: tell the extension we're ready ────────────────────────────
  vscode.postMessage({ type: "webviewReady" });

  // ── Message listener ──────────────────────────────────────────────────────
  window.addEventListener("message", (event) => {
    const msg = event.data;
    switch (msg.type) {
      case "init":
        cfg = msg.config;
        render();
        break;
      case "triggerGenerate":
        if (!generateBtn.disabled) {
          generateBtn.click();
        }
        break;
      case "refresh":
        if (cfg) {
          generate();
        }
        break;
    }
  });

  // ── Generate button ───────────────────────────────────────────────────────
  generateBtn.addEventListener("click", () => {
    if (!cfg) {
      return;
    }
    generate();
  });

  // ── Render — drives all 4 UI states ──────────────────────────────────────
  function render() {
    if (!cfg) {
      return;
    }

    // State 1 — No Config
    if (!cfg.username) {
      generateBtn.disabled = true;
      reposEl.classList.add("hidden");
      setContent(
        `<div class="no-config">
          <div class="no-config-icon">⚙️</div>
          <p class="no-config-title">Username not set</p>
          <p class="no-config-hint">Open <strong>Settings → Extensions → GitPulse</strong> and add your GitHub username to get started.</p>
        </div>`
      );
      return;
    }

    // State 2 — Ready (repos detected)
    generateBtn.disabled = false;
    renderRepos(cfg.repos);
    setContent(
      `<div class="splash">
        <div class="splash-icon">✅</div>
        <p>Workspace ready.</p>
        <p class="splash-hint">Hit <strong>Generate Standup</strong> to analyse the last 7 days of commits.</p>
      </div>`
    );
  }

  // ── API fetch ─────────────────────────────────────────────────────────────
  function generate() {
    if (!cfg) {
      return;
    }

    generateBtn.disabled = true;
    reposEl.classList.remove("hidden");

    // State 3 — Loading
    setContent(
      `<div class="loading">
        <div class="spinner" aria-label="Loading"></div>
        <p>Analysing commits…</p>
      </div>`
    );

    fetch(`${cfg.apiUrl}/summarise`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: cfg.username,
        repos: cfg.repos.length ? cfg.repos : [cfg.username],
        days: 7,
      }),
    })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((err) => {
            throw new Error(err.error ?? `HTTP ${res.status}`);
          });
        }
        return res.json();
      })
      .then((data) => {
        // State 4 — Result
        generateBtn.disabled = false;
        setContent(renderSummary(data.display, data.summary));
      })
      .catch((err) => {
        generateBtn.disabled = false;
        const msg = err.message || "Unknown error";
        setContent(
          `<div class="error">
            <div class="error-icon">⚠️</div>
            <p class="error-title">Failed to connect</p>
            <p class="error-body">${escHtml(msg)}</p>
            <p class="error-hint">Ensure the GitPulse API is running at <code>${escHtml(cfg.apiUrl)}</code>.</p>
          </div>`
        );
        vscode.postMessage({ type: "onError", value: msg });
      });
  }

  // ── Render helpers ────────────────────────────────────────────────────────
  function renderRepos(repos) {
    if (!repos || repos.length === 0) {
      reposEl.classList.add("hidden");
      return;
    }
    reposEl.classList.remove("hidden");
    reposEl.innerHTML =
      `<div class="repos-label">Detected repos</div>` +
      repos.map((r) => `<span class="repo-chip">${escHtml(r)}</span>`).join("");
  }

  /**
   * Renders the API response into a human-friendly summary block.
   * Uses markdown-lite parsing (bold, bullet lists, headings).
   */
  function renderSummary(display, summary) {
    const formatted = markdownLite(summary || "No summary returned.");
    return `
      <div class="result">
        <div class="result-section">
          <div class="result-label">Summary</div>
          <div class="result-body">${formatted}</div>
        </div>
        ${display ? `
        <details class="result-commits">
          <summary class="result-commits-toggle">Commit breakdown</summary>
          <pre class="result-commits-body">${escHtml(display)}</pre>
        </details>` : ""}
      </div>`;
  }

  /** Minimal markdown-lite: h1–h3, bold, italic, bullets */
  function markdownLite(md) {
    return md
      .split("\n")
      .map((line) => {
        if (/^### (.+)/.test(line)) {
          return `<h3>${escHtml(line.replace(/^### /, ""))}</h3>`;
        }
        if (/^## (.+)/.test(line)) {
          return `<h2>${escHtml(line.replace(/^## /, ""))}</h2>`;
        }
        if (/^# (.+)/.test(line)) {
          return `<h1>${escHtml(line.replace(/^# /, ""))}</h1>`;
        }
        if (/^\* (.+)/.test(line)) {
          return `<li>${inlineMarkdown(line.replace(/^\* /, ""))}</li>`;
        }
        if (/^- (.+)/.test(line)) {
          return `<li>${inlineMarkdown(line.replace(/^- /, ""))}</li>`;
        }
        if (line.trim() === "") {
          return "<br>";
        }
        return `<p>${inlineMarkdown(line)}</p>`;
      })
      .join("\n");
  }

  function inlineMarkdown(text) {
    return escHtml(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
  }

  function setContent(html) {
    contentEl.innerHTML = html;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
}());
