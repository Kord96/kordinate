#!/usr/bin/env node
// Job Router — HTTP/MCP frontend that publishes jobs to Kafka.
//
// Replaces the old MCP agent server (Beorn). Keeps:
// - Route registry from KORD.json
// - Resource registry and cache logic
// - MCP tool registration (backward-compatible with workstation)
// - Script route handling (runs locally, no agent needed)
//
// Replaces:
// - All spawnClaude/invokeFull/invokeLightweight → Kafka publish + wait
// - Gate secret management → removed (agents are pods, not subagents)
// - Auth delegation → removed

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import yaml from 'js-yaml';
import { Kafka } from 'kafkajs';
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, readdirSync, statSync, mkdirSync, watch } from 'node:fs';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3100');
const HOME = process.env.HOME || '/home/claude';
const KORDINATE_HOME = process.env.KORDINATE_HOME || join(HOME, '.kord');
const CACHE_DIR = join(KORDINATE_HOME, 'cache');
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka.dev.svc.cluster.local:9092').split(',');
const BOOT_TIME = new Date().toISOString();
const DEFAULT_TIMEOUT_MS = 900_000;

const TRACKED_EXTS = new Set(['.md', '.yaml', '.yml', '.json', '.sh', '.js']);

// ─── Kafka ───

const kafka = new Kafka({
  clientId: 'job-router',
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const producer = kafka.producer();
const resultConsumer = kafka.consumer({ groupId: 'job-router-results' });

// Pending results: correlationId → { resolve, reject, timer }
const pendingResults = new Map();

async function publishJob(agent, prompt, opts = {}) {
  const correlationId = randomUUID();
  const job = {
    id: randomUUID(),
    agent,
    skill: opts.skill || null,
    prompt,
    correlation_id: correlationId,
    created_at: new Date().toISOString(),
    timeout_ms: opts.timeoutMs || DEFAULT_TIMEOUT_MS,
    mode: opts.mode || 'full',
    metadata: opts.metadata || {},
  };

  await producer.send({
    topic: `jobs.${agent}`,
    messages: [{ key: correlationId, value: JSON.stringify(job) }],
  });

  log(`JOB published to jobs.${agent}`, { correlation_id: correlationId, skill: opts.skill });
  return correlationId;
}

function waitForResult(correlationId, timeoutMs = DEFAULT_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pendingResults.delete(correlationId);
      reject(new Error(`Job timed out after ${timeoutMs}ms`));
    }, timeoutMs + 5000); // small buffer beyond agent timeout

    pendingResults.set(correlationId, { resolve, reject, timer });
  });
}

async function submitAndWait(agent, prompt, opts = {}) {
  const correlationId = await publishJob(agent, prompt, opts);
  const result = await waitForResult(correlationId, opts.timeoutMs || DEFAULT_TIMEOUT_MS);
  if (result.status === 'error' || result.status === 'timeout') {
    throw new Error(`Agent ${agent} ${result.status}: ${result.output}`);
  }
  return result.output;
}

// ─── Route registry ───

function loadRouteRegistry() {
  const registry = new Map();
  const kordJsonPath = join(KORDINATE_HOME, 'KORD.json');
  if (!existsSync(kordJsonPath)) { log('WARN: KORD.json not found'); return registry; }

  try {
    const entries = JSON.parse(readFileSync(kordJsonPath, 'utf8'));
    for (const entry of entries) {
      if (entry.type !== 'skill' || !entry.public) continue;
      if (!entry.name || !entry.agent) continue;
      const routeName = entry.agent === 'team'
        ? entry.name
        : `${entry.agent}_${entry.name}`.replace(/-/g, '_');
      if (registry.has(routeName)) continue;
      registry.set(routeName, {
        name: routeName, method: 'POST', description: entry.description,
        provider: entry.agent, skill: entry.name,
        arguments: entry.arguments, handler: entry.handler || null,
        registryPath: entry.registry || null,
        cache: entry.cache || null, guidelines: entry.guidelines || null,
      });
    }
    log(`Loaded ${registry.size} routes`);
  } catch (e) { log(`WARN: KORD.json parse error: ${e.message}`); }
  return registry;
}

