#!/usr/bin/env node
// Beorn — shape-shifting MCP agent server.
//
// A single pod that can become any kordinate agent on demand.
// Loads the target agent's identity (CLAUDE.md) and memory, invokes
// Claude Code as that agent via --print, returns the response.
//
// MCP tools: delegate, status
// MCP endpoint: POST|GET|DELETE /mcp
// Health:       GET /health

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import { spawn, execSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3100');
const HOME = process.env.HOME || '/home/claude';
const KORDINATE_HOME = process.env.KORDINATE_HOME || join(HOME, 'kordinate', 'kordinate');
const REPO_ROOT = join(KORDINATE_HOME, '..');
const BOOT_TIME = new Date().toISOString();

// ─── Discover agents from registry.yaml ───

function loadAgentNames() {
  try {
    const content = readFileSync(join(KORDINATE_HOME, 'agents', 'registry.yaml'), 'utf8');
    const agentBlock = content.split(/^beorn:/m)[0];
    return [...agentBlock.matchAll(/^  (\w+):$/gm)].map(m => m[1]);
  } catch {
    return ['deployer', 'sauron', 'designer', 'scribe'];
  }
}

const KNOWN_AGENTS = loadAgentNames();
const activeRequests = new Map();

// ─── Agent helpers ───

function regenerateMemory(agent) {
  const hookScript = join(KORDINATE_HOME, 'hooks', 'agent-memory.sh');
  if (!existsSync(hookScript)) return;

  const hookInput = JSON.stringify({
    tool_name: 'Agent',
    tool_input: { subagent_type: agent },
  });
  try {
    execSync(
      `printf '%s' ${JSON.stringify(hookInput)} | bash "${hookScript}"`,
      {
        cwd: KORDINATE_HOME,
        timeout: 30000,
        env: { ...process.env, HOME, KORDINATE_HOME },
        stdio: ['pipe', 'pipe', 'pipe'],
      },
    );
  } catch (e) {
    console.error(`[beorn] Memory regen failed for ${agent}: ${e.stderr?.toString() || e.message}`);
  }
}

function loadSystemPrompt(agent) {
  const parts = [];

  const claudeMd = join(HOME, '.claude', 'agents', agent, 'CLAUDE.md');
  if (existsSync(claudeMd)) {
    const raw = readFileSync(claudeMd, 'utf8');
    parts.push(raw.replace(/^---\n[\s\S]*?\n---\n?/, ''));
  }

  const memoryMd = join(KORDINATE_HOME, 'agents', agent, 'memory', 'dynamic', 'MEMORY.md');
  if (existsSync(memoryMd)) {
    parts.push(readFileSync(memoryMd, 'utf8'));
  }

  return parts.join('\n\n');
}

function cleanGitState() {
  try {
    execSync('git checkout . 2>/dev/null; git clean -fd 2>/dev/null', {
      cwd: REPO_ROOT,
      timeout: 10000,
    });
  } catch { /* best-effort */ }
}

async function invokeAgent(agent, prompt) {
  log(`INVOKE ${agent}: ${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}`);
  const start = Date.now();

  log(`INVOKE ${agent}: regenerating memory...`);
  regenerateMemory(agent);

  log(`INVOKE ${agent}: loading system prompt...`);
  const systemPrompt = loadSystemPrompt(agent);
  log(`INVOKE ${agent}: system prompt ${systemPrompt ? systemPrompt.length + ' chars' : 'empty'}`);

  const args = ['--print', '--dangerously-skip-permissions'];
  if (systemPrompt) {
    args.push('--system-prompt', systemPrompt);
  }
  args.push(prompt);

  log(`INVOKE ${agent}: spawning claude --print (${args.length} args)...`);

  try {
    const result = await new Promise((resolve, reject) => {
      const child = spawn('claude', args, {
        cwd: REPO_ROOT,
        env: { ...process.env, HOME },
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: true, // survive parent shell exit
      });

      let stdout = '';
      let stderr = '';
      child.stdout.on('data', (d) => { stdout += d; });
      child.stderr.on('data', (d) => { stderr += d; });

      const timer = setTimeout(() => {
        child.kill('SIGTERM');
        reject(new Error(`Timed out after 300s`));
      }, 300000);

      child.on('close', (code) => {
        clearTimeout(timer);
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          const err = new Error(`claude exited with code ${code}`);
          err.stdout = stdout;
          err.stderr = stderr;
          reject(err);
        }
      });

      child.on('error', (e) => {
        clearTimeout(timer);
        reject(e);
      });

      // Don't let the child prevent Node from exiting when server shuts down
      child.unref();
    });

    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE ${agent}: done in ${elapsed}s, response ${result.stdout.length} chars`);
    if (result.stderr) log(`INVOKE ${agent}: stderr: ${result.stderr.substring(0, 200)}`);
    return result.stdout.trim();
  } catch (e) {
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE ${agent}: FAILED after ${elapsed}s — ${e.message}`);
    if (e.stderr) log(`INVOKE ${agent}: stderr: ${e.stderr.substring(0, 500)}`);
    if (e.stdout) log(`INVOKE ${agent}: stdout: ${e.stdout.substring(0, 500)}`);
    throw e;
  } finally {
    cleanGitState();
  }
}

