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
import { readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync, statSync } from 'node:fs';
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

// Agent MEMORY.md is maintained by Scribe (via /onboard and /kord remember).
// No spawn-time regeneration needed — the index is always current.

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

function parseCacheInputPaths(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return [];
  const fm = match[1];
  if (!fm.includes('cache_inputs:')) return [];
  const paths = [];
  let inPaths = false;
  for (const line of fm.split('\n')) {
    const s = line.trim();
    if (s === 'paths:') { inPaths = true; continue; }
    if (inPaths) {
      if (s.startsWith('- ')) {
        paths.push(join(KORDINATE_HOME, s.slice(2).trim()));
      } else if (s && !s.startsWith('-')) {
        inPaths = false;
      }
    }
  }
  return paths;
}

function extractGuidelines(raw) {
  const idx = raw.indexOf('## Provider Guidelines');
  return idx >= 0 ? raw.slice(idx + '## Provider Guidelines'.length).trim() : '';
}

function findKordDir(kordName) {
  // Search across all agents/*/kords/ directories
  const agentsDir = join(KORDINATE_HOME, 'agents');
  try {
    const agents = readdirSync(agentsDir, { withFileTypes: true })
      .filter(d => d.isDirectory());
    for (const agent of agents) {
      const candidate = join(agentsDir, agent.name, 'kords', kordName);
      if (existsSync(join(candidate, 'contract.md'))) {
        return { dir: candidate, provider: agent.name };
      }
    }
  } catch { /* fall through */ }
  return null;
}

