import assert from 'node:assert/strict'
import test from 'node:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import {
  listAugurAnalysisSummaries,
  loadAugurAnalysisDetails,
  loadAugurBase,
  loadAugurProjectSummary,
  loadAugurReflections,
  resolveAugurProjectNames,
} from './augur-base.js'

async function writeAcceptedAnalysis(root: string, project: string, sha: string, analysisId: string): Promise<string> {
  const analysisDir = join(root, project, 'analysis', sha, analysisId)
  await mkdir(join(analysisDir, 'stories'), { recursive: true })
  await mkdir(join(analysisDir, 'reflections'), { recursive: true })
  await writeFile(join(analysisDir, 'atlas.json'), JSON.stringify({
    project,
    purpose: 'Demo purpose',
    components: [{ id: 'svc', title: 'Service' }],
  }, null, 2))
  await writeFile(join(analysisDir, 'stories', 'svc.yaml'), 'id: svc\ntitle: Service\nsummary: Main story\n')
  await writeFile(join(analysisDir, 'narratives.yaml'), 'version: "1"\nnarratives:\n  - id: system-overview\n    title: Overview\n    stories: [svc]\n')
  await writeFile(join(analysisDir, 'log.json'), JSON.stringify({ log_type: 'validation', latest_status: 'valid' }, null, 2))
  await writeFile(join(analysisDir, 'reflections', 'index.json'), JSON.stringify({ analysis_id: analysisId, reflections: [{ id: 'r1' }] }, null, 2))
  await writeFile(join(analysisDir, 'meta.json'), JSON.stringify({
    request_id: 'req-1',
    repository: {
      project,
      commit: sha,
      commit_time: '123',
      base_commit: '',
      base_commit_time: '',
      file_count: 10,
      files_read_count: 3,
      repo_tokens_est: 240,
    },
    agent: {
      name: 'augur-opus',
      bundle_mode: 'selective',
    },
    analysis: {
      id: analysisId,
      mode: 'full',
      analyzed_at: '2026-04-18T16:24:54Z',
      blast: { mode: 'full', tier: 3, reasons: [], affected_components: [], affected_flows: [], affected_state: [], affected_dependencies: [], affected_concepts: [] },
      artifacts: {
        root: '.',
        atlas: 'atlas.json',
        facts_index: '',
        stories_dir: 'stories',
        narratives: 'narratives.yaml',
        blast: '',
        overlays_dir: 'overlays',
        overlays_index: 'overlays/index.json',
        reflections_dir: 'reflections',
        reflections_index: 'reflections/index.json',
      },
      schemas: { facts: '/facts', atlas: '/atlas', story: '/story', narratives: '/narratives', meta: '/meta' },
      inputs: {
        bundles: [],
        loaded_refs: [],
        artifacts: [],
        totals: { bundle_tokens_est: 0, loaded_ref_tokens_est: 0, artifact_tokens_est: 0, repo_tokens_est: 240, validation_tokens_est: 0, total_tokens_est: 240 },
      },
      validation: { passed: true, attempts: 2, token: '' },
    },
  }, null, 2))
  await writeFile(join(root, project, 'analysis', 'latest.json'), JSON.stringify({
    analysis_id: analysisId,
    analysis_dir: analysisDir,
    sha,
    commit_time: '123',
  }, null, 2))
  await writeFile(join(root, project, 'analysis', 'index.json'), JSON.stringify({
    project,
    analyses: [{
      analysis_id: analysisId,
      analysis_dir: analysisDir,
      project,
      sha,
      commit_time: '123',
      analyzed_at: '2026-04-18T16:24:54Z',
      request_id: 'req-1',
      repository: { project, commit: sha, commit_time: '123' },
      agent: { name: 'augur-opus', bundle_mode: 'selective' },
      validation: { passed: true },
    }],
  }, null, 2))
  return analysisDir
}

test('augur base loaders use accepted meta.json snapshots', async () => {
  const root = await mkdtemp(join(tmpdir(), 'augur-api-test-'))
  try {
    await writeAcceptedAnalysis(root, 'demo', 'abc123', '2026-04-18T16-24-54Z')

    assert.deepEqual(await resolveAugurProjectNames(root), ['demo'])

    const project = await loadAugurProjectSummary(root, 'demo')
    assert.ok(project)
    assert.equal(project.latest_analysis_id, '2026-04-18T16-24-54Z')
    assert.equal(project.latest_commit_sha, 'abc123')

    const analyses = await listAugurAnalysisSummaries(root, 'demo')
    assert.equal(analyses.length, 1)
    assert.equal(analyses[0].status, 'accepted')
    assert.equal(analyses[0].commit_time, '123')
    assert.equal(analyses[0].request_id, 'req-1')
    assert.deepEqual(analyses[0].agent, { name: 'augur-opus', bundle_mode: 'selective' })

    const details = await loadAugurAnalysisDetails(root, 'demo', '2026-04-18T16-24-54Z')
    assert.ok(details)
    assert.equal((details.meta.analysis as { id?: string }).id, '2026-04-18T16-24-54Z')
    assert.equal(details.artifacts.atlas, true)

    const base = await loadAugurBase(root, 'demo', '2026-04-18T16-24-54Z')
    assert.ok(base)
    assert.equal((base.meta.analysis as { id?: string }).id, '2026-04-18T16-24-54Z')
    assert.equal(Array.isArray(base.stories), true)
    assert.equal(base.stories.length, 1)
    assert.equal(Array.isArray(base.narratives), true)
    assert.equal(base.narratives.length, 1)

    const reflections = await loadAugurReflections(root, 'demo', '2026-04-18T16-24-54Z')
    assert.deepEqual(reflections, [{ id: 'r1' }])
  } finally {
    await rm(root, { recursive: true, force: true })
  }
})
