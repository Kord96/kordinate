#!/usr/bin/env node
// Agent Pod Daemon — stream-json bridge between Kafka and a persistent Claude session.
//
// Pod = Claude session. Claude runs as a long-lived process for the pod's
// entire lifetime. The daemon is a thin bridge:
//
//   Kafka consumer → parse job → write to Claude stdin (stream-json)
//   Claude stdout (stream-json) → parse result → Kafka producer
//
// No --system-prompt, --resume, --session-id, preload.py, or boot step.
// Claude loads CLAUDE.md (with @ imports) natively from cwd.
//
// KEDA scales the pod itself. Scale down = kill pod = kill Claude.
// Scale up = new pod = new Claude session = fresh memory from shared PVC.

import { Kafka } from 'kafkajs';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { createInterface } from 'node:readline';
import { randomUUID } from 'node:crypto';
import { readFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, relative } from 'node:path';
import { execSync } from 'node:child_process';

// ─── Config ───

const AGENT_NAME = process.env.AGENT_NAME;
if (!AGENT_NAME) { console.error('AGENT_NAME required'); process.exit(1); }

const AGENT_PROJECT_DIR = process.env.AGENT_PROJECT_DIR || `/kord/agents/${AGENT_NAME}`;
const KAFKA_BROKERS = (process.env.KAFKA_BROKERS || 'kafka-kafka-bootstrap.dev.svc.cluster.local:9092').split(',');
const STATUS_PORT = parseInt(process.env.STATUS_PORT || '9090');
const DEFAULT_TIMEOUT_MS = 1_800_000; // 30 minutes
const POD_NAME = process.env.HOSTNAME || `agent-${AGENT_NAME}-local`;
const RESPAWN_DELAY_MS = 3000;
const KORDINATE_HOME = process.env.KORDINATE_HOME || '/data/repos/kordinate';
const PROJECTS_ROOT = process.env.PROJECTS_ROOT || '/kord/repos';

// Read model, provider, and OpenClaude profile from files (written by deploy-runtime.sh from IDENTITY.md)
let AGENT_MODEL = 'sonnet';
let AGENT_PROVIDER = 'anthropic';
let AGENT_MODEL_SPEC = 'anthropic:sonnet';
let PROFILE_DATA = null;
let BACKEND_POOL = null;
let ACTIVE_BACKEND = null;
let MODEL_ENV = {};

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function selectBackend(pool, podName) {
  if (!pool?.backends?.length) return null;
  const selection = pool.selection || 'first';
  if (selection === 'random') {
    return pool.backends[Math.floor(Math.random() * pool.backends.length)];
  }
  if (selection === 'hash') {
    const seed = createHash('md5').update(String(podName || POD_NAME)).digest('hex');
    const index = parseInt(seed.slice(0, 8), 16) % pool.backends.length;
    return pool.backends[index];
  }
  return pool.backends[0];
}

function resolveBackendEnv(backend) {
  if (!backend) return {};
  const env = {};
  if (backend.base_url) {
    if (backend.profile === 'gemini') env.GEMINI_BASE_URL = backend.base_url;
    else env.OPENAI_BASE_URL = backend.base_url;
  }
  if (backend.model) {
    if (backend.profile === 'anthropic') env.MODEL = backend.model;
    else if (backend.profile === 'gemini') env.GEMINI_MODEL = backend.model;
    else env.OPENAI_MODEL = backend.model;
  }
  if (backend.api_key_env && process.env[backend.api_key_env]) {
    if (backend.profile === 'anthropic') env.ANTHROPIC_API_KEY = process.env[backend.api_key_env];
    else if (backend.profile === 'gemini') env.GEMINI_API_KEY = process.env[backend.api_key_env];
    else if (backend.profile !== 'ollama') env.OPENAI_API_KEY = process.env[backend.api_key_env];
  }
  if (backend.profile === 'ollama' && !env.OPENAI_API_KEY) {
    env.OPENAI_API_KEY = 'ollama';
  }
  if (backend.extra_env && typeof backend.extra_env === 'object') {
    Object.assign(env, backend.extra_env);
  }
  if (Array.isArray(backend.env_passthrough)) {
    for (const key of backend.env_passthrough) {
      if (process.env[key] !== undefined) env[key] = process.env[key];
    }
  }
  return env;
}

BACKEND_POOL = readJson(`${AGENT_PROJECT_DIR}/.openclaude-backends.json`);
PROFILE_DATA = readJson(`${AGENT_PROJECT_DIR}/.openclaude-profile.json`);

const manuallySelectedBackend = PROFILE_DATA?.selection === 'manual' && PROFILE_DATA?.backend_name && BACKEND_POOL?.backends?.length
  ? BACKEND_POOL.backends.find((backend) => backend.name === PROFILE_DATA.backend_name) || null
  : null;

