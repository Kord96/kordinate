import assert from 'node:assert/strict';
import test from 'node:test';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { listAugurAnalysisSummaries, loadAugurAnalysisDetails, loadAugurBase, loadAugurProjectSummary, loadAugurReflections, resolveAugurProjectNames, } from './augur-base.js';
async function writeAcceptedAnalysis(root, project, sha, analysisId) {
    const analysisDir = join(root, project, 'analysis', sha, analysisId);
    await mkdir(join(analysisDir, 'stories'), { recursive: true });
    await mkdir(join(analysisDir, 'reflections'), { recursive: true });
    await writeFile(join(analysisDir, 'atlas.json'), JSON.stringify({
        project,
        purpose: 'Demo purpose',
        components: [{ id: 'svc', title: 'Service' }],
    }, null, 2));
    await writeFile(join(analysisDir, 'stories', 'svc.yaml'), 'id: svc\ntitle: Service\nsummary: Main story\n');
    await writeFile(join(analysisDir, 'narratives.yaml'), 'version: "1"\nnarratives:\n  - id: getting-started\n    title: Getting Started\n    stories: [svc]\n');
    await writeFile(join(analysisDir, 'repair-log.json'), JSON.stringify({ latest_status: 'valid' }, null, 2));
    await writeFile(join(analysisDir, 'reflections', 'index.json'), JSON.stringify({ analysis_id: analysisId, reflections: [{ id: 'r1' }] }, null, 2));
    await writeFile(join(analysisDir, 'meta.json'), JSON.stringify({
        project,
        analysis_id: analysisId,
        sha,
        commit_time: '123',
        analysis_mode: 'full',
        base_sha: '',
        base_commit_time: '',
        analyzed_at: '2026-04-18T16:24:54Z',
        blast: { mode: 'full', tier: 3, reasons: [], affected_components: [], affected_flows: [], affected_state: [], affected_dependencies: [], affected_concepts: [] },
        artifacts: {
            root: analysisDir,
            atlas: join(analysisDir, 'atlas.json'),
            facts_index: '',
            stories_dir: join(analysisDir, 'stories'),
            narratives: join(analysisDir, 'narratives.yaml'),
            blast: '',
            overlays_dir: join(analysisDir, 'overlays'),
            overlays_index: join(analysisDir, 'overlays', 'index.json'),
            reflections_dir: join(analysisDir, 'reflections'),
            reflections_index: join(analysisDir, 'reflections', 'index.json'),
        },
        schemas: { facts: '/facts', atlas: '/atlas', story: '/story', narratives: '/narratives', meta: '/meta' },
        execution: {},
        validation: { passed: true, attempts: 2, token: '' },
    }, null, 2));
    await writeFile(join(root, project, 'analysis', 'latest.json'), JSON.stringify({
        analysis_id: analysisId,
        analysis_dir: analysisDir,
        sha,
        commit_time: '123',
    }, null, 2));
    await writeFile(join(root, project, 'analysis', 'index.json'), JSON.stringify({
        project,
        analyses: [{
                analysis_id: analysisId,
                analysis_dir: analysisDir,
                project,
                sha,
                commit_time: '123',
                analyzed_at: '2026-04-18T16:24:54Z',
                validation: { passed: true },
            }],
    }, null, 2));
    return analysisDir;
}
test('augur base loaders use accepted meta.json snapshots', async () => {
    const root = await mkdtemp(join(tmpdir(), 'augur-api-test-'));
    try {
        await writeAcceptedAnalysis(root, 'demo', 'abc123', '2026-04-18T16-24-54Z');
        assert.deepEqual(await resolveAugurProjectNames(root), ['demo']);
        const project = await loadAugurProjectSummary(root, 'demo');
        assert.ok(project);
        assert.equal(project.latest_analysis_id, '2026-04-18T16-24-54Z');
        assert.equal(project.latest_commit_sha, 'abc123');
        const analyses = await listAugurAnalysisSummaries(root, 'demo');
        assert.equal(analyses.length, 1);
        assert.equal(analyses[0].status, 'accepted');
        const details = await loadAugurAnalysisDetails(root, 'demo', '2026-04-18T16-24-54Z');
        assert.ok(details);
        assert.equal(details.meta.analysis_id, '2026-04-18T16-24-54Z');
        assert.equal(details.artifacts.atlas, true);
        const base = await loadAugurBase(root, 'demo', '2026-04-18T16-24-54Z');
        assert.ok(base);
        assert.equal(base.meta.analysis_id, '2026-04-18T16-24-54Z');
        assert.equal(Array.isArray(base.stories), true);
        assert.equal(base.stories.length, 1);
        assert.equal(Array.isArray(base.narratives), true);
        assert.equal(base.narratives.length, 1);
        const reflections = await loadAugurReflections(root, 'demo', '2026-04-18T16-24-54Z');
        assert.deepEqual(reflections, [{ id: 'r1' }]);
    }
    finally {
        await rm(root, { recursive: true, force: true });
    }
});
