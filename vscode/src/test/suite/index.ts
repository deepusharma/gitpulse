import * as path from 'path';
import * as fs from 'fs';

// eslint-disable-next-line @typescript-eslint/no-require-imports
const Mocha = require('mocha') as typeof import('mocha');

export function run(): Promise<void> {
  const mocha = new Mocha({ ui: 'tdd', color: true, timeout: 10000 });

  const testsRoot = path.resolve(__dirname, '.');

  // Discover compiled test files without a glob dependency
  const files = fs
    .readdirSync(testsRoot)
    .filter((f) => f.endsWith('.test.js'));

  files.forEach((f) => mocha.addFile(path.resolve(testsRoot, f)));

  return new Promise((resolve, reject) => {
    try {
      mocha.run((failures: number) => {
        if (failures > 0) {
          reject(new Error(`${failures} tests failed.`));
        } else {
          resolve();
        }
      });
    } catch (err) {
      console.error(err);
      reject(err);
    }
  });
}