ACTIVE_BACKEND = manuallySelectedBackend || selectBackend(BACKEND_POOL, POD_NAME);

if (ACTIVE_BACKEND) {
  PROFILE_DATA = {
    ...PROFILE_DATA,
    version: BACKEND_POOL?.version || PROFILE_DATA?.version || 2,
    selection: manuallySelectedBackend ? 'manual' : (BACKEND_POOL?.selection || PROFILE_DATA?.selection || 'first'),
    backend_name: ACTIVE_BACKEND.name,
    profile: ACTIVE_BACKEND.profile,
    provider: ACTIVE_BACKEND.provider || ACTIVE_BACKEND.profile,
    model: ACTIVE_BACKEND.model,
    base_url: ACTIVE_BACKEND.base_url || null,
    api_key_env: ACTIVE_BACKEND.api_key_env || null,
    api_key_ref: ACTIVE_BACKEND.api_key_ref || null,
    env_passthrough: ACTIVE_BACKEND.env_passthrough || [],
    extra_env: ACTIVE_BACKEND.extra_env || {},
  };
}

if (!PROFILE_DATA) {
  PROFILE_DATA = readJson(`${AGENT_PROJECT_DIR}/.openclaude-profile.json`);
}

if (PROFILE_DATA) {
  AGENT_PROVIDER = PROFILE_DATA.provider || PROFILE_DATA.profile || AGENT_PROVIDER;
  AGENT_MODEL = PROFILE_DATA.model || AGENT_MODEL;
  AGENT_MODEL_SPEC = `${AGENT_PROVIDER}:${AGENT_MODEL}`;
}

MODEL_ENV = resolveBackendEnv(ACTIVE_BACKEND || PROFILE_DATA);

// Read OpenClaude profile first (primary)
try {
  const profileContent = readFileSync(`${AGENT_PROJECT_DIR}/.openclaude-profile.json`, 'utf8');
  if (!PROFILE_DATA) PROFILE_DATA = JSON.parse(profileContent);
} catch {}

// Read backward compatibility files only if no profile data is available
if (!PROFILE_DATA) {
  try {
    AGENT_MODEL = readFileSync(`${AGENT_PROJECT_DIR}/.model`, 'utf8').trim();
  } catch {}

  try {
    AGENT_PROVIDER = readFileSync(`${AGENT_PROJECT_DIR}/.provider`, 'utf8').trim();
  } catch {}

  try {
    AGENT_MODEL_SPEC = readFileSync(`${AGENT_PROJECT_DIR}/.model-spec`, 'utf8').trim();
  } catch {}
}

if (AGENT_PROVIDER === 'claude') {
  AGENT_PROVIDER = 'anthropic';
}
if (AGENT_MODEL_SPEC.startsWith('claude:')) {
  AGENT_MODEL_SPEC = `anthropic:${AGENT_MODEL_SPEC.slice('claude:'.length)}`;
}
if (!AGENT_MODEL_SPEC || AGENT_MODEL_SPEC === 'anthropic:sonnet') {
  AGENT_MODEL_SPEC = `${AGENT_PROVIDER}:${AGENT_MODEL}`;
}

ACTIVE_BACKEND = ACTIVE_BACKEND || {
  name: PROFILE_DATA?.backend_name || AGENT_PROVIDER,
  profile: PROFILE_DATA?.profile || AGENT_PROVIDER,
  provider: PROFILE_DATA?.provider || AGENT_PROVIDER,
  model: PROFILE_DATA?.model || AGENT_MODEL,
  base_url: PROFILE_DATA?.base_url || null,
  api_key_env: PROFILE_DATA?.api_key_env || null,
  api_key_ref: PROFILE_DATA?.api_key_ref || null,
};

MODEL_ENV = {
  ...MODEL_ENV,
  ...resolveBackendEnv(ACTIVE_BACKEND),
};

AGENT_PROVIDER = ACTIVE_BACKEND.provider || AGENT_PROVIDER;
AGENT_MODEL = ACTIVE_BACKEND.model || AGENT_MODEL;
AGENT_MODEL_SPEC = `${AGENT_PROVIDER}:${AGENT_MODEL}`;
if (AGENT_PROVIDER === 'anthropic') {
  AGENT_MODEL_SPEC = `anthropic:${AGENT_MODEL}`;
}
if (PROFILE_DATA?.profile === 'anthropic') {
  AGENT_MODEL = PROFILE_DATA.model || AGENT_MODEL;
}

