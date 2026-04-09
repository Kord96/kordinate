import assert from 'node:assert/strict';
import test from 'node:test';
import { getOpenClaudeBinaryConfig } from './runtime.js';
test('getOpenClaudeBinaryConfig defaults to npm-installed openclaude package', () => {
    const config = getOpenClaudeBinaryConfig({});
    assert.deepEqual(config, {
        command: 'openclaude',
        packageName: '@gitlawb/openclaude',
    });
});
test('getOpenClaudeBinaryConfig respects explicit overrides', () => {
    const config = getOpenClaudeBinaryConfig({
        OPENCLAUDE_BIN: '/custom/bin/openclaude',
        OPENCLAUDE_NPM_PACKAGE: '@example/openclaude-fork',
    });
    assert.deepEqual(config, {
        command: '/custom/bin/openclaude',
        packageName: '@example/openclaude-fork',
    });
});
