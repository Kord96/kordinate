#!/usr/bin/env node
// Beorn — shape-shifting MCP agent server.
//
// A single pod that can become any kordinate agent on demand.
// Loads the target agent's identity (IDENTITY.md) and memory, invokes
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
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3100');
const HOME = process.env.HOME || '/home/claude';
const KORDINATE_HOME = process.env.KORDINATE_HOME || join(HOME, '.kord');
const REPO_ROOT = process.env.REPO_ROOT || join(HOME, 'kordinate');
const BOOT_TIME = new Date().toISOString();

// ─── Discover agents from KORD.json or agents/ directory ───

function loadAgentNames() {
  // Try KORD.json first — it lists all agents with IDENTITY.md entries
  try {
    const kordPath = join(KORDINATE_HOME, 'KORD.json');
    if (existsSync(kordPath)) {
      const entries = JSON.parse(readFileSync(kordPath, 'utf8'));
      const names = entries
        .filter(e => e.path.match(/^agents\/[^/]+\/IDENTITY\.md$/))
        .map(e => e.path.split('/')[1]);
      if (names.length > 0) return names;
    }
  } catch { /* fall through */ }

  // Fallback: scan agents/ directory for dirs containing IDENTITY.md
  try {
    const agentsDir = join(KORDINATE_HOME, 'agents');
    return readdirSync(agentsDir, { withFileTypes: true })
      .filter(d => d.isDirectory() && existsSync(join(agentsDir, d.name, 'IDENTITY.md')))
      .map(d => d.name);
  } catch { /* fall through */ }

  return ['deployer', 'sauron', 'designer', 'scribe'];
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

  // Load agent identity from $KORDINATE_HOME/agents/<name>/IDENTITY.md
  const identityMd = join(KORDINATE_HOME, 'agents', agent, 'IDENTITY.md');
  if (existsSync(identityMd)) {
    const raw = readFileSync(identityMd, 'utf8');
    parts.push(raw.replace(/^---\n[\s\S]*?\n---\n?/, ''));
  }

  // Load all memory files from $KORDINATE_HOME/agents/<name>/memory/
  const memoryDir = join(KORDINATE_HOME, 'agents', agent, 'memory');
  if (existsSync(memoryDir)) {
    try {
      const files = readdirSync(memoryDir).filter(f => f.endsWith('.md')).sort();
      for (const file of files) {
        const content = readFileSync(join(memoryDir, file), 'utf8').trim();
        if (content) parts.push(content);
      }
    } catch { /* best-effort */ }
  }

  return parts.join('\n\n');
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