// Model mappings for backward compatibility (used only if profile not found)
const CLAUDE_MODEL_MAP = {
  'opus': 'claude-opus-4-6',
  'sonnet': 'claude-sonnet-4-6',
  'haiku': 'claude-haiku-4-5-20251001',
};

const DEEPSEEK_MODEL_MAP = {
  'chat': 'deepseek-chat',
  'reasoner': 'deepseek-reasoner',
};

const FIREWORKS_MODEL_MAP = {
  'deepseek-v3p2': 'accounts/fireworks/models/deepseek-v3p2',
  'deepseek-r1': 'accounts/fireworks/models/deepseek-r1',
};

const GEMINI_MODEL_MAP = {
  'gemini-3.1-pro-preview': 'gemini-3.1-pro-preview',
};

let CLAUDE_MODEL = CLAUDE_MODEL_MAP[AGENT_MODEL] || AGENT_MODEL || CLAUDE_MODEL_MAP['sonnet'];
if (AGENT_PROVIDER === 'anthropic') {
  CLAUDE_MODEL = AGENT_MODEL;
}

if (PROFILE_DATA?.profile === 'anthropic') {
  CLAUDE_MODEL = PROFILE_DATA.model || CLAUDE_MODEL_MAP[AGENT_MODEL] || CLAUDE_MODEL;
} else if (!ACTIVE_BACKEND) {
  // Fallback to legacy provider logic when no explicit backend profile is available
  if (AGENT_PROVIDER === 'anthropic') {
    CLAUDE_MODEL = CLAUDE_MODEL_MAP[AGENT_MODEL] || CLAUDE_MODEL_MAP['sonnet'];
  } else if (AGENT_PROVIDER === 'deepseek') {
    const model = DEEPSEEK_MODEL_MAP[AGENT_MODEL] || DEEPSEEK_MODEL_MAP['chat'];
    MODEL_ENV = {
      OPENAI_BASE_URL: 'https://api.deepseek.com',
      OPENAI_MODEL: model,
      OPENAI_API_KEY: process.env.DEEPSEEK_API_KEY || '',
    };
    PROFILE_DATA = { profile: 'openai', provider: 'openai', model, backend_name: 'deepseek', base_url: 'https://api.deepseek.com', api_key_env: 'DEEPSEEK_API_KEY' };
    AGENT_PROVIDER = 'openai';
    AGENT_MODEL = model;
    AGENT_MODEL_SPEC = `openai:${model}`;
  } else if (AGENT_PROVIDER === 'fireworks') {
    const model = FIREWORKS_MODEL_MAP[AGENT_MODEL] || FIREWORKS_MODEL_MAP['deepseek-v3p2'];
    MODEL_ENV = {
      OPENAI_BASE_URL: 'https://api.fireworks.ai/inference/v1',
      OPENAI_MODEL: model,
      OPENAI_API_KEY: process.env.FIREWORKS_API_KEY || '',
    };
    PROFILE_DATA = { profile: 'openai', provider: 'openai', model, backend_name: 'fireworks', base_url: 'https://api.fireworks.ai/inference/v1', api_key_env: 'FIREWORKS_API_KEY' };
    AGENT_PROVIDER = 'openai';
    AGENT_MODEL = model;
    AGENT_MODEL_SPEC = `openai:${model}`;
  } else if (AGENT_PROVIDER === 'gemini') {
    const model = GEMINI_MODEL_MAP[AGENT_MODEL] || AGENT_MODEL || 'gemini-2.0-flash';
    MODEL_ENV = {
      GEMINI_BASE_URL: 'https://generativelanguage.googleapis.com/v1beta/openai',
      GEMINI_MODEL: model,
      GEMINI_API_KEY: process.env.GEMINI_API_KEY || '',
    };
    PROFILE_DATA = { profile: 'gemini', provider: 'gemini', model, backend_name: 'gemini', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai', api_key_env: 'GEMINI_API_KEY' };
    AGENT_PROVIDER = 'gemini';
    AGENT_MODEL = model;
    AGENT_MODEL_SPEC = `gemini:${model}`;
  }
}

if (!PROFILE_DATA?.profile) {
  PROFILE_DATA = {
    profile: AGENT_PROVIDER === 'claude' ? 'anthropic' : AGENT_PROVIDER,
    provider: AGENT_PROVIDER === 'claude' ? 'anthropic' : AGENT_PROVIDER,
    model: AGENT_MODEL,
    backend_name: AGENT_PROVIDER === 'claude' ? 'anthropic' : AGENT_PROVIDER,
  };
}

if (PROFILE_DATA.profile === 'anthropic') {
  AGENT_PROVIDER = 'anthropic';
  CLAUDE_MODEL = PROFILE_DATA.model || CLAUDE_MODEL;
  AGENT_MODEL = CLAUDE_MODEL;
  AGENT_MODEL_SPEC = `anthropic:${CLAUDE_MODEL}`;
}

ACTIVE_BACKEND = ACTIVE_BACKEND || {
  name: PROFILE_DATA.backend_name || PROFILE_DATA.provider || PROFILE_DATA.profile,
  profile: PROFILE_DATA.profile,
  provider: PROFILE_DATA.provider || PROFILE_DATA.profile,
  model: PROFILE_DATA.model || AGENT_MODEL,
  base_url: PROFILE_DATA.base_url || null,
  api_key_env: PROFILE_DATA.api_key_env || null,
  api_key_ref: PROFILE_DATA.api_key_ref || null,
};

MODEL_ENV = {
  ...MODEL_ENV,
  ...resolveBackendEnv(ACTIVE_BACKEND),
};

AGENT_PROVIDER = ACTIVE_BACKEND.provider || PROFILE_DATA.provider || PROFILE_DATA.profile || AGENT_PROVIDER;
AGENT_MODEL = ACTIVE_BACKEND.model || PROFILE_DATA.model || AGENT_MODEL;
AGENT_MODEL_SPEC = `${AGENT_PROVIDER}:${AGENT_MODEL}`;
if (AGENT_PROVIDER === 'anthropic') {
  CLAUDE_MODEL = AGENT_MODEL;
}

// Memory dirs — Claude reads directly, no local copies
const AGENT_GLOBAL_DIR = `${AGENT_PROJECT_DIR}/memory/global`;
const TEAM_GLOBAL_DIR = '/kord/team/memory/global';

// Load reflection prompt template once at startup
let REFLECTION_PROMPT = '';
try {
  REFLECTION_PROMPT = readFileSync(`${KORDINATE_HOME}/lib/templates/reflection-prompt.md`, 'utf8');
} catch {
  REFLECTION_PROMPT = '';
}

// ─── Hash-based change detection ───
// Tracks MD5 hashes of files in watched directories.
// No copies — Claude reads directly from the shared dirs.
// Before each job, re-hash and report what changed.

function hashFile(filePath) {
  try {
    return createHash('md5').update(readFileSync(filePath)).digest('hex');
  } catch { return null; }
}

function walkDir(dir, base = dir) {
  const entries = [];
  if (!existsSync(dir)) return entries;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    const rel = relative(base, full);
    if (entry.isDirectory()) entries.push(...walkDir(full, base));
    else entries.push(rel);
  }
  return entries;
}

