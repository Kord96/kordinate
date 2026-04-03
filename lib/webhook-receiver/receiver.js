#!/usr/bin/env node
// Webhook Receiver — lightweight GitHub push-event gateway.
//
// Deterministic gates decide whether a push triggers a build:
//   1. Branch filter   — only main
//   2. Path filter     — skip docs-only changes
//   3. Cooldown        — 2-minute per-repo dedup
//   4. Dep detection   — flag dependency changes for full rebuild
//
// If deps changed: POST to job-router to delegate to charon.
// If code-only:    log "git-sync will handle" and skip.

import express from 'express';
import { createHmac, timingSafeEqual } from 'node:crypto';

const PORT = parseInt(process.env.PORT || '8080');
const WEBHOOK_SECRET = process.env.GITHUB_WEBHOOK_SECRET || '';
const JOB_ROUTER_URL = process.env.JOB_ROUTER_URL || 'http://job-router.kord.svc.cluster.local:3100';
const BOOT_TIME = new Date().toISOString();

const DOCS_PATTERN = /\.(md|txt|png|jpg)$/;
const DEP_FILES = new Set([
  'package.json', 'package-lock.json',
  'requirements.txt', 'Pipfile',
  'go.mod', 'Dockerfile',
]);
const COOLDOWN_MS = 2 * 60 * 1000;

// repo -> timestamp of last triggered build
const cooldowns = new Map();

// Ring buffer of recent events for /status
const recentEvents = [];
const MAX_EVENTS = 50;

function log(msg, data) {
  const entry = { level: 'info', component: 'webhook-receiver', event: msg, timestamp: new Date().toISOString(), ...data };
  console.log(JSON.stringify(entry));
}

function record(event) {
  recentEvents.push({ ...event, timestamp: new Date().toISOString() });
  if (recentEvents.length > MAX_EVENTS) recentEvents.shift();
}

// ─── Signature verification ───

function verifySignature(payload, signature) {
  if (!WEBHOOK_SECRET) return true; // no secret configured — accept all
  if (!signature) return false;
  const expected = 'sha256=' + createHmac('sha256', WEBHOOK_SECRET).update(payload).digest('hex');
  if (expected.length !== signature.length) return false;
  return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}

// ─── Gate logic ───

function extractChangedFiles(commits) {
  const files = new Set();
  for (const c of commits || []) {
    for (const f of c.added || []) files.add(f);
    for (const f of c.modified || []) files.add(f);
    for (const f of c.removed || []) files.add(f);
  }
  return [...files];
}

function isDocsOnly(files) {
  return files.length > 0 && files.every(f => DOCS_PATTERN.test(f));
}

function hasDependencyChange(files) {
  return files.some(f => {
    const basename = f.split('/').pop();
    return DEP_FILES.has(basename);
  });
}

function isOnCooldown(repo) {
  const last = cooldowns.get(repo);
  if (!last) return false;
  return (Date.now() - last) < COOLDOWN_MS;
}

// ─── Express app ───

const app = express();

// Capture raw body for signature verification, then parse JSON
app.use(express.json({
  limit: '1mb',
  verify: (req, _res, buf) => { req.rawBody = buf; },
}));

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', name: 'webhook-receiver', boot: BOOT_TIME });
});

app.get('/status', (_req, res) => {
  res.json({ name: 'webhook-receiver', boot: BOOT_TIME, recent_events: recentEvents });
});

app.post('/webhook', async (req, res) => {
  const ghEvent = req.headers['x-github-event'];
  const signature = req.headers['x-hub-signature-256'];

  // Only handle push events
  if (ghEvent !== 'push') {
    record({ type: 'ignored', reason: `event type: ${ghEvent}` });
    return res.json({ status: 'ignored', reason: `unhandled event: ${ghEvent}` });
  }

  // Verify signature
  if (!verifySignature(req.rawBody, signature)) {
    log('Signature verification failed');
    return res.status(401).json({ error: 'invalid signature' });
  }

  const body = req.body;
  const ref = body.ref || '';
  const repo = body.repository?.full_name || 'unknown';
  const cloneUrl = body.repository?.clone_url || '';
  const repoName = body.repository?.name || repo.split('/').pop();

  // Gate 1: Branch filter
  if (ref !== 'refs/heads/main') {
    const result = { type: 'skipped', repo, reason: `branch: ${ref}` };
    record(result); log('Skip: not main', result);
    return res.json({ status: 'skipped', reason: 'not main branch' });
  }

  const files = extractChangedFiles(body.commits);

  // Gate 2: Docs-only filter
  if (isDocsOnly(files)) {
    const result = { type: 'skipped', repo, reason: 'docs only', files_count: files.length };
    record(result); log('Skip: docs only', result);
    return res.json({ status: 'skipped', reason: 'docs only' });
  }

  // Gate 3: Cooldown
  if (isOnCooldown(repo)) {
    const result = { type: 'skipped', repo, reason: 'cooldown' };
    record(result); log('Skip: cooldown', result);
    return res.json({ status: 'skipped', reason: 'cooldown — build recently triggered' });
  }

  // Gate 4: Dependency change detection
  const needsRebuild = hasDependencyChange(files);

  if (!needsRebuild) {
    const result = { type: 'skipped', repo, reason: 'code only — git-sync will handle', files_count: files.length };
    record(result); log('git-sync will handle', result);
    return res.json({ status: 'skipped', reason: 'git-sync will handle' });
  }

  // Dependency change — delegate to charon via job-router
  cooldowns.set(repo, Date.now());

  const payload = {
    agent: 'charon',
    prompt: `Build and deploy ${repoName} to dev`,
    project: repoName,
    repo: cloneUrl,
  };

  log('Delegating to charon', { repo, files_changed: files.length, needs_rebuild: true });
  record({ type: 'delegated', repo, agent: 'charon', needs_rebuild: true, files_count: files.length });

  try {
    const resp = await fetch(`${JOB_ROUTER_URL}/api/delegate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await resp.json();
    log('Delegation response', { repo, status: resp.status, job_id: result.job_id });
    return res.json({ status: 'delegated', agent: 'charon', job_id: result.job_id });
  } catch (err) {
    log('Delegation failed', { repo, error: err.message });
    return res.status(502).json({ status: 'error', error: `delegation failed: ${err.message}` });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  log('Webhook receiver started', { port: PORT, job_router: JOB_ROUTER_URL });
});