function loadResourceRegistry() {
  const registry = new Map();
  const kordJsonPath = join(KORDINATE_HOME, 'KORD.json');
  if (!existsSync(kordJsonPath)) return registry;
  try {
    const entries = JSON.parse(readFileSync(kordJsonPath, 'utf8'));
    for (const entry of entries) {
      if (entry.type !== 'resource') continue;
      if (!entry.name || !entry.agent) continue;
      if (!registry.has(entry.agent)) registry.set(entry.agent, []);
      registry.get(entry.agent).push(entry);
    }
  } catch (e) { log(`WARN: resource load error: ${e.message}`); }
  return registry;
}

function getKnownAgents(registry) {
  const agents = new Set();
  for (const route of registry.values()) agents.add(route.provider);
  try {
    const agentsDir = join(KORDINATE_HOME, 'agents');
    for (const d of readdirSync(agentsDir, { withFileTypes: true })) {
      if (d.isDirectory() && existsSync(join(agentsDir, d.name, 'IDENTITY.md'))) agents.add(d.name);
    }
  } catch {}
  agents.delete('main'); // main is removed
  return [...agents].sort();
}

let routeRegistry = loadRouteRegistry();
let resourceRegistry = loadResourceRegistry();
let KNOWN_AGENTS = getKnownAgents(routeRegistry);

// Watch KORD.json for changes
const kordJsonPath = join(KORDINATE_HOME, 'KORD.json');
if (existsSync(kordJsonPath)) {
  let reloadTimeout;
  watch(kordJsonPath, () => {
    clearTimeout(reloadTimeout);
    reloadTimeout = setTimeout(() => {
      routeRegistry = loadRouteRegistry();
      resourceRegistry = loadResourceRegistry();
      KNOWN_AGENTS = getKnownAgents(routeRegistry);
    }, 500);
  });
}

// ─── Cache helpers (kept from original server.js) ───

function getCacheDir(routeName) { return join(CACHE_DIR, routeName); }
function ensureCacheDir(routeName) { const d = getCacheDir(routeName); if (!existsSync(d)) mkdirSync(d, { recursive: true }); return d; }
function parseDuration(str) { if (!str) return 0; const m = String(str).match(/^(\d+)(s|m|h|d)$/); if (!m) return 604800; const n = parseInt(m[1]); return { s: n, m: n*60, h: n*3600, d: n*86400 }[m[2]] || 604800; }
function md5(content) { return createHash('md5').update(content).digest('hex'); }
function computeETag(data) { return `"${md5(data)}"`; }

function collectFiles(inputs) {
  const files = [];
  for (const input of inputs) {
    const absPath = join(KORDINATE_HOME, input);
    try {
      const stat = statSync(absPath);
      if (stat.isDirectory()) walkDir(absPath, files);
      else if (stat.isFile() && TRACKED_EXTS.has(extname(absPath))) files.push(absPath);
    } catch {}
  }
  return files.sort();
}

function walkDir(dir, out) {
  try {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) walkDir(full, out);
      else if (entry.isFile() && TRACKED_EXTS.has(extname(entry.name))) out.push(full);
    }
  } catch {}
}

function readSnapshot(path) {
  const snap = new Map();
  if (!existsSync(path)) return snap;
  try {
    for (const line of readFileSync(path, 'utf8').split('\n')) {
      if (!line.trim()) continue;
      const parts = line.split(/\s+/);
      if (parts.length >= 3) snap.set(parts.slice(2).join(' '), { lines: parseInt(parts[0]), hash: parts[1] });
    }
  } catch {}
  return snap;
}

function writeSnapshot(snapshotPath, inputs) {
  const files = collectFiles(inputs);
  const lines = [];
  for (const file of files) {
    try {
      const content = readFileSync(file, 'utf8');
      lines.push(`${content.split('\n').length} ${md5(content)} ${file}`);
    } catch {}
  }
  writeFileSync(snapshotPath, lines.join('\n') + '\n');
}