function createWatcher(dir) {
  const hashes = new Map();

  function snapshot() {
    if (!existsSync(dir)) return 0;
    const files = walkDir(dir);
    for (const rel of files) hashes.set(rel, hashFile(join(dir, rel)));
    return files.length;
  }

  function detectChanges() {
    const changes = { modified: [], added: [], removed: [] };
    if (!existsSync(dir)) return changes;

    const currentFiles = new Set(walkDir(dir));

    for (const rel of currentFiles) {
      const currentHash = hashFile(join(dir, rel));
      const prevHash = hashes.get(rel);
      if (!prevHash) {
        hashes.set(rel, currentHash);
        changes.added.push(rel);
      } else if (currentHash !== prevHash) {
        hashes.set(rel, currentHash);
        changes.modified.push(rel);
      }
    }

    for (const rel of hashes.keys()) {
      if (!currentFiles.has(rel)) {
        hashes.delete(rel);
        changes.removed.push(rel);
      }
    }

    return changes;
  }

  return { snapshot, detectChanges, dir };
}

const globalWatcher = createWatcher(AGENT_GLOBAL_DIR);
const teamWatcher = createWatcher(TEAM_GLOBAL_DIR);

// ─── State ───

let currentJob = null;
let jobCount = 0;
let claudeProcess = null;
let claudeReady = false;
let pendingResolve = null;
let resultBuffer = '';

// ─── Logging ───

function log(level, event, data = {}) {
  console.log(JSON.stringify({
    level, agent: AGENT_NAME,
    job_id: currentJob?.id || null,
    correlation_id: currentJob?.correlationId || null,
    event, pod_name: POD_NAME,
    timestamp: new Date().toISOString(),
    ...data,
  }));
}

// ─── Claude process management ───

