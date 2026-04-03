// Test backend-pool selection + env hydration used by daemon.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const testAgentDir = '/tmp/test-openclaude-agent';
fs.mkdirSync(testAgentDir, { recursive: true });

const backends = {
  version: 2,
  selection: 'hash',
  backends: [
    {
      name: 'anthropic-primary',
      profile: 'anthropic',
      provider: 'anthropic',
      model: 'claude-sonnet-4-6',
      api_key_env: 'ANTHROPIC_API_KEY'
    },
    {
      name: 'deepseek-chat',
      profile: 'openai',
      provider: 'openai',
      model: 'deepseek-chat',
      base_url: 'https://api.deepseek.com',
      api_key_env: 'DEEPSEEK_API_KEY'
    }
  ]
};

fs.writeFileSync(path.join(testAgentDir, '.openclaude-backends.json'), JSON.stringify(backends, null, 2));
fs.writeFileSync(path.join(testAgentDir, '.openclaude-profile.json'), JSON.stringify({
  version: 2,
  selection: 'hash',
  backend_name: 'anthropic-primary',
  profile: 'anthropic',
  provider: 'anthropic',
  model: 'claude-sonnet-4-6',
  createdAt: new Date().toISOString()
}, null, 2));

function selectBackend(pool, podName) {
  if (pool.selection === 'random') {
    return pool.backends[Math.floor(Math.random() * pool.backends.length)];
  }
  if (pool.selection === 'hash') {
    const seed = crypto.createHash('md5').update(String(podName)).digest('hex');
    const index = parseInt(seed.slice(0, 8), 16) % pool.backends.length;
    return pool.backends[index];
  }
  return pool.backends[0];
}

function resolveBackendEnv(backend, env) {
  const resolved = {};
  if (backend.base_url) {
    if (backend.profile === 'gemini') resolved.GEMINI_BASE_URL = backend.base_url;
    else resolved.OPENAI_BASE_URL = backend.base_url;
  }
  if (backend.model) {
    if (backend.profile === 'anthropic') resolved.MODEL = backend.model;
    else if (backend.profile === 'gemini') resolved.GEMINI_MODEL = backend.model;
    else resolved.OPENAI_MODEL = backend.model;
  }
  if (backend.api_key_env && env[backend.api_key_env]) {
    if (backend.profile === 'anthropic') resolved.ANTHROPIC_API_KEY = env[backend.api_key_env];
    else if (backend.profile === 'gemini') resolved.GEMINI_API_KEY = env[backend.api_key_env];
    else resolved.OPENAI_API_KEY = env[backend.api_key_env];
  }
  return resolved;
}

const podName = process.argv[2] || 'agent-augur-7f6c9d4b7b-abcde';
const selected = selectBackend(backends, podName);
const env = resolveBackendEnv(selected, {
  ANTHROPIC_API_KEY: 'anthropic-test-key',
  DEEPSEEK_API_KEY: 'deepseek-test-key'
});

console.log('Pod:', podName);
console.log('Selected backend:', selected.name);
console.log('Profile:', selected.profile);
console.log('Provider:', selected.provider);
console.log('Model:', selected.model);
console.log('Resolved env:', JSON.stringify(env, null, 2));
console.log('CLI:', ['openclaude', '--provider', selected.profile === 'ollama' ? 'openai' : selected.provider, '--model', selected.model].join(' '));
console.log('\n✅ Backend selection test completed successfully');