function checkExpiry(kordDir) {
  const expiryScript = join(kordDir, 'expiry.sh');
  if (!existsSync(expiryScript)) return 'stale';
  try {
    execSync(`bash "${expiryScript}"`, {
      cwd: kordDir,
      timeout: 10000,
      env: { ...process.env, HOME, KORDINATE_HOME },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return 'fresh';  // exit 0
  } catch (e) {
    if (e.status === 2) return 'uncertain';  // exit 2
    return 'stale';  // exit 1
  }
}

function runCacheReview(kordDir, provider) {
  // Read the review.md template
  const reviewPath = join(kordDir, 'review.md');
  if (!existsSync(reviewPath)) return 'STALE';

  let template = readFileSync(reviewPath, 'utf8');
  // Strip frontmatter
  template = template.replace(/^---\n[\s\S]*?\n---\n?/, '');

  // Compute changed files: files newer than .snapshot (or .hash for compat)
  const snapshotFile = join(kordDir, '.snapshot');
  const hashFile = join(kordDir, '.hash');
  const referenceFile = existsSync(snapshotFile) ? snapshotFile : hashFile;
  let changedFiles = '';
  if (existsSync(referenceFile)) {
    try {
      // Read contract to find cache input paths from frontmatter
      const contractPath = join(kordDir, 'contract.md');
      const contractRaw = existsSync(contractPath) ? readFileSync(contractPath, 'utf8') : '';
      const inputPaths = parseCacheInputPaths(contractRaw).filter(p => existsSync(p));
      if (inputPaths.length > 0) {
        const dirs = inputPaths.map(p => `"${p}"`).join(' ');
        changedFiles = execSync(
          `find ${dirs} -newer "${referenceFile}" -type f 2>/dev/null | head -50`,
          { timeout: 5000, env: { ...process.env, HOME, KORDINATE_HOME } },
        ).toString().trim();
      }
    } catch { /* best-effort */ }
  }
  if (!changedFiles) changedFiles = '(unable to determine changed files)';

  // Read cached data
  const dataPath = join(kordDir, 'data.md');
  const cachedData = existsSync(dataPath) ? readFileSync(dataPath, 'utf8') : '';

  // Fill template placeholders
  const prompt = template
    .replace('{{DIFF}}', changedFiles)
    .replace('{{CACHED_DATA}}', cachedData);

  // Invoke the provider agent with the review prompt (lightweight)
  try {
    const result = execSync(
      `claude --print --dangerously-skip-permissions ${JSON.stringify(prompt)}`,
      {
        cwd: REPO_ROOT,
        timeout: 60000,
        env: { ...process.env, HOME, KORDINATE_HOME },
        stdio: ['ignore', 'pipe', 'pipe'],
      },
    ).toString().trim();

    const firstLine = result.split('\n')[0].trim().toUpperCase();
    return firstLine.startsWith('VALID') ? 'VALID' : 'STALE';
  } catch {
    return 'STALE';  // review failed → treat as stale
  }
}

function updateHash(kordDir) {
  // Re-run cache_store to update the hash after a VALID review
  try {
    execSync(`bash -c 'source "$KORDINATE_HOME/lib/cache.sh" && cache_store "${join(kordDir, '.hash')}"'`, {
      cwd: kordDir,
      timeout: 5000,
      env: { ...process.env, HOME, KORDINATE_HOME },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch { /* best-effort */ }

  // Also update the snapshot for magnitude-based expiry
  updateSnapshot(kordDir);
}

function updateSnapshot(kordDir) {
  try {
    const contractPath = join(kordDir, 'contract.md');
    if (!existsSync(contractPath)) return;
    const contractRaw = readFileSync(contractPath, 'utf8');
    const inputPaths = parseCacheInputPaths(contractRaw);
    if (inputPaths.length === 0) return;

    const snapshotFile = join(kordDir, '.snapshot');
    const pathArgs = inputPaths.map(p => `"${p}"`).join(' ');
    execSync(
      `bash -c 'source "$KORDINATE_HOME/lib/cache.sh" && cache_snapshot "${snapshotFile}" ${pathArgs}'`,
      {
        cwd: kordDir,
        timeout: 10000,
        env: { ...process.env, HOME, KORDINATE_HOME },
        stdio: ['ignore', 'pipe', 'pipe'],
      },
    );
  } catch (e) {
    log(`Snapshot update failed for ${kordDir}: ${e.message}`);
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
      const found = findKordDir(kord_name);

      if (!found) {
        throw new Error(`Kord not found: ${kord_name} (searched agents/*/kords/)`);
      }

      const { dir: kordDir, provider } = found;
      const contractPath = join(kordDir, 'contract.md');
      const raw = readFileSync(contractPath, 'utf8');
      const dataPath = join(kordDir, 'data.md');

      // Check cache freshness — three states
      const expiryState = checkExpiry(kordDir);

      if (expiryState === 'fresh' && existsSync(dataPath)) {
        const cached = readFileSync(dataPath, 'utf8');
        log(`TOOL kord cache hit`, { kord_name, cachedLen: cached.length });
        return { content: [{ type: 'text', text: `[cached]\n\n${cached}` }] };
      }

      if (expiryState === 'uncertain') {
        // Stage 2: lightweight agent review
        log(`TOOL kord uncertain`, { kord_name, provider });
        const verdict = runCacheReview(kordDir, provider);
        log(`TOOL kord review verdict`, { kord_name, verdict });

        if (verdict === 'VALID') {
          updateHash(kordDir);
          const cached = readFileSync(dataPath, 'utf8');
          log(`TOOL kord cache revalidated`, { kord_name, cachedLen: cached.length });
          return { content: [{ type: 'text', text: `[cached:revalidated]\n\n${cached}` }] };
        }
        // verdict is STALE — fall through to full regeneration
        log(`TOOL kord review stale, regenerating`, { kord_name });
      }

      // Stale or review-stale — spawn agent for full regeneration
      const guidelines = extractGuidelines(raw);
      const fullPrompt = guidelines
        ? `${guidelines}\n\n---\n\n${message}`
        : message;

      log(`TOOL kord spawning`, { kord_name, provider });
      const response = await invokeAgent(provider, fullPrompt);

      // Cache result and snapshot inputs
      try {
        writeFileSync(dataPath, response);
        writeFileSync(join(kordDir, '.valid'), new Date().toISOString());
        updateSnapshot(kordDir);
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