function spawnClaude() {
  log('info', 'claude_spawn', {
    cwd: AGENT_PROJECT_DIR,
    provider: AGENT_PROVIDER,
    model: AGENT_MODEL,
    model_spec: AGENT_MODEL_SPEC,
    profile: PROFILE_DATA?.profile || 'none',
    backend_name: ACTIVE_BACKEND?.name || PROFILE_DATA?.backend_name || null,
    backend_selection: BACKEND_POOL?.selection || PROFILE_DATA?.selection || 'first'
  });

  // Build CLI arguments
  const cliArgs = [
    '--print',
    '--input-format', 'stream-json',
    '--output-format', 'stream-json',
    '--verbose',
    '--dangerously-skip-permissions',
  ];

  // Add provider flag based on profile or backward compatibility
  let effectiveProvider = AGENT_PROVIDER;
  let effectiveModel = AGENT_MODEL;

  if (PROFILE_DATA?.profile) {
    const profile = PROFILE_DATA.profile;
    if (profile === 'anthropic') {
      effectiveProvider = 'anthropic';
      effectiveModel = CLAUDE_MODEL;
    } else if (profile === 'openai' || profile === 'ollama') {
      effectiveProvider = 'openai';
      effectiveModel = MODEL_ENV.OPENAI_MODEL || effectiveModel;
    } else if (profile === 'gemini') {
      effectiveProvider = 'gemini';
      effectiveModel = MODEL_ENV.GEMINI_MODEL || effectiveModel;
    } else {
      effectiveProvider = profile;
      effectiveModel = effectiveModel;
    }
  }

  // Add provider and model flags for OpenClaude
  cliArgs.push('--provider', effectiveProvider);
  if (effectiveModel) {
    cliArgs.push('--model', effectiveModel);
  }

  // Prepare environment
  const env = {
    ...process.env,
    ...MODEL_ENV,
    CLAUDE_CODE_DISABLE_MEMORY: '1',
    KAFKAJS_NO_PARTITIONER_WARNING: '1',
  };

  const proc = spawn('openclaude', cliArgs, {
    cwd: AGENT_PROJECT_DIR,
    env,
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  // Parse stdout line by line (stream-json is newline-delimited JSON)
  const rl = createInterface({ input: proc.stdout });
  rl.on('line', (line) => {
    if (!line.trim()) return;
    try {
      const event = JSON.parse(line);
      handleClaudeEvent(event);
    } catch {
      // Non-JSON output (e.g., startup messages) — log it
      log('debug', 'claude_raw', { line: line.slice(0, 200) });
    }
  });

  // Log stderr
  proc.stderr.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) log('debug', 'claude_stderr', { text: text.slice(0, 500) });
  });

  proc.on('exit', (code, signal) => {
    log('warn', 'claude_exited', { code, signal });
    claudeReady = false;

    // Reject pending job if any
    if (pendingResolve) {
      pendingResolve({ text: `Claude exited (code=${code}, signal=${signal})`, is_error: true });
      pendingResolve = null;
      resultBuffer = '';
    }

    // Respawn after delay
    setTimeout(() => {
      log('info', 'claude_respawn');
      claudeProcess = spawnClaude();
    }, RESPAWN_DELAY_MS);
  });

  proc.on('error', (err) => {
    log('error', 'claude_spawn_error', { error: err.message });
  });

  // claudeReady is set true only when the 'system' event arrives
  return proc;
}

function handleClaudeEvent(event) {
  switch (event.type) {
    case 'system':
      // System init message — Claude is ready
      log('info', 'claude_ready', { session_id: event.session_id });
      claudeReady = true;
      break;

    case 'assistant':
      // Assistant message — extract text content
      if (event.message?.content) {
        for (const block of event.message.content) {
          if (block.type === 'text') resultBuffer += block.text;
        }
      }
      break;

    case 'result':
      // Turn complete — resolve pending promise
      const text = resultBuffer || event.result || '';
      const isError = event.is_error || false;
      if (pendingResolve) {
        pendingResolve({ text, is_error: isError });
        pendingResolve = null;
      }
      resultBuffer = '';
      break;

    default:
      // Other events (tool_use, tool_result, etc.) — ignore for result collection
      break;
  }
}

function sendMessage(prompt) {
  return new Promise((resolve, reject) => {
    if (!claudeProcess || !claudeReady) {
      return reject(new Error('Claude not ready'));
    }

    pendingResolve = resolve;
    resultBuffer = '';

    const msg = JSON.stringify({
      type: 'user',
      message: { role: 'user', content: prompt },
    });

    try {
      claudeProcess.stdin.write(msg + '\n');
    } catch (e) {
      pendingResolve = null;
      reject(new Error(`Failed to write to Claude stdin: ${e.message}`));
    }
  });
}

// ─── Kafka ───

const kafka = new Kafka({
  clientId: `agent-${AGENT_NAME}-${POD_NAME}`,
  brokers: KAFKA_BROKERS,
  retry: { retries: 5, initialRetryTime: 1000 },
});

