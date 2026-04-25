import * as vscode from "vscode";
import * as path from "path";

export class SidebarProvider implements vscode.WebviewViewProvider {
  _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(webviewView: vscode.WebviewView) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    // S20.2 & S20.3 — Read config and workspace repos
    const config = vscode.workspace.getConfiguration("gitpulse");
    const apiUrl: string = config.get("apiUrl") ?? "http://localhost:8000";
    const username: string = config.get("username") ?? "";

    const repos: string[] = (vscode.workspace.workspaceFolders ?? []).map(
      (folder) => path.basename(folder.uri.fsPath)
    );

    webviewView.webview.html = this._getHtmlForWebview(
      webviewView.webview,
      apiUrl
    );

    // S20.4 — Post init message once webview is ready
    webviewView.webview.onDidReceiveMessage(async (data) => {
      switch (data.type) {
        case "webviewReady": {
          webviewView.webview.postMessage({
            type: "init",
            config: { apiUrl, username, repos },
          });
          break;
        }
        case "onInfo": {
          if (!data.value) {
            return;
          }
          vscode.window.showInformationMessage(data.value);
          break;
        }
        case "onError": {
          if (!data.value) {
            return;
          }
          vscode.window.showErrorMessage(data.value);
          break;
        }
      }
    });
  }

  /** Called by the generate command to trigger generation from the command palette. */
  public triggerGenerate(): void {
    this._view?.webview.postMessage({ type: "triggerGenerate" });
  }

  public revive(panel: vscode.WebviewView) {
    this._view = panel;
  }

  private _getHtmlForWebview(webview: vscode.Webview, apiUrl: string) {
    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.css")
    );
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.js")
    );

    const nonce = getNonce();

    // S20.1 (CSP) — include connect-src for the configured API URL so fetch works
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'none';
                 style-src ${webview.cspSource} 'unsafe-inline';
                 script-src 'nonce-${nonce}';
                 connect-src ${apiUrl} http://localhost:* https:;">
  <link href="${styleMainUri}" rel="stylesheet">
  <title>GitPulse</title>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-logo">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="1,12 4,12 6,5 8,19 10,9 12,15 14,8 16,12 19,12 22,12" />
        </svg>
        <span class="logo-text">GitPulse</span>
      </div>
      <p class="header-sub">AI Standup Generator</p>
    </div>

    <div id="repos-section" class="repos-section hidden"></div>

    <div id="content" class="content">
      <div class="splash">
        <div class="splash-icon">⚡</div>
        <p>Loading workspace…</p>
      </div>
    </div>

    <div class="actions">
      <button id="generate-btn" disabled>Generate Standup</button>
    </div>
  </div>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
  }
}

function getNonce() {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
