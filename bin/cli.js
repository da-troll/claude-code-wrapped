#!/usr/bin/env node

const { spawn, spawnSync } = require('child_process');

// Pass through all arguments
const args = process.argv.slice(2);

// Check if a command exists
function commandExists(cmd) {
  const result = spawnSync(cmd, ['--version'], { stdio: 'ignore' });
  return result.status === 0;
}

// Check if Python module is installed
function pythonModuleExists() {
  const result = spawnSync('python3', ['-c', 'import claude_code_wrapped'], { stdio: 'ignore' });
  return result.status === 0;
}

// Try to find the best way to run the Python package
function findExecutor() {
  // Try uvx first (recommended)
  if (commandExists('uvx')) {
    return { cmd: 'uvx', args: ['claude-code-wrapped', ...args] };
  }

  // Try pipx
  if (commandExists('pipx')) {
    return { cmd: 'pipx', args: ['run', 'claude-code-wrapped', ...args] };
  }

  // Try direct python module
  if (pythonModuleExists()) {
    return { cmd: 'python3', args: ['-m', 'claude_code_wrapped', ...args] };
  }

  // No executor found
  console.error('claude-code-wrapped requires Python 3.12+ and one of: uvx, pipx, or pip');
  console.error('');
  console.error('Recommended: Install uv (https://docs.astral.sh/uv/) then run:');
  console.error('  uvx claude-code-wrapped');
  console.error('');
  console.error('Or install with pip:');
  console.error('  pip install claude-code-wrapped');
  console.error('  claude-code-wrapped');
  process.exit(1);
}

const executor = findExecutor();
const child = spawn(executor.cmd, executor.args, {
  stdio: 'inherit',
  env: process.env
});

child.on('close', (code) => {
  process.exit(code || 0);
});

child.on('error', (err) => {
  console.error('Failed to start:', err.message);
  process.exit(1);
});