const consumer = kafka.consumer({
  groupId: `agent-${AGENT_NAME}`,
  sessionTimeout: 2100000,     // 35 min — must exceed max job duration
  heartbeatInterval: 30000,    // 30s heartbeats
  rebalanceTimeout: 120000,    // 2 min for rebalance
  maxWaitTimeInMs: 5000,
});
const producer = kafka.producer();

async function processJob(message) {
  let job;
  try {
    job = JSON.parse(message.value.toString());
  } catch (e) {
    log('error', 'job_parse_failed', { error: e.message });
    return;
  }

  currentJob = {
    id: job.id,
    correlationId: job.correlation_id,
    startedAt: new Date().toISOString(),
  };

  jobCount++;
  log('info', 'job_start', { skill: job.skill, job_number: jobCount });

  const startTime = Date.now();
  let status = 'success';
  let output = '';

  try {
    // Detect memory changes since last job
    let memoryRefresh = '';
    const globalChanges = globalWatcher.detectChanges();
    const teamChanges = teamWatcher.detectChanges();

    const allLines = [];
    for (const f of globalChanges.modified) allLines.push(`- ${AGENT_GLOBAL_DIR}/${f} (updated — re-read this file)`);
    for (const f of globalChanges.added) allLines.push(`- ${AGENT_GLOBAL_DIR}/${f} (new — read this file)`);
    for (const f of globalChanges.removed) allLines.push(`- ${f} (removed from global memory — disregard previous content)`);
    for (const f of teamChanges.modified) allLines.push(`- ${TEAM_GLOBAL_DIR}/${f} (updated — re-read this file)`);
    for (const f of teamChanges.added) allLines.push(`- ${TEAM_GLOBAL_DIR}/${f} (new — read this file)`);
    for (const f of teamChanges.removed) allLines.push(`- ${f} (removed from team memory — disregard)`);

    if (allLines.length) {
      memoryRefresh = `\nMemory changes since your last job:\n${allLines.join('\n')}\n`;
      log('info', 'memory_changes', {
        global: { modified: globalChanges.modified.length, added: globalChanges.added.length, removed: globalChanges.removed.length },
        team: { modified: teamChanges.modified.length, added: teamChanges.added.length, removed: teamChanges.removed.length },
      });
    }

    // Clone project repo if not already present
    if (job.project) {
      const projPath = `${PROJECTS_ROOT}/${job.project}`;
      if (!existsSync(projPath)) {
        if (job.repo) {
          log('info', 'cloning_repo', { repo: job.repo, dest: projPath });
          try {
            mkdirSync(PROJECTS_ROOT, { recursive: true });
            execSync(`cd /tmp && git clone --depth 1 ${job.repo} clone-${job.project} && mv clone-${job.project} ${projPath}`, { timeout: 120000 });
          } catch (e) {
            throw new Error(`Failed to clone ${job.repo}: ${e.message}`);
          }
        } else {
          throw new Error(`Project not found: ${projPath}. Provide "repo" field to clone.`);
        }
      }
    }

    // Generic preflight: if /kord/agents/<name>/preflight.sh exists, run it.
    // Receives job JSON on stdin. If stdout starts with "SKIP:", return immediately.
    const preflightScript = `${AGENT_PROJECT_DIR}/preflight.sh`;
    if (existsSync(preflightScript)) {
      try {
        const preflightResult = execSync(`bash ${preflightScript}`, {
          input: JSON.stringify(job),
          encoding: 'utf8',
          timeout: 30000,
          env: { ...process.env, PROJECTS_ROOT, AGENT_PROJECT_DIR },
        }).trim();
        if (preflightResult.startsWith('SKIP:')) {
          const skipMsg = preflightResult.slice(5).trim();
          log('info', 'preflight_skip', { message: skipMsg });
          try {
            await producer.send({
              topic: 'jobs.result',
              messages: [{ key: job.correlation_id, value: JSON.stringify({
                id: randomUUID(), correlation_id: job.correlation_id, agent: AGENT_NAME,
                skill: job.skill, status: 'success', output: skipMsg,
                started_at: currentJob.startedAt, finished_at: new Date().toISOString(),
                pod_name: POD_NAME, job_number: jobCount, preflight: true,
              }) }],
            });
          } catch (e) { log('error', 'result_publish_failed', { error: e.message }); }
          currentJob = null;
          return;
        }
      } catch (e) {
        log('debug', 'preflight_error', { error: e.message });
      }
    }

    // Inject memory paths so skills don't hardcode them
    let context = `\n[Memory]\n`
      + `Global: ${AGENT_GLOBAL_DIR}/\n`
      + `Team: ${TEAM_GLOBAL_DIR}/\n`;
    if (job.project) {
      const projMemPath = `${AGENT_PROJECT_DIR}/memory/projects/${job.project}`;
      context += `Project: ${projMemPath}/\n`
        + `Project code: ${PROJECTS_ROOT}/${job.project}\n`
        + `Read the files in ${projMemPath}/ for your prior findings on this project (if the directory exists).\n`;
    }

    const backendContext = `\n[Backend]\nName: ${ACTIVE_BACKEND?.name || PROFILE_DATA?.backend_name || 'unknown'}\nProfile: ${PROFILE_DATA?.profile || 'unknown'}\nProvider: ${AGENT_PROVIDER}\nModel: ${AGENT_MODEL}\nSelection: ${BACKEND_POOL?.selection || PROFILE_DATA?.selection || 'first'}\n`;
    const prompt = memoryRefresh + job.prompt + context + backendContext + `\n[Job ${job.id}]`;

    if (currentJob) {
      currentJob.backend = {
        name: ACTIVE_BACKEND?.name || PROFILE_DATA?.backend_name || null,
        profile: PROFILE_DATA?.profile || null,
        provider: AGENT_PROVIDER,
        model: AGENT_MODEL,
        selection: BACKEND_POOL?.selection || PROFILE_DATA?.selection || 'first',
      };
    }

    // Send job to Claude and wait for result
    const timeoutMs = job.timeout_ms || DEFAULT_TIMEOUT_MS;
    const result = await Promise.race([
      sendMessage(prompt),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error(`Job timed out after ${timeoutMs}ms`)), timeoutMs)
      ),
    ]);

    output = result.text;
    if (result.is_error) {
      status = 'error';
      log('error', 'job_error', { duration_ms: Date.now() - startTime });
    } else {
      log('info', 'job_complete', { duration_ms: Date.now() - startTime, job_number: jobCount });
    }

    // Second turn: reflection (only on successful jobs)
    if (status === 'success' && REFLECTION_PROMPT) {
      try {
        let reflectionCtx = REFLECTION_PROMPT;
        if (job.project) {
          reflectionCtx = reflectionCtx
            .replace('{{PROJECT}}', job.project)
            .replace('{{NO_PROJECT_NOTICE}}', '');
        } else {
          reflectionCtx = reflectionCtx
            .replace('{{PROJECT}}', '')
            .replace('{{NO_PROJECT_NOTICE}}', 'No project context for this job. Only save global insights (scope: global). Skip project-scoped reflections.');
        }
        reflectionCtx += `\n\nBackend attribution for this job: ${ACTIVE_BACKEND?.name || PROFILE_DATA?.backend_name || 'unknown'} | ${PROFILE_DATA?.profile || 'unknown'} | ${AGENT_MODEL}`;
        await Promise.race([
          sendMessage(reflectionCtx),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Reflection timed out')), 120_000)
          ),
        ]);
        log('info', 'reflection_complete', { job_id: job.id });
      } catch (e) {
        log('warn', 'reflection_failed', { error: e.message });
      }
    }
  } catch (e) {
    if (e.message.includes('timed out')) status = 'timeout';
    else if (e.message.includes('exited') || e.message.includes('SIGTERM')) status = 'cancelled';
    else status = 'error';
    output = e.message;
    log(status === 'cancelled' ? 'info' : 'error', 'job_failed', { status, error: e.message, duration_ms: Date.now() - startTime });
  }

  // Produce result to Kafka
  const result = {
    id: randomUUID(),
    correlation_id: job.correlation_id,
    agent: AGENT_NAME,
    skill: job.skill || null,
    status,
    output,
    started_at: currentJob.startedAt,
    finished_at: new Date().toISOString(),
    pod_name: POD_NAME,
    job_number: jobCount,
    backend: {
      name: ACTIVE_BACKEND?.name || PROFILE_DATA?.backend_name || null,
      profile: PROFILE_DATA?.profile || null,
      provider: AGENT_PROVIDER,
      model: AGENT_MODEL,
      model_spec: AGENT_MODEL_SPEC,
      selection: BACKEND_POOL?.selection || PROFILE_DATA?.selection || 'first',
    },
  };

  try {
    await producer.send({
      topic: 'jobs.result',
      messages: [{ key: job.correlation_id, value: JSON.stringify(result) }],
    });
  } catch (e) {
    log('error', 'result_publish_failed', { error: e.message });
  }

  currentJob = null;
}