function checkCacheExpiry(route, cacheDir) {
  const cache = route.cache;
  if (!cache) return 'stale';
  const dataPath = join(cacheDir, 'data.md');
  if (!existsSync(dataPath)) return 'stale';

  const maxAgeSeconds = parseDuration(cache.max_age);
  if (maxAgeSeconds > 0) {
    try { if ((Date.now() - statSync(dataPath).mtimeMs) / 1000 >= maxAgeSeconds) return 'stale'; } catch { return 'stale'; }
  }

  if (cache.type === 'hash' && cache.inputs) {
    const files = collectFiles(cache.inputs);
    const allContent = files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('');
    const currentHash = md5(allContent);
    try { return readFileSync(join(cacheDir, '.hash'), 'utf8').trim() === currentHash ? 'fresh' : 'stale'; } catch { return 'stale'; }
  }

  if (!cache.inputs) return 'fresh';
  const snapshot = readSnapshot(join(cacheDir, '.snapshot'));
  if (snapshot.size === 0) return 'uncertain';

  const threshold = cache.threshold ?? 0.05;
  const staleThreshold = cache.stale_threshold ?? 0.30;
  const currentFiles = collectFiles(cache.inputs);
  let totalLines = 0, changedLines = 0;

  for (const [path, { lines: oldLines, hash: oldHash }] of snapshot) {
    totalLines += oldLines;
    try {
      const content = readFileSync(path, 'utf8');
      if (md5(content) !== oldHash) { const diff = Math.abs(content.split('\n').length - oldLines); changedLines += diff > 0 ? diff : 1; }
    } catch { changedLines += oldLines; }
  }
  for (const file of currentFiles) {
    if (!snapshot.has(file)) { try { changedLines += readFileSync(file, 'utf8').split('\n').length; } catch {} }
  }

  if (totalLines === 0) totalLines = 1;
  const changeRatio = changedLines / totalLines;
  const ageRatio = Math.min((Date.now() - statSync(join(cacheDir, 'data.md')).mtimeMs) / 1000 / (maxAgeSeconds || 1), 1.0);
  const score = changeRatio + (ageRatio * changeRatio);

  if (score < threshold) return 'fresh';
  if (score > staleThreshold) return 'stale';
  return 'uncertain';
}

async function runCacheReview(route, cacheDir) {
  const dataPath = join(cacheDir, 'data.md');
  const snapshotPath = join(cacheDir, '.snapshot');
  let diff = 'No diff available.';
  try {
    const snapshot = readSnapshot(snapshotPath);
    const changed = [];
    for (const [path, { hash }] of snapshot) {
      try { if (md5(readFileSync(path, 'utf8')) !== hash) changed.push(`Changed: ${path}`); } catch { changed.push(`Deleted: ${path}`); }
    }
    if (changed.length) diff = changed.join('\n');
  } catch {}

  const cachedData = existsSync(dataPath) ? readFileSync(dataPath, 'utf8').substring(0, 2000) : 'No cached data.';
  const reviewPrompt = `You are reviewing whether your cached response is still valid.\n\n## Changed Inputs\n\n${diff}\n\n## Cached Response\n\n${cachedData}\n\nRespond with ONLY \`VALID\` or \`STALE\` on the first line, followed by a brief reason.`;

  try {
    const response = await submitAndWait(route.provider, reviewPrompt, { mode: 'lightweight', timeoutMs: 60_000 });
    return response.split('\n')[0].trim().toUpperCase().startsWith('VALID') ? 'valid' : 'stale';
  } catch (e) {
    log(`Cache review failed for ${route.name}: ${e.message}`);
    return 'stale';
  }
}

// ─── Resource helpers ───

function resolveProjectPath(projectArg) {
  if (!projectArg) return null;
  if (projectArg.startsWith('/')) { if (existsSync(projectArg)) return projectArg; throw new Error(`Not found: ${projectArg}`); }
  for (const c of [join(HOME, projectArg), join(HOME, 'repos', projectArg)]) { if (existsSync(c)) return c; }
  throw new Error(`Project not found: ${projectArg}`);
}

function resolveResourcePath(entry, projectParam) {
  if (!entry.path) return null;
  if (entry.scope === 'project') return entry.path.replace('<project>', resolveProjectPath(projectParam));
  return join(KORDINATE_HOME, entry.path);
}

function readResourceContent(resolved, isDir, format) {
  if (isDir) {
    if (!existsSync(resolved)) return null;
    const files = readdirSync(resolved).filter(f => {
      if (format === 'yaml') return f.endsWith('.yaml') || f.endsWith('.yml');
      if (format === 'json') return f.endsWith('.json');
      if (format === 'md') return f.endsWith('.md');
      return true;
    }).sort();
    if (!files.length) return null;
    return files.map(f => `--- ${f} ---\n${readFileSync(join(resolved, f), 'utf8')}`).join('\n\n');
  }
  if (!existsSync(resolved)) return null;
  return readFileSync(resolved, 'utf8');
}

