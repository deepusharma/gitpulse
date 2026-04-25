import * as assert from 'assert';
import * as vscode from 'vscode';

suite('GitPulse Extension — Smoke Tests', () => {
  /**
   * Test 1 — Extension activates successfully.
   *
   * The extension contributes a webview view, so VS Code needs a moment after
   * activation. We look it up by its published ID.
   */
  test('Extension is present in the extension host', () => {
    const ext = vscode.extensions.getExtension('deepusharma.gitpulse-vscode');
    assert.ok(
      ext !== undefined,
      'Extension "deepusharma.gitpulse-vscode" should be present'
    );
  });

  /**
   * Test 2 — `gitpulse.generateStandup` command is registered.
   */
  test('gitpulse.generateStandup command is registered', async () => {
    const commands = await vscode.commands.getCommands(true);
    assert.ok(
      commands.includes('gitpulse.generateStandup'),
      'Command "gitpulse.generateStandup" should be registered'
    );
  });

  /**
   * Test 3 — `gitpulse.refresh` command is registered (back-compat).
   */
  test('gitpulse.refresh command is registered', async () => {
    const commands = await vscode.commands.getCommands(true);
    assert.ok(
      commands.includes('gitpulse.refresh'),
      'Command "gitpulse.refresh" should be registered'
    );
  });

  /**
   * Test 4 — Default configuration values are present.
   */
  test('Default apiUrl configuration is set', () => {
    const config = vscode.workspace.getConfiguration('gitpulse');
    const apiUrl: string = config.get('apiUrl') ?? '';
    assert.strictEqual(
      apiUrl,
      'http://localhost:8000',
      'Default apiUrl should be http://localhost:8000'
    );
  });
});