// ─── Status server ───

const statusServer = createServer((req, res) => {
  if (req.url === '/status' && req.method === 'GET') {
    const body = currentJob
      ? { state: 'busy', job_id: currentJob.id, since: currentJob.startedAt, jobs_completed: jobCount - 1 }
      : { state: 'idle', claude_ready: claudeReady, jobs_completed: jobCount };
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(body));

  } else if (req.url === '/cancel' && req.method === 'POST') {
    // Cancel the current job — kills Claude process, reports cancelled
    if (!currentJob) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ cancelled: false, reason: 'no active job' }));
      return;
    }
    const cancelledJobId = currentJob.id;
    log('info', 'job_cancelled', { job_id: cancelledJobId });
    // Kill Claude — sendMessage promise will reject, processJob catches it
    if (claudeProcess) claudeProcess.kill('SIGTERM');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ cancelled: true, job_id: cancelledJobId }));

  } else if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(claudeReady ? 200 : 503);
    res.end(claudeReady ? 'ok' : 'claude not ready');

  } else if (req.url === '/memory-update' && req.method === 'POST') {
    // Used by agents (via curl in reflection) to publish memory updates to Kafka
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', async () => {
      try {
        const update = JSON.parse(body);
        await producer.send({
          topic: `memory.updates.${AGENT_NAME}`,
          messages: [{ key: update.path, value: JSON.stringify(update) }],
        });
        res.writeHead(200);
        res.end('queued');
      } catch (e) {
        res.writeHead(500);
        res.end(e.message);
      }
    });

  } else {
    res.writeHead(404);
    res.end('not found');
  }
});

