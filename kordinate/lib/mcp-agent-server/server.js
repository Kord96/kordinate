#!/usr/bin/env node
// Kord — HTTP-inspired route protocol server for agent orchestration.
//
// Registers capability-based MCP tools from KORD.json entries.
// Skills become POST tools, resources become catalog/get tools.
// Routes requests to the right agent. No worktree isolation — agents run
// in the current directory. KORD.json ownership model handles protection.
// Lightweight --print mode for cache, -p mode for full tool access.
//
// Skills and resources are declared per agent in KORD.json. Each skill
// becomes an MCP tool with a capability-based name (no agent names visible).
// Resources are exposed via <agent>_resources and <agent>_fetch tools.
//
// MCP tools: delegate, status, + dynamic per-route tools + resource catalog/get
// MCP endpoint: POST /mcp
// Health:       GET /health

import express from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';
import yaml from 'js-yaml';
import { spawn, execSync } from 'node:child_process';
import { readFileSync, writeFileSync, existsSync, readdirSync, statSync, mkdirSync } from 'node:fs';
import { join, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3100');
const HOME = process.env.HOME || '/home/claude';
const KORDINATE_HOME = process.env.KORDINATE_HOME || join(HOME, '.kord');
const REPO_ROOT = process.env.REPO_ROOT || join(HOME, 'kordinate');
const CACHE_DIR = join(KORDINATE_HOME, 'cache');
const BOOT_TIME = new Date().toISOString();

// File extensions tracked for cache magnitude scoring
const TRACKED_EXTS = new Set(['.md', '.yaml', '.yml', '.json', '.sh', '.js']);

// ─── Route registry ───

function loadRouteRegistry() {
  const registry = new Map();
  const kordJsonPath = join(KORDINATE_HOME, 'KORD.json');

  if (!existsSync(kordJsonPath)) {
    log('WARN: KORD.json not found, no routes registered');
    return registry;
  }

  try {
    const entries = JSON.parse(readFileSync(kordJsonPath, 'utf8'));

    // Load skill entries as routes
    for (const entry of entries) {
      if (entry.type !== 'skill' || !entry.public) continue;
      if (!entry.name || !entry.agent) {
        log(`WARN: skipping invalid skill entry`, entry);
        continue;
      }

      // Convert skill entry to route format
      const routeName = entry.agent === 'team'
        ? entry.name
        : `${entry.agent}_${entry.name}`.replace(/-/g, '_');

      if (registry.has(routeName)) {
        log(`WARN: duplicate route "${routeName}" (already registered)`);
        continue;
      }

      registry.set(routeName, {
        name: routeName,
        method: 'POST',
        description: entry.description,
        provider: entry.agent,
        skill: entry.name,
        arguments: entry.arguments,
        handler: entry.handler || null,
        registryPath: entry.registry || null,
      });
    }

    log(`Loaded ${registry.size} routes from KORD.json`);
  } catch (e) {
    log(`WARN: failed to parse KORD.json: ${e.message}`);
  }

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
      if (!entry.name || !entry.agent) { log(`WARN: skipping invalid resource entry`, entry); continue; }
      if (!registry.has(entry.agent)) registry.set(entry.agent, []);
      registry.get(entry.agent).push(entry);
    }
    log(`Loaded resources for ${registry.size} agents`);
  } catch (e) { log(`WARN: failed to load resources: ${e.message}`); }
  return registry;
}

function getKnownAgents(registry) {
  const agents = new Set();
  for (const route of registry.values()) {
    agents.add(route.provider);
  }
  // Also include agents with IDENTITY.md but no routes
  try {
    const agentsDir = join(KORDINATE_HOME, 'agents');
    for (const d of readdirSync(agentsDir, { withFileTypes: true })) {
      if (d.isDirectory() && existsSync(join(agentsDir, d.name, 'IDENTITY.md'))) {
        agents.add(d.name);
      }
    }
  } catch { /* best-effort */ }
  return [...agents].sort();
}

let routeRegistry = loadRouteRegistry();
let resourceRegistry = loadResourceRegistry();
let KNOWN_AGENTS = getKnownAgents(routeRegistry);
const activeRequests = new Map();

// Watch KORD.json for changes — reload routes automatically
const kordJsonPath = join(KORDINATE_HOME, 'KORD.json');
if (existsSync(kordJsonPath)) {
  const { watch } = await import('node:fs');
  let reloadTimeout;
  watch(kordJsonPath, () => {
    // Debounce — multiple writes may fire rapidly
    clearTimeout(reloadTimeout);
    reloadTimeout = setTimeout(() => {
      const oldCount = routeRegistry.size;
      routeRegistry = loadRouteRegistry();
      resourceRegistry = loadResourceRegistry();
      KNOWN_AGENTS = getKnownAgents(routeRegistry);
      log(`KORD.json changed — reloaded: ${oldCount} → ${routeRegistry.size} routes`);
    }, 500);
  });
  log(`Watching KORD.json for changes`);
}

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
    log(`Memory regen failed for ${agent}: ${e.stderr?.toString() || e.message}`);
  }
}