async function handleResourceGet(entry, projectParam, ifNoneMatch) {
  if (entry.path) {
    const resolved = resolveResourcePath(entry, projectParam);
    const isDir = entry.path.endsWith('/');
    const content = readResourceContent(resolved, isDir, entry.format);
    if (content) {
      const etag = computeETag(content);
      if (ifNoneMatch && ifNoneMatch === etag) return { text: '[304 not modified]', etag, status: 304 };
      return { text: content, etag, status: 200 };
    }
    if (entry.produced_by) {
      await submitAndWait(entry.agent, `Run the /${entry.produced_by} skill. Input: ${projectParam || ''}`);
      const newContent = readResourceContent(resolved, isDir, entry.format);
      if (newContent) return { text: newContent, etag: computeETag(newContent), status: 200 };
    }
    return { text: `Resource not found: ${entry.name}`, status: 404 };
  }
  if (entry.guidelines) {
    const cacheKey = `resource/${entry.agent}/${entry.name}`;
    if (entry.cache) {
      const cacheDir = ensureCacheDir(cacheKey);
      const dataPath = join(cacheDir, 'data.md');
      const syntheticRoute = { name: cacheKey, cache: entry.cache, provider: entry.agent };
      const expiry = checkCacheExpiry(syntheticRoute, cacheDir);
      if (expiry === 'fresh' && existsSync(dataPath)) {
        const cached = readFileSync(dataPath, 'utf8');
        const etag = computeETag(cached);
        if (ifNoneMatch && ifNoneMatch === etag) return { text: '[304 not modified]', etag, status: 304 };
        return { text: `[cached]\n\n${cached}`, etag, status: 200 };
      }
      if (expiry === 'uncertain') {
        const reviewResult = await runCacheReview(syntheticRoute, cacheDir);
        if (reviewResult === 'valid') {
          if (entry.cache.inputs) writeSnapshot(join(cacheDir, '.snapshot'), entry.cache.inputs);
          writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
          const cached = readFileSync(dataPath, 'utf8');
          return { text: `[cached:revalidated]\n\n${cached}`, etag: computeETag(cached), status: 200 };
        }
      }
      const response = await submitAndWait(entry.agent, entry.guidelines, { mode: 'lightweight', timeoutMs: 120_000 });
      writeFileSync(dataPath, response);
      if (entry.cache.inputs) writeSnapshot(join(cacheDir, '.snapshot'), entry.cache.inputs);
      if (entry.cache.type === 'hash' && entry.cache.inputs) {
        const files = collectFiles(entry.cache.inputs);
        writeFileSync(join(cacheDir, '.hash'), md5(files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('')));
      }
      return { text: response, etag: computeETag(response), status: 200 };
    }
    const response = await submitAndWait(entry.agent, entry.guidelines, { mode: 'lightweight' });
    return { text: response, etag: computeETag(response), status: 200 };
  }
  return { text: `Resource "${entry.name}" has neither path nor guidelines`, status: 500 };
}

// ─── Script route handler (runs locally, no agent needed) ───

async function handleScriptRoute(route, message) {
  const dir = message.trim();
  if (!dir) return 'ERROR: No directory provided.';
  const registryFile = join(KORDINATE_HOME, route.registryPath);
  if (!existsSync(registryFile)) return `ERROR: Registry not found at ${registryFile}`;

  let registry;
  try { registry = yaml.load(readFileSync(registryFile, 'utf8')); } catch (e) { return `ERROR: ${e.message}`; }

  const match = (registry.validators || []).find(v => dir.includes(v.pattern));
  if (!match) return `NO_VALIDATOR: No validator for ${dir}. Proceed.`;

  const scriptPath = join(KORDINATE_HOME, match.script);
  if (!existsSync(scriptPath)) return `ERROR: Script not found at ${scriptPath}`;

  try {
    const result = execSync(`python3 "${scriptPath}" "${dir}"`, { cwd: KORDINATE_HOME, timeout: 60000, env: { ...process.env, HOME, KORDINATE_HOME }, stdio: ['pipe', 'pipe', 'pipe'] });
    const output = result.toString().trim();
    try {
      const token = execSync(`find "${dir}" -name "*.json" -o -name "*.yaml" | sort | xargs cat | sha256sum | cut -d' ' -f1`, { timeout: 10000, stdio: ['pipe', 'pipe', 'pipe'] }).toString().trim();
      return `${output}\n\nVALIDATED — token: ${token}\nInclude this token in your report.`;
    } catch { return `${output}\n\nVALID but token computation failed.`; }
  } catch (e) {
    const output = ((e.stdout?.toString() || '') + '\n' + (e.stderr?.toString() || '')).trim();
    return `VALIDATION FAILED\n\n${output}\n\nFix the errors and re-validate.`;
  }
}

