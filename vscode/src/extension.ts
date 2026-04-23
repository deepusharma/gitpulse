import * as vscode from 'vscode';
import { SidebarProvider } from './SidebarProvider';

export function activate(context: vscode.ExtensionContext) {
	const sidebarProvider = new SidebarProvider(context.extensionUri);
	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider("gitpulse.sidebarView", sidebarProvider)
	);

	context.subscriptions.push(
		vscode.commands.registerCommand('gitpulse.refresh', () => {
			sidebarProvider._view?.webview.postMessage({ type: 'refresh' });
		})
	);
}

export function deactivate() {}
