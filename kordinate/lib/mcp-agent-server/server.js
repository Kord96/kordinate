#!/usr/bin/env node
// Beorn — shape-shifting MCP agent server.
//
// A single pod that can become any kordinate agent on demand.
// Loads the target agent's identity (IDENTITY.md) and memory, invokes
// Claude Code as that agent via --print, returns the response.
//
// MCP tools: delegate, kord, status
// MCP endpoint: POST|GET|DELETE /mcp
// Health:       GET /health

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import { spawn, execSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync } from 'node:fs';
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

// ─── Git worktree lifecycle ───

const KORD_WORKTREE_ROOT = process.env.KORD_WORKTREE_ROOT || join(KORDINATE_HOME, '.worktrees');
const KORD_LOCK_DIR = join(KORDINATE_HOME, '.locks');

function createAgentWorktree(agent) {
  const id = `mem-${agent}-${randomUUID().slice(0, 8)}`;
  const path = join(KORD_WORKTREE_ROOT, id);
  const branch = `memory/${id}`;
  execSync(`git -C "${KORDINATE_HOME}" worktree add "${path}" -b "${branch}" HEAD`, {
    timeout: 30000,
    env: { ...process.env, HOME, KORDINATE_HOME },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  log(`WORKTREE created: ${id} (branch: ${branch})`);
  return { id, path, branch };
}

function mergeAgentWorktree(worktree) {
  const { id, path, branch } = worktree;
  try {
    // Check if worktree has changes
    const status = execSync(`git -C "${path}" status --porcelain`, { encoding: 'utf8', timeout: 10000 }).trim();
    if (!status) {
      log(`WORKTREE ${id}: no changes`);
      return true; // nothing to merge
    }
    // Commit changes
    execSync(`git -C "${path}" add -A`, { timeout: 10000 });
    execSync(`git -C "${path}" commit -m "memory: ${worktree.id}"`, { timeout: 10000, env: { ...process.env, GIT_AUTHOR_NAME: 'beorn', GIT_AUTHOR_EMAIL: 'beorn@kordinate', GIT_COMMITTER_NAME: 'beorn', GIT_COMMITTER_EMAIL: 'beorn@kordinate' } });
    // Try fast-forward merge with flock
    mkdirSync(KORD_LOCK_DIR, { recursive: true });
    execSync(`flock "${KORD_LOCK_DIR}/merge.lock" git -C "${KORDINATE_HOME}" merge --ff-only "${branch}"`, {
      timeout: 30000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    log(`WORKTREE ${id}: merged to main`);
    return true;
  } catch (e) {
    log(`WORKTREE ${id}: merge failed — ${e.message}. Branch preserved for /merge.`);
    return false;
  }
}

function cleanupAgentWorktree(worktree, merged) {
  const { id, path, branch } = worktree;
  try {
    execSync(`git -C "${KORDINATE_HOME}" worktree remove "${path}" --force`, { timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] });
    if (merged) {
      execSync(`git -C "${KORDINATE_HOME}" branch -d "${branch}"`, { timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] });
    }
    log(`WORKTREE ${id}: cleaned up (merged: ${merged})`);
  } catch (e) {
    log(`WORKTREE ${id}: cleanup error — ${e.message}`);
  }
}

async function invokeAgent(agent, prompt) {
  log(`INVOKE ${agent}: ${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}`);
  const start = Date.now();

  const worktree = createAgentWorktree(agent);

  try {
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

    const result = await new Promise((resolve, reject) => {
      const child = spawn('claude', args, {
        cwd: REPO_ROOT,
        env: { ...process.env, HOME, KORDINATE_HOME: worktree.path },
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
    const merged = mergeAgentWorktree(worktree);
    cleanupAgentWorktree(worktree, merged);
  }
}

// ─── Contract helpers ───

function parseContractFrontmatter(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split('\n')) {
    const idx = line.indexOf(':');
    if (idx > 0) fm[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
  }
  return fm;
}

function extractGuidelines(raw) {
  const idx = raw.indexOf('## Provider Guidelines');
  return idx >= 0 ? raw.slice(idx + '## Provider Guidelines'.length).trim() : '';
}

function checkExpiry(kordDir) {
  const expiryScript = join(kordDir, 'expiry.sh');
  if (!existsSync(expiryScript)) return false; // no expiry = stale
  try {
    execSync(`bash "${expiryScript}"`, {
      cwd: kordDir,
      timeout: 10000,
      env: { ...process.env, HOME, KORDINATE_HOME },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return true; // exit 0 = fresh
  } catch {
    return false; // exit 1 = stale
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

  server.tool(
    'kord',
    'Route a stateful request through a kord contract. Handles contract lookup, cache/expiry checking, agent spawning, and result caching.',
    {
      kord_name: z.string().describe('The kord contract name (e.g., deployer-default, pattern-review)'),
      message: z.string().describe('The message/question to send to the provider'),
    },
    async ({ kord_name, message }) => {
      log(`TOOL kord called`, { kord_name, message: message.substring(0, 100) });
      const kordDir = join(KORDINATE_HOME, 'kords', kord_name);
      const contractPath = join(kordDir, 'contract.md');

      if (!existsSync(contractPath)) {
        throw new Error(`Kord not found: ${kord_name} (looked in ${contractPath})`);
      }

      const raw = readFileSync(contractPath, 'utf8');
      const fm = parseContractFrontmatter(raw);
      const provider = fm.provider;

      if (!provider) {
        throw new Error(`Kord ${kord_name} has no provider in frontmatter`);
      }

      // Check cache freshness
      const dataPath = join(kordDir, 'data.md');
      if (checkExpiry(kordDir) && existsSync(dataPath)) {
        const cached = readFileSync(dataPath, 'utf8');
        log(`TOOL kord cache hit`, { kord_name, cachedLen: cached.length });
        return { content: [{ type: 'text', text: `[cached]\n\n${cached}` }] };
      }

      // Stale or no cache — spawn agent
      const guidelines = extractGuidelines(raw);
      const fullPrompt = guidelines
        ? `${guidelines}\n\n---\n\n${message}`
        : message;

      log(`TOOL kord spawning`, { kord_name, provider });
      const response = await invokeAgent(provider, fullPrompt);

      // Cache result
      try {
        writeFileSync(dataPath, response);
        writeFileSync(join(kordDir, '.valid'), new Date().toISOString());
        log(`TOOL kord cached`, { kord_name, responseLen: response.length });
      } catch (e) {
        log(`TOOL kord cache write failed`, { kord_name, error: e.message });
      }

      return { content: [{ type: 'text', text: response }] };
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

// Prune stale worktrees every 5 minutes
setInterval(() => {
  try {
    execSync(`git -C "${KORDINATE_HOME}" worktree prune`, { timeout: 10000, stdio: 'ignore' });
  } catch { /* best-effort */ }
}, 300000);