function loadSystemPrompt(agent) {
  const parts = [];

  const identityMd = join(KORDINATE_HOME, 'agents', agent, 'IDENTITY.md');
  if (existsSync(identityMd)) {
    const raw = readFileSync(identityMd, 'utf8');
    parts.push(raw.replace(/^---\n[\s\S]*?\n---\n?/, ''));
  }

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

// ─── Worktree lifecycle (removed) ───
// Worktree isolation removed. KORD.json ownership model handles write
// protection. Agents run in the current working directory.


// ─── Agent invocation ───

/** Spawn claude in a child process. Returns stdout. */
function spawnClaude(args, cwd, env, timeoutMs = 900000) {
  return new Promise((resolve, reject) => {
    const child = spawn('claude', args, {
      cwd,
      env: {
        ...process.env,
        ...env,
        // Disable file watching in spawned agents — they don't need hot-reload
        CHOKIDAR_USEPOLLING: '0',
        CHOKIDAR_INTERVAL: '999999',
        TSC_WATCHFILE: 'UseFsEvents',
        DISABLE_FILE_WATCHER: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      reject(new Error(`Timed out after ${timeoutMs / 1000}s`));
    }, timeoutMs);

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

    child.unref();
  });
}

/**
 * Lightweight invoke — --print mode, no worktree, no tool access.
 * Used for: skill routes, cache reviews, simple queries.
 */
async function invokeLightweight(agent, prompt) {
  log(`INVOKE-LIGHT ${agent}: ${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}`);
  const start = Date.now();

  regenerateMemory(agent);
  const systemPrompt = loadSystemPrompt(agent);

  const args = ['--print', '--dangerously-skip-permissions'];
  if (systemPrompt) args.push('--system-prompt', systemPrompt);
  args.push(prompt);

  try {
    const result = await spawnClaude(args, REPO_ROOT, { HOME });
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE-LIGHT ${agent}: done in ${elapsed}s, ${result.stdout.length} chars`);
    if (result.stderr) log(`INVOKE-LIGHT ${agent}: stderr: ${result.stderr.substring(0, 200)}`);
    return result.stdout.trim();
  } catch (e) {
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE-LIGHT ${agent}: FAILED after ${elapsed}s — ${e.message}`);
    if (e.stderr) log(`INVOKE-LIGHT ${agent}: stderr: ${e.stderr.substring(0, 500)}`);
    if (e.stdout) log(`INVOKE-LIGHT ${agent}: stdout: ${e.stdout.substring(0, 500)}`);
    throw e;
  }
}

/**
 * Full invoke — -p mode with tool access. No worktree isolation.
 * Agents run in the current working directory. KORD.json ownership handles protection.
 */
async function invokeFull(agent, prompt) {
  log(`INVOKE-FULL ${agent}: ${prompt.substring(0, 100)}${prompt.length > 100 ? '...' : ''}`);
  const start = Date.now();

  regenerateMemory(agent);
  const systemPrompt = loadSystemPrompt(agent);

  const args = ['-p', '--dangerously-skip-permissions'];
  if (systemPrompt) args.push('--system-prompt', systemPrompt);
  args.push(prompt);

  try {
    const result = await spawnClaude(args, REPO_ROOT, {
      HOME,
      KORDINATE_HOME,
    });
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE-FULL ${agent}: done in ${elapsed}s, ${result.stdout.length} chars`);
    if (result.stderr) log(`INVOKE-FULL ${agent}: stderr: ${result.stderr.substring(0, 200)}`);
    return result.stdout.trim();
  } catch (e) {
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    log(`INVOKE-FULL ${agent}: FAILED after ${elapsed}s — ${e.message}`);
    if (e.stderr) log(`INVOKE-FULL ${agent}: stderr: ${e.stderr.substring(0, 500)}`);
    if (e.stdout) log(`INVOKE-FULL ${agent}: stdout: ${e.stdout.substring(0, 500)}`);
    throw e;
  }
}

/** Backward-compatible wrapper — defaults to full. */
async function invokeAgent(agent, prompt) {
  return invokeFull(agent, prompt);
}

// ─── Cache helpers ───

function getCacheDir(routeName) {
  return join(CACHE_DIR, routeName);
}

function ensureCacheDir(routeName) {
  const dir = getCacheDir(routeName);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  return dir;
}

function parseDuration(str) {
  if (!str) return 0;
  const match = String(str).match(/^(\d+)(s|m|h|d)$/);
  if (!match) return 7 * 86400; // default 7d
  const n = parseInt(match[1]);
  switch (match[2]) {
    case 's': return n;
    case 'm': return n * 60;
    case 'h': return n * 3600;
    case 'd': return n * 86400;
    default: return 7 * 86400;
  }
}

function md5(content) {
  return createHash('md5').update(content).digest('hex');
}

function computeETag(data) {
  return `"${md5(data)}"`;
}

/** Walk input paths and collect tracked files. */
function collectFiles(inputs) {
  const files = [];
  for (const input of inputs) {
    const absPath = join(KORDINATE_HOME, input);
    try {
      const stat = statSync(absPath);
      if (stat.isDirectory()) {
        walkDir(absPath, files);
      } else if (stat.isFile() && TRACKED_EXTS.has(extname(absPath))) {
        files.push(absPath);
      }
    } catch { /* path doesn't exist, skip */ }
  }
  return files.sort();
}

function walkDir(dir, out) {
  try {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        walkDir(full, out);
      } else if (entry.isFile() && TRACKED_EXTS.has(extname(entry.name))) {
        out.push(full);
      }
    }
  } catch { /* skip unreadable dirs */ }
}

/** Read snapshot file into a Map of path -> { lines, hash }. */
function readSnapshot(snapshotPath) {
  const snap = new Map();
  if (!existsSync(snapshotPath)) return snap;
  try {
    const content = readFileSync(snapshotPath, 'utf8');
    for (const line of content.split('\n')) {
      if (!line.trim()) continue;
      const parts = line.split(/\s+/);
      if (parts.length >= 3) {
        const lines = parseInt(parts[0]);
        const hash = parts[1];
        const path = parts.slice(2).join(' ');
        snap.set(path, { lines, hash });
      }
    }
  } catch { /* best-effort */ }
  return snap;
}

/** Write snapshot of current file state. */
function writeSnapshot(snapshotPath, inputs) {
  const files = collectFiles(inputs);
  const lines = [];
  for (const file of files) {
    try {
      const content = readFileSync(file, 'utf8');
      const lineCount = content.split('\n').length;
      const hash = md5(content);
      lines.push(`${lineCount} ${hash} ${file}`);
    } catch { /* skip unreadable files */ }
  }
  writeFileSync(snapshotPath, lines.join('\n') + '\n');
}

/**
 * Check cache freshness for a route.
 * Returns 'fresh', 'uncertain', or 'stale'.
 */
function checkCacheExpiry(route, cacheDir) {
  const cache = route.cache;
  if (!cache) return 'stale'; // no cache config = always regenerate

  const dataPath = join(cacheDir, 'data.md');
  if (!existsSync(dataPath)) return 'stale';

  // Age check
  const maxAgeSeconds = parseDuration(cache.max_age);
  if (maxAgeSeconds > 0) {
    try {
      const mtime = statSync(dataPath).mtimeMs;
      const ageSeconds = (Date.now() - mtime) / 1000;
      if (ageSeconds >= maxAgeSeconds) return 'stale';
    } catch {
      return 'stale';
    }
  }

  // Hash-only mode — no magnitude scoring
  if (cache.type === 'hash' && cache.inputs) {
    const hashPath = join(cacheDir, '.hash');
    const files = collectFiles(cache.inputs);
    const allContent = files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('');
    const currentHash = md5(allContent);
    try {
      const storedHash = readFileSync(hashPath, 'utf8').trim();
      return currentHash === storedHash ? 'fresh' : 'stale';
    } catch {
      return 'stale'; // no stored hash
    }
  }

  // Magnitude-based scoring
  if (!cache.inputs) return 'fresh'; // no inputs to check = trust max_age alone

  const snapshotPath = join(cacheDir, '.snapshot');
  const snapshot = readSnapshot(snapshotPath);
  if (snapshot.size === 0) return 'uncertain'; // data exists but no snapshot

  const threshold = cache.threshold ?? 0.05;
  const staleThreshold = cache.stale_threshold ?? 0.30;

  const currentFiles = collectFiles(cache.inputs);
  let totalLines = 0;
  let changedLines = 0;

  // Check files in snapshot
  for (const [path, { lines: oldLines, hash: oldHash }] of snapshot) {
    totalLines += oldLines;
    try {
      const content = readFileSync(path, 'utf8');
      const newHash = md5(content);
      if (oldHash !== newHash) {
        const newLines = content.split('\n').length;
        const diff = Math.abs(newLines - oldLines);
        changedLines += diff > 0 ? diff : 1; // hash differs but same length = at least 1
      }
    } catch {
      changedLines += oldLines; // file deleted
    }
  }

  // Detect new files not in snapshot
  for (const file of currentFiles) {
    if (!snapshot.has(file)) {
      try {
        const content = readFileSync(file, 'utf8');
        changedLines += content.split('\n').length;
      } catch { /* skip */ }
    }
  }

  if (totalLines === 0) totalLines = 1;

  // Staleness score: change_ratio + (age_ratio * change_ratio)
  const changeRatio = changedLines / totalLines;
  const mtime = statSync(join(cacheDir, 'data.md')).mtimeMs;
  const ageSeconds = (Date.now() - mtime) / 1000;
  const ageRatio = Math.min(ageSeconds / (maxAgeSeconds || 1), 1.0);
  const score = changeRatio + (ageRatio * changeRatio);

  if (score < threshold) return 'fresh';
  if (score > staleThreshold) return 'stale';
  return 'uncertain';
}

// Review template for uncertain cache state (shared across all routes)
const REVIEW_TEMPLATE = `You are reviewing whether your cached response is still valid.

## Changed Inputs

{{DIFF}}

## Cached Response

{{CACHED_DATA}}

## Decision

Based on the changes above, is your cached response still accurate and complete?

- If the changes are irrelevant to your cached response (e.g., comments, formatting, unrelated files), respond: \`VALID\`
- If the changes affect the accuracy of your cached response, respond: \`STALE\`

Respond with ONLY \`VALID\` or \`STALE\` on the first line, followed by a brief reason.`;

/** Run lightweight cache review for uncertain state. */
async function runCacheReview(route, cacheDir) {
  const dataPath = join(cacheDir, 'data.md');
  const snapshotPath = join(cacheDir, '.snapshot');

  let diff = 'No diff available.';
  try {
    const snapshot = readSnapshot(snapshotPath);
    const changed = [];
    for (const [path, { hash: oldHash }] of snapshot) {
      try {
        const content = readFileSync(path, 'utf8');
        if (md5(content) !== oldHash) {
          changed.push(`Changed: ${path}`);
        }
      } catch {
        changed.push(`Deleted: ${path}`);
      }
    }
    if (changed.length > 0) {
      diff = changed.join('\n');
    }
  } catch { /* best-effort */ }

  const cachedData = existsSync(dataPath) ? readFileSync(dataPath, 'utf8') : 'No cached data.';
  const reviewPrompt = REVIEW_TEMPLATE
    .replace('{{DIFF}}', diff)
    .replace('{{CACHED_DATA}}', cachedData.substring(0, 2000)); // truncate for review

  try {
    const response = await invokeAgent(route.provider, reviewPrompt);
    const firstLine = response.split('\n')[0].trim().toUpperCase();
    return firstLine.startsWith('VALID') ? 'valid' : 'stale';
  } catch (e) {
    log(`Cache review failed for ${route.name}: ${e.message}`);
    return 'stale'; // fail-open: regenerate
  }
}

// ─── Resource helpers ───

function resolveProjectPath(projectArg) {
  if (!projectArg) return null;
  if (projectArg.startsWith('/')) {
    if (existsSync(projectArg)) return projectArg;
    throw new Error(`Project path not found: ${projectArg}`);
  }
  const candidates = [join(HOME, projectArg), join(HOME, 'repos', projectArg), join(HOME, 'test-repos', projectArg)];
  for (const c of candidates) { if (existsSync(c)) return c; }
  throw new Error(`Project not found: ${projectArg}`);
}

function resolveResourcePath(entry, projectParam) {
  if (!entry.path) return null;
  if (entry.scope === 'project') {
    const projectPath = resolveProjectPath(projectParam);
    return entry.path.replace('<project>', projectPath);
  }
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
    if (files.length === 0) return null;
    return files.map(f => `--- ${f} ---\n${readFileSync(join(resolved, f), 'utf8')}`).join('\n\n');
  }
  if (!existsSync(resolved)) return null;
  return readFileSync(resolved, 'utf8');
}

function checkFileResourceFreshness(entry, resolvedPath) {
  if (!entry.cache) return 'fresh';
  const maxAgeSeconds = parseDuration(entry.cache.max_age);
  if (maxAgeSeconds <= 0) return 'fresh';
  try {
    const ageSeconds = (Date.now() - statSync(resolvedPath).mtimeMs) / 1000;
    return ageSeconds >= maxAgeSeconds ? 'stale' : 'fresh';
  } catch { return 'stale'; }
}

const activeProductions = new Map();

async function triggerProduction(entry, projectPath) {
  const prodKey = `${entry.agent}/${entry.produced_by}/${projectPath || 'global'}`;
  if (activeProductions.has(prodKey)) {
    log(`RESOURCE: waiting on in-flight production ${prodKey}`);
    return activeProductions.get(prodKey);
  }
  const promise = (async () => {
    try {
      log(`RESOURCE: triggering /${entry.produced_by} as ${entry.agent} for ${prodKey}`);
      await invokeFull(entry.agent, `Run the /${entry.produced_by} skill. Input: ${projectPath || ''}`);
      log(`RESOURCE: production complete for ${prodKey}`);
    } finally { activeProductions.delete(prodKey); }
  })();
  activeProductions.set(prodKey, promise);
  return promise;
}

async function handleResourceGet(entry, projectParam, ifNoneMatch) {
  if (entry.path) {
    const resolved = resolveResourcePath(entry, projectParam);
    const isDir = entry.path.endsWith('/');
    const freshness = checkFileResourceFreshness(entry, resolved);
    log(`RESOURCE ${entry.agent}/${entry.name}: freshness=${freshness}`);
    if (freshness === 'fresh') {
      const content = readResourceContent(resolved, isDir, entry.format);
      if (content) {
        const etag = computeETag(content);
        if (ifNoneMatch && ifNoneMatch === etag) return { text: '[304 not modified]', etag, status: 304 };
        return { text: content, etag, status: 200 };
      }
    }
    if (entry.produced_by) {
      await triggerProduction(entry, projectParam);
      const content = readResourceContent(resolved, isDir, entry.format);
      if (content) return { text: content, etag: computeETag(content), status: 200 };
      return { text: `Production completed but resource not found at ${resolved}`, status: 404 };
    }
    const content = readResourceContent(resolved, isDir, entry.format);
    if (content) return { text: content, etag: computeETag(content), status: 200 };
    return { text: `Resource not found: ${entry.name}`, status: 404 };
  }
  if (entry.guidelines) {
    const cacheKey = `resource/${entry.agent}/${entry.name}`;
    if (entry.cache) {
      const cacheDir = ensureCacheDir(cacheKey);
      const dataPath = join(cacheDir, 'data.md');
      const syntheticRoute = { name: cacheKey, cache: entry.cache, provider: entry.agent };
      const expiry = checkCacheExpiry(syntheticRoute, cacheDir);
      log(`RESOURCE ${entry.agent}/${entry.name}: query cache=${expiry}`);
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
      const response = await invokeLightweight(entry.agent, entry.guidelines);
      writeFileSync(dataPath, response);
      writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
      if (entry.cache.inputs) writeSnapshot(join(cacheDir, '.snapshot'), entry.cache.inputs);
      if (entry.cache.type === 'hash' && entry.cache.inputs) {
        const files = collectFiles(entry.cache.inputs);
        const allContent = files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('');
        writeFileSync(join(cacheDir, '.hash'), md5(allContent));
      }
      log(`RESOURCE ${entry.agent}/${entry.name}: regenerated, ${response.length} chars`);
      return { text: response, etag: computeETag(response), status: 200 };
    }
    const response = await invokeLightweight(entry.agent, entry.guidelines);
    return { text: response, etag: computeETag(response), status: 200 };
  }
  return { text: `Resource "${entry.name}" has neither path nor guidelines`, status: 500 };
}

// ─── Script route handler ───

async function handleScriptRoute(route, message) {
  const dir = message.trim();
  if (!dir) return 'ERROR: No directory provided. Usage: validate-output <dir>';

  // Load the validator registry
  const registryFile = join(KORDINATE_HOME, route.registryPath);
  if (!existsSync(registryFile)) return `ERROR: Registry not found at ${registryFile}`;

  let registry;
  try {
    registry = yaml.load(readFileSync(registryFile, 'utf8'));
  } catch (e) {
    return `ERROR: Failed to parse registry: ${e.message}`;
  }

  // Match dir against registry patterns
  const validators = registry.validators || [];
  const match = validators.find(v => dir.includes(v.pattern));
  if (!match) return `NO_VALIDATOR: No validator registered for ${dir}. Proceed.`;

  // Resolve script path
  const scriptPath = join(KORDINATE_HOME, match.script);
  if (!existsSync(scriptPath)) return `ERROR: Validator script not found at ${scriptPath}`;

  // Run the validator
  log(`SCRIPT ${route.name}: running ${scriptPath} on ${dir}`);
  try {
    const result = execSync(`python3 "${scriptPath}" "${dir}"`, {
      cwd: KORDINATE_HOME,
      timeout: 60000,
      env: { ...process.env, HOME, KORDINATE_HOME },
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    const output = result.toString().trim();

    // Validation passed — compute completion token
    try {
      const tokenResult = execSync(
        `find "${dir}" -name "*.json" -o -name "*.yaml" | sort | xargs cat | sha256sum | cut -d' ' -f1`,
        { timeout: 10000, stdio: ['pipe', 'pipe', 'pipe'] }
      );
      const token = tokenResult.toString().trim();
      log(`SCRIPT ${route.name}: VALID, token=${token.substring(0, 16)}...`);
      return `${output}\n\nVALIDATED — token: ${token}\nInclude this token in your report to confirm validation passed.`;
    } catch {
      return `${output}\n\nVALID but token computation failed.`;
    }
  } catch (e) {
    // Validation failed — return errors
    const stderr = e.stderr?.toString() || '';
    const stdout = e.stdout?.toString() || '';
    const output = (stdout + '\n' + stderr).trim();
    log(`SCRIPT ${route.name}: INVALID — ${output.substring(0, 200)}`);
    return `VALIDATION FAILED\n\n${output}\n\nTo fix:\n1. Read each ERROR line — it tells you exactly what's wrong and where.\n2. Fix the output files (atlas.json, stories/*.yaml, journeys/*.yaml).\n3. Call warden validate-output again with the same directory.\n4. Repeat until you get a VALIDATED response with a completion token.\n\nDo NOT compute the token yourself — only this server can issue valid tokens.`;
  }
}

// ─── Auth delegation ───

function readAuthSecret(agent) {
  const lockFile = join(KORDINATE_HOME, 'profile', 'locks', agent);
  try {
    return readFileSync(lockFile, 'utf8').trim();
  } catch {
    return null;
  }
}

// ─── Route handler ───

async function handleRoute(route, message, ifNoneMatch, caller) {
  const isMain = !caller || caller === 'main';
  const requestId = `${route.name}-${Date.now()}`;
  activeRequests.set(requestId, { route: route.name, provider: route.provider, caller: caller || 'unknown', startedAt: new Date().toISOString() });

  try {
    // Script-handled routes — run directly, no agent spawn
    if (route.handler === 'script' && route.registryPath) {
      const result = await handleScriptRoute(route, message);
      return { text: result, status: 200 };
    }

    // Skill routes — always return auth grant (caller runs locally)
    if (route.skill && !route.guidelines && !route.cache) {
      const secret = readAuthSecret(route.provider);
      if (secret) {
        log(`ROUTE ${route.name}: auth delegation to /${route.skill} as ${route.provider}`);
        return {
          text: JSON.stringify({
            local: true,
            skill: route.skill,
            provider: route.provider,
            secret,
            instructions: `Run this locally: echo '${secret}' > /tmp/.${route.provider}-auth && then run /${route.skill} with your original input. After the skill completes, run: rm /tmp/.${route.provider}-auth`,
          }),
          status: 200,
        };
      }
      log(`ROUTE ${route.name}: no auth secret for ${route.provider}, falling back to spawn`);
    }

    // Non-cached routes
    if (!route.cache) {
      const prompt = route.guidelines
        ? `${route.guidelines}\n\n---\n\n${message}`
        : route.skill
          ? `Run the /${route.skill} skill. Input: ${message}`
          : message;

      // Main caller: return instructions to spawn locally (faster, visible)
      // Subagent caller: kord spawns remotely (subagents can't spawn subagents)
      if (isMain) {
        const secret = readAuthSecret(route.provider);
        log(`ROUTE ${route.name}: local spawn instructions for main caller`);
        return {
          text: JSON.stringify({
            local: true,
            agent: route.provider,
            prompt,
            gate_secret: secret,
            instructions: secret
              ? `First run: echo '${secret}' > /tmp/.kord-gate-${route.provider} — then spawn a subagent using the Agent tool with subagent_type="${route.provider}" and the prompt above. The gate secret is one-time use and auto-consumed.`
              : `Spawn a subagent using the Agent tool with subagent_type="${route.provider}" and the prompt above.`,
          }),
          status: 200,
        };
      }

      const response = await invokeFull(route.provider, prompt);
      return { text: response, etag: computeETag(response), status: 200 };
    }

    // Cached routes
    const cacheDir = ensureCacheDir(route.name);
    const dataPath = join(cacheDir, 'data.md');
    const snapshotPath = join(cacheDir, '.snapshot');
    const hashPath = join(cacheDir, '.hash');

    const expiry = checkCacheExpiry(route, cacheDir);
    log(`ROUTE ${route.name}: cache=${expiry}`);

    // Fresh — serve from cache
    if (expiry === 'fresh' && existsSync(dataPath)) {
      const cached = readFileSync(dataPath, 'utf8');
      const etag = computeETag(cached);

      // ETag conditional check
      if (ifNoneMatch && ifNoneMatch === etag) {
        return { text: '[304 not modified]', etag, status: 304 };
      }

      return { text: `[cached]\n\n${cached}`, etag, status: 200 };
    }

    // Uncertain — run lightweight review
    if (expiry === 'uncertain') {
      const reviewResult = await runCacheReview(route, cacheDir);
      if (reviewResult === 'valid') {
        // Update snapshot and serve
        if (route.cache.inputs) writeSnapshot(snapshotPath, route.cache.inputs);
        writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
        const cached = readFileSync(dataPath, 'utf8');
        return { text: `[cached:revalidated]\n\n${cached}`, etag: computeETag(cached), status: 200 };
      }
      // Fall through to regenerate
    }

    // Stale — regenerate
    const prompt = route.guidelines
      ? `${route.guidelines}\n\n---\n\n${message}`
      : route.skill
        ? `Run the /${route.skill} skill. Input: ${message}`
        : message;

    // Main caller: return instructions to regenerate locally
    if (isMain) {
      const secret = readAuthSecret(route.provider);
      log(`ROUTE ${route.name}: stale cache, local regeneration for main caller`);
      return {
        text: JSON.stringify({
          local: true,
          agent: route.provider,
          prompt,
          cache_stale: true,
          gate_secret: secret,
          instructions: secret
            ? `Cache is stale. First run: echo '${secret}' > /tmp/.kord-gate-${route.provider} — then spawn a subagent using Agent tool with subagent_type="${route.provider}" and the prompt above.`
            : `Cache is stale. Spawn a subagent using Agent tool with subagent_type="${route.provider}" and the prompt above.`,
        }),
        status: 200,
      };
    }

    const response = await invokeFull(route.provider, prompt);

    // Cache the result
    try {
      writeFileSync(dataPath, response);
      writeFileSync(join(cacheDir, '.valid'), new Date().toISOString());
      if (route.cache.inputs) writeSnapshot(snapshotPath, route.cache.inputs);
      if (route.cache.type === 'hash' && route.cache.inputs) {
        const files = collectFiles(route.cache.inputs);
        const allContent = files.map(f => { try { return readFileSync(f, 'utf8'); } catch { return ''; } }).join('');
        writeFileSync(hashPath, md5(allContent));
      }
      log(`ROUTE ${route.name}: cached, ${response.length} chars`);
    } catch (e) {
      log(`ROUTE ${route.name}: cache write failed — ${e.message}`);
    }

    return { text: response, etag: computeETag(response), status: 200 };
  } finally {
    activeRequests.delete(requestId);
  }
}

// ─── MCP tool registration ───

function registerTools(server) {
  // Delegate — invoke any agent directly
  server.tool(
    'delegate',
    'Delegate a prompt to a kordinate agent. If caller is main, returns instructions to spawn locally. If caller is a subagent, spawns remotely.',
    {
      agent: z.enum(KNOWN_AGENTS).describe('The agent to invoke'),
      prompt: z.string().describe('The prompt to send to the agent'),
      caller: z.string().optional().describe('Who is calling — "main" for local spawn instructions, agent name for remote spawn'),
    },
    async ({ agent, prompt, caller }) => {
      const isMain = !caller || caller === 'main';
      log('TOOL delegate called', { agent, caller: caller || 'main', prompt: prompt.substring(0, 100) });

      // Check if the prompt matches a script-handled route for this agent
      // e.g., "validate-output /path/to/dir" → warden_validate_output route
      for (const [, route] of routeRegistry) {
        if (route.provider === agent && route.handler === 'script' && route.skill) {
          const skillPrefix = route.skill.replace(/-/g, '[ -]');
          const match = prompt.match(new RegExp(`^${skillPrefix}\\s+(.+)`, 'i'));
          if (match) {
            log(`DELEGATE ${agent}: matched script route ${route.name}`);
            const result = await handleScriptRoute(route, match[1].trim());
            return { content: [{ type: 'text', text: result }] };
          }
        }
      }

      if (isMain) {
        const secret = readAuthSecret(agent);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              local: true,
              agent,
              prompt,
              gate_secret: secret,
              instructions: secret
                ? `First run: echo '${secret}' > /tmp/.kord-gate-${agent} — then spawn a subagent using the Agent tool with subagent_type="${agent}" and the prompt above. The gate secret is one-time use and auto-consumed.`
                : `Spawn a subagent using the Agent tool with subagent_type="${agent}" and the prompt above.`,
            }),
          }],
        };
      }

      const requestId = `${agent}-${Date.now()}`;
      activeRequests.set(requestId, { agent, caller, startedAt: new Date().toISOString() });
      try {
        const response = await invokeFull(agent, prompt);
        return { content: [{ type: 'text', text: response }] };
      } catch (e) {
        log('TOOL delegate error', { agent, error: e.message });
        throw e;
      } finally {
        activeRequests.delete(requestId);
      }
    },
  );

  // Status
  server.tool(
    'status',
    'Return the current status of the kord server — uptime, known agents, registered routes, active requests.',
    {},
    async () => {
      const routes = [];
      for (const [name, route] of routeRegistry) {
        routes.push({ name, method: route.method, provider: route.provider, cached: !!route.cache });
      }
      const resourceInfo = {};
      for (const [agent, resources] of resourceRegistry) { resourceInfo[agent] = resources.map(r => r.name); }
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            name: 'kord',
            boot: BOOT_TIME,
            agents: KNOWN_AGENTS,
            routes,
            resources: resourceInfo,
            active: [...activeRequests.values()],
          }, null, 2),
        }],
      };
    },
  );

  // Dynamic per-route tools
  for (const [name, route] of routeRegistry) {
    const schema = {
      message: z.string().describe('The request message'),
      caller: z.string().optional().describe('Who is calling — "main" for local spawn instructions, omit or agent name for remote spawn'),
    };

    // Add optional ETag field for cached routes
    if (route.cache) {
      schema.if_none_match = z.string().optional().describe('ETag from a previous response for conditional requests');
    }

    server.tool(
      name,
      route.description,
      schema,
      async (params) => {
        log(`TOOL ${name} called`, { caller: params.caller || 'main', message: params.message?.substring(0, 100) });
        try {
          const result = await handleRoute(route, params.message, params.if_none_match, params.caller);
          const meta = route.cache ? ` etag=${result.etag}` : '';
          log(`TOOL ${name} done`, { status: result.status, responseLen: result.text.length });
          return {
            content: [{
              type: 'text',
              text: result.etag ? `${result.text}\n\n<!-- etag: ${result.etag} -->` : result.text,
            }],
          };
        } catch (e) {
          log(`TOOL ${name} error`, { error: e.message });
          throw e;
        }
      },
    );
  }

  // Resource catalog + get tools
  for (const [agent, resources] of resourceRegistry) {
    server.tool(
      `${agent}_resources`,
      `List resources available from ${agent} — descriptions, scope, and format.`,
      {},
      async () => {
        const items = resources.map(r => ({ name: r.name, description: r.description, scope: r.scope, format: r.format || null, produced_by: r.produced_by || null }));
        return { content: [{ type: 'text', text: JSON.stringify(items, null, 2) }] };
      },
    );
    const resourceNames = resources.map(r => r.name);
    const hasProjectScoped = resources.some(r => r.scope === 'project');
    const getSchema = { resource: z.enum(resourceNames).describe('Which resource to retrieve') };
    if (hasProjectScoped) getSchema.project = z.string().optional().describe('Project path — required for project-scoped resources');
    getSchema.if_none_match = z.string().optional().describe('ETag from previous response for conditional requests');
    server.tool(
      `${agent}_fetch`,
      `Retrieve a ${agent} resource. Serves from disk/cache if fresh, triggers production if stale.`,
      getSchema,
      async (params) => {
        log(`TOOL ${agent}_get called`, { resource: params.resource, project: params.project });
        const entry = resources.find(r => r.name === params.resource);
        if (!entry) throw new Error(`Unknown resource: ${params.resource}`);
        if (entry.scope === 'project' && !params.project) throw new Error(`Resource "${entry.name}" is project-scoped — provide a project parameter`);
        try {
          const result = await handleResourceGet(entry, params.project, params.if_none_match);
          log(`TOOL ${agent}_get done`, { resource: params.resource, status: result.status });
          return { content: [{ type: 'text', text: result.etag ? `${result.text}\n\n<!-- etag: ${result.etag} -->` : result.text }] };
        } catch (e) { log(`TOOL ${agent}_get error`, { resource: params.resource, error: e.message }); throw e; }
      },
    );
  }
}