// ─── Route handler ───

async function handleRoute(route, message, ifNoneMatch) {
  // Script-handled routes — run directly
  if (route.handler === 'script' && route.registryPath) {
    return { text: await handleScriptRoute(route, message), status: 200 };
  }

  // Non-cached routes — publish to Kafka
  if (!route.cache) {
    const prompt = route.guidelines
      ? `${route.guidelines}\n\n---\n\n${message}`
      : route.skill ? `Run the /${route.skill} skill. Input: ${message}` : message;

    const response = await submitAndWait(route.provider, prompt, { skill: route.skill });
    return { text: response, etag: computeETag(response), status: 200 };
  }

  // Cached routes
  const cacheDir = ensureCacheDir(route.name);
  const dataPath = join(cacheDir, 'data.md');
  const expiry = checkCacheExpiry(route, cacheDir);
  log(`ROUTE ${route.name}: cache=${expiry}`);

  if (expiry === 'fresh' && existsSync(dataPath)) {
    const cached = readFileSync(dataPath, 'utf8');
    const etag = computeETag(cached);
    if (ifNoneMatch && ifNoneMatch === etag) return { text: '[304 not modified]', etag, status: 304 };
    return { text: `[cached]\n\n${cached}`, etag, status: 200 };
  }

  if (expiry === 'uncertain') {
    const reviewResult = await runCacheReview(route, cacheDir);
    if (reviewResult === 'valid') {
      if (route.cache.inputs) writeSnapshot(join(cacheDir, '.snapshot'), route.cache.inputs);
      writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
      const cached = readFileSync(dataPath, 'utf8');
      return { text: `[cached:revalidated]\n\n${cached}`, etag: computeETag(cached), status: 200 };
    }
  }

  // Stale — publish to Kafka for regeneration
  const prompt = route.guidelines
    ? `${route.guidelines}\n\n---\n\n${message}`
    : route.skill ? `Run the /${route.skill} skill. Input: ${message}` : message;

  const response = await submitAndWait(route.provider, prompt, { skill: route.skill });

  try {
    writeFileSync(dataPath, response);
    writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
    if (route.cache.inputs) writeSnapshot(join(cacheDir, '.snapshot'), route.cache.inputs);
    if (route.cache.type === 'hash' && route.cache.inputs) {
      const files = collectFiles(route.cache.inputs);
      writeFileSync(join(cacheDir, '.hash'), md5(files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('')));
    }
  } catch (e) { log(`Cache write failed for ${route.name}: ${e.message}`); }

  return { text: response, etag: computeETag(response), status: 200 };
}

// ─── MCP tool registration ───

