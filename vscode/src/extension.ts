import * as vscode from 'vscode';
import { SidebarProvider } from './SidebarProvider';

export function activate(context: vscode.ExtensionContext) {
  const sidebarProvider = new SidebarProvider(context.extensionUri);

  // Register the sidebar webview
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      "gitpulse.sidebarView",
      sidebarProvider,
      { webviewOptions: { retainContextWhenHidden: true } }
    )
  );

  // S20.7 — "Generate Standup" command: focus sidebar and trigger generation
  context.subscriptions.push(
    vscode.commands.registerCommand('gitpulse.generateStandup', async () => {
      await vscode.commands.executeCommand('gitpulse.sidebarView.focus');
      sidebarProvider.triggerGenerate();
    })
  );

  // Legacy refresh command kept for back-compat
  context.subscriptions.push(
    vscode.commands.registerCommand('gitpulse.refresh', () => {
      sidebarProvider._view?.webview.postMessage({ type: 'refresh' });
    })
  );
}

export function deactivate() {}