// ─── Logging ───

function log(msg, data) {
  const ts = new Date().toISOString().slice(11, 23);
  if (data) {
    console.log(`[kord ${ts}] ${msg}`, JSON.stringify(data));
  } else {
    console.log(`[kord ${ts}] ${msg}`);
  }
}

// ─── Express app ───

const app = express();
app.use(express.json({ limit: '1mb' }));

app.use((req, _res, next) => {
  if (req.path !== '/health') {
    const body = req.body;
    const method = body?.method || body?.params?.name || '-';
    log(`${req.method} ${req.path} method=${method} session=${req.headers['mcp-session-id'] || 'none'}`);
  }
  next();
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'kord', boot: BOOT_TIME, routes: routeRegistry.size });
});

// ─── MCP transport ───

app.post('/mcp', async (req, res) => {
  const method = req.body?.method || 'unknown';
  log(`MCP request: ${method}`);

  try {
    const server = new McpServer({ name: 'kord', version: '2.0.0' });
    registerTools(server);

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
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
  log('Shape-shifting MCP agent server on :' + PORT);
  log(`Known agents: ${KNOWN_AGENTS.join(', ')}`);
  log(`Registered routes: ${[...routeRegistry.keys()].join(', ')}`);
  log(`Resources: ${[...resourceRegistry.entries()].map(([a, rs]) => `${a}(${rs.length})`).join(', ') || 'none'}`);
  log('MCP: /mcp | Health: /health');
});