function registerTools(server) {
  // Delegate — publish job to Kafka and wait for result
  server.tool(
    'delegate',
    'Delegate a prompt to a kordinate agent. Publishes to Kafka and waits for the result.',
    {
      agent: z.enum(KNOWN_AGENTS).describe('The agent to invoke'),
      prompt: z.string().describe('The prompt to send'),
    },
    async ({ agent, prompt }) => {
      log('TOOL delegate', { agent, prompt: prompt.substring(0, 100) });

      // Check for script-handled routes first
      for (const [, route] of routeRegistry) {
        if (route.provider === agent && route.handler === 'script' && route.skill) {
          const skillPrefix = route.skill.replace(/-/g, '[ -]');
          const match = prompt.match(new RegExp(`^${skillPrefix}\\s+(.+)`, 'i'));
          if (match) {
            const result = await handleScriptRoute(route, match[1].trim());
            return { content: [{ type: 'text', text: result }] };
          }
        }
      }

      const response = await submitAndWait(agent, prompt);
      return { content: [{ type: 'text', text: response }] };
    },
  );

  // Status
  server.tool('status', 'Server status — uptime, agents, routes, pending jobs.', {}, async () => {
    const routes = [...routeRegistry.entries()].map(([name, r]) => ({ name, provider: r.provider, cached: !!r.cache }));
    const resources = {};
    for (const [agent, rs] of resourceRegistry) resources[agent] = rs.map(r => r.name);
    return {
      content: [{ type: 'text', text: JSON.stringify({
        name: 'kord-router', boot: BOOT_TIME, agents: KNOWN_AGENTS,
        routes, resources, pending_jobs: pendingResults.size,
      }, null, 2) }],
    };
  });

  // Dynamic per-route tools
  for (const [name, route] of routeRegistry) {
    const schema = { message: z.string().describe('The request message') };
    if (route.cache) schema.if_none_match = z.string().optional().describe('ETag for conditional requests');

    server.tool(name, route.description, schema, async (params) => {
      const result = await handleRoute(route, params.message, params.if_none_match);
      return { content: [{ type: 'text', text: result.etag ? `${result.text}\n\n<!-- etag: ${result.etag} -->` : result.text }] };
    });
  }

  // Resource catalog + get tools
  for (const [agent, resources] of resourceRegistry) {
    server.tool(`${agent}_resources`, `List ${agent} resources.`, {}, async () => {
      const items = resources.map(r => ({ name: r.name, description: r.description, scope: r.scope, format: r.format || null }));
      return { content: [{ type: 'text', text: JSON.stringify(items, null, 2) }] };
    });

    const resourceNames = resources.map(r => r.name);
    const hasProjectScoped = resources.some(r => r.scope === 'project');
    const getSchema = { resource: z.enum(resourceNames).describe('Which resource') };
    if (hasProjectScoped) getSchema.project = z.string().optional().describe('Project path for project-scoped resources');
    getSchema.if_none_match = z.string().optional().describe('ETag for conditional requests');

    server.tool(`${agent}_fetch`, `Retrieve a ${agent} resource.`, getSchema, async (params) => {
      const entry = resources.find(r => r.name === params.resource);
      if (!entry) throw new Error(`Unknown resource: ${params.resource}`);
      if (entry.scope === 'project' && !params.project) throw new Error(`Project-scoped — provide project`);
      const result = await handleResourceGet(entry, params.project, params.if_none_match);
      return { content: [{ type: 'text', text: result.etag ? `${result.text}\n\n<!-- etag: ${result.etag} -->` : result.text }] };
    });
  }
}

// ─── Logging ───

function log(msg, data) {
  const entry = { level: 'info', component: 'router', event: msg, timestamp: new Date().toISOString(), ...data };
  console.log(JSON.stringify(entry));
}

// ─── Express app ───

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'kord-router', boot: BOOT_TIME, routes: routeRegistry.size, pending: pendingResults.size });
});

app.post('/mcp', async (req, res) => {
  try {
    const server = new McpServer({ name: 'kord', version: '3.0.0' });
    registerTools(server);
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (e) {
    log('MCP error', { error: e.message });
    if (!res.headersSent) res.status(500).json({ jsonrpc: '2.0', error: { code: -32603, message: e.message }, id: null });
  }
});

// ─── Start ───

async function main() {
  await producer.connect();
  await resultConsumer.connect();
  await resultConsumer.subscribe({ topic: 'jobs.result', fromBeginning: false });

  // Listen for results and resolve pending promises
  await resultConsumer.run({
    eachMessage: async ({ message }) => {
      try {
        const result = JSON.parse(message.value.toString());
        const pending = pendingResults.get(result.correlation_id);
        if (pending) {
          clearTimeout(pending.timer);
          pendingResults.delete(result.correlation_id);
          pending.resolve(result);
        }
      } catch {}
    },
  });

  app.listen(PORT, '0.0.0.0', () => {
    log('Router started', { port: PORT, agents: KNOWN_AGENTS, routes: routeRegistry.size });
  });
}

async function shutdown() {
  log('Router shutdown');
  try { await resultConsumer.disconnect(); await producer.disconnect(); } catch {}
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => { log('Fatal', { error: e.message }); process.exit(1); });