// ─── MCP tool registration ───

function registerTools(server) {
  server.tool(
    'delegate',
    'Delegate a prompt to a kordinate agent. Beorn loads the agent identity, invokes Claude Code as that agent, and returns the response.',
    {
      agent: z.enum(KNOWN_AGENTS).describe('The agent to invoke (deployer, sauron, designer, scribe)'),
      prompt: z.string().describe('The prompt to send to the agent'),
    },
    async ({ agent, prompt }) => {
      log(`TOOL delegate called`, { agent, prompt: prompt.substring(0, 100) });
      const requestId = `${agent}-${Date.now()}`;
      activeRequests.set(requestId, { agent, startedAt: new Date().toISOString() });
      try {
        const response = await invokeAgent(agent, prompt);
        log(`TOOL delegate done`, { agent, responseLen: response.length });
        return { content: [{ type: 'text', text: response }] };
      } catch (e) {
        log(`TOOL delegate error`, { agent, error: e.message });
        throw e;
      } finally {
        activeRequests.delete(requestId);
      }
    },
  );

  server.tool(
    'status',
    'Return the current status of the beorn server — uptime, known agents, active requests.',
    {},
    async () => {
      log('TOOL status called');
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            name: 'beorn',
            boot: BOOT_TIME,
            agents: KNOWN_AGENTS,
            active: [...activeRequests.values()],
          }, null, 2),
        }],
      };
    },
  );
}

// ─── Logging ───

function log(msg, data) {
  const ts = new Date().toISOString().slice(11, 23);
  if (data) {
    console.log(`[beorn ${ts}] ${msg}`, JSON.stringify(data));
  } else {
    console.log(`[beorn ${ts}] ${msg}`);
  }
}

// ─── Express app ───

const app = express();
app.use(express.json({ limit: '1mb' }));

// Request logging middleware
app.use((req, _res, next) => {
  if (req.path !== '/health') {
    const body = req.body;
    const method = body?.method || body?.params?.name || '-';
    log(`${req.method} ${req.path} method=${method} session=${req.headers['mcp-session-id'] || 'none'}`);
  }
  next();
});

// Health — K8s readiness probe
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'beorn', boot: BOOT_TIME });
});

// ─── MCP transport ───
// Stateless: each request gets its own server + transport.
// No session persistence needed — each call is independent.

app.post('/mcp', async (req, res) => {
  const method = req.body?.method || 'unknown';
  log(`MCP request: ${method}`);

  try {
    const server = new McpServer({ name: 'beorn', version: '1.0.0' });
    registerTools(server);

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined, // stateless — no sessions
    });

    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
    log(`MCP response sent: ${method}`);
  } catch (e) {
    log(`MCP error: ${method} — ${e.message}`);
    if (!res.headersSent) {
      res.status(500).json({ jsonrpc: '2.0', error: { code: -32603, message: e.message }, id: null });
    }
  }
});

// ─── Start ───

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[beorn] Shape-shifting MCP agent server on :${PORT}`);
  console.log(`[beorn] Known agents: ${KNOWN_AGENTS.join(', ')}`);
  console.log(`[beorn] MCP: /mcp | Health: /health`);
});