// ─── Main ───

async function main() {
  log('info', 'agent_boot', { brokers: KAFKA_BROKERS, project_dir: AGENT_PROJECT_DIR, model: CLAUDE_MODEL });

  // Start status server
  statusServer.listen(STATUS_PORT, () => {
    log('info', 'status_server_ready', { port: STATUS_PORT });
  });

  // Snapshot memory hashes (Claude reads directly, no copies)
  const globalFiles = globalWatcher.snapshot();
  const teamFiles = teamWatcher.snapshot();
  log('info', 'memory_init', { global_files: globalFiles, team_files: teamFiles });

  // Spawn persistent Claude session
  claudeProcess = spawnClaude();

  // Send init message — Claude stream-json emits system event only after first input
  await new Promise(resolve => setTimeout(resolve, 1000));
  try {
    // Bypass claudeReady check — write directly to stdin to trigger system event
    const initMsg = JSON.stringify({
      type: 'user',
      message: { role: 'user', content: `You are booting up as the ${AGENT_NAME} agent. Your working directory is ${AGENT_PROJECT_DIR}. Read your CLAUDE.md to learn your identity and available skills. Then respond with "ready".` },
    });
    claudeProcess.stdin.write(initMsg + '\n');
    // Wait for the system event to set claudeReady
    for (let i = 0; i < 30 && !claudeReady; i++) {
      await new Promise(r => setTimeout(r, 1000));
    }
    if (claudeReady) {
      log('info', 'claude_boot_complete');
    } else {
      log('error', 'claude_boot_timeout');
    }
  } catch (e) {
    log('error', 'claude_init_failed', { error: e.message });
  }

  // Connect to Kafka
  await consumer.connect();
  await producer.connect();
  await consumer.subscribe({ topic: `jobs.${AGENT_NAME}`, fromBeginning: false });

  log('info', 'kafka_ready', { topic: `jobs.${AGENT_NAME}` });

  // Process one job at a time with manual offset commits.
  // Prevents duplicate processing during KEDA scale-up rebalances:
  // - autoCommit: false — offset only committed after job completes
  // - Pause during processing — leaves other messages for new pods
  // - If rebalance revokes our partition mid-job, we lose the job
  //   but the new consumer replays from the uncommitted offset
  const topic = `jobs.${AGENT_NAME}`;
  await consumer.run({
    autoCommit: false,
    eachMessage: async ({ message, partition }) => {
      // Wait for Claude to be ready (it may be respawning)
      let retries = 0;
      while (!claudeReady && retries < 30) {
        await new Promise(r => setTimeout(r, 1000));
        retries++;
      }
      if (!claudeReady) {
        log('error', 'claude_not_ready', { waited_seconds: retries });
        return;
      }
      // Pause consumption while processing — lets other pods take queued jobs
      consumer.pause([{ topic }]);
      try {
        await processJob(message);
        // Commit only after successful processing
        await consumer.commitOffsets([{
          topic,
          partition,
          offset: (Number(message.offset) + 1).toString(),
        }]);
        log('info', 'offset_committed', { partition, offset: message.offset });
      } finally {
        consumer.resume([{ topic }]);
      }
    },
  });
}

// ─── Shutdown ───

async function shutdown() {
  log('info', 'agent_shutdown', { jobs_completed: jobCount });
  try {
    if (claudeProcess) claudeProcess.kill('SIGTERM');
    await consumer.disconnect();
    await producer.disconnect();
  } catch {}
  statusServer.close();
  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

main().catch((e) => {
  log('error', 'agent_fatal', { error: e.message });
  process.exit(1);
});
