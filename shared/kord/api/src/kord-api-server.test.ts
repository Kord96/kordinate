import assert from 'node:assert/strict'
import test from 'node:test'
import { mkdir, rm } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { canonicalizeWorkingDir } from './working-dir.js'

test('canonicalizeWorkingDir prefers existing PROJECTS_ROOT repo paths', async () => {
  const root = join(tmpdir(), `kord-api-test-${Date.now()}`)
  const projectsRoot = join(root, 'repos')
  const repoPath = join(projectsRoot, 'demo')
  await mkdir(repoPath, { recursive: true })
  const previousProjectsRoot = process.env.PROJECTS_ROOT
  try {
    process.env.PROJECTS_ROOT = projectsRoot
    const value = canonicalizeWorkingDir('/kord/workstation/home/project/demo')
    assert.equal(value, repoPath)
  } finally {
    if (previousProjectsRoot === undefined) delete process.env.PROJECTS_ROOT
    else process.env.PROJECTS_ROOT = previousProjectsRoot
    await rm(root, { recursive: true, force: true })
  }
})

test('canonicalizeWorkingDir falls back to KORDINATE_HOME for the kordinate repo', async () => {
  const previousProjectsRoot = process.env.PROJECTS_ROOT
  const previousKordinateHome = process.env.KORDINATE_HOME
  try {
    delete process.env.PROJECTS_ROOT
    process.env.KORDINATE_HOME = '/kord/workstation/home/project/kordinate'
    const value = canonicalizeWorkingDir('/kord/workstation/home/project/kordinate/shared/kord/api')
    assert.equal(value, '/kord/workstation/home/project/kordinate/shared/kord/api')
  } finally {
    if (previousProjectsRoot === undefined) delete process.env.PROJECTS_ROOT
    else process.env.PROJECTS_ROOT = previousProjectsRoot
    if (previousKordinateHome === undefined) delete process.env.KORDINATE_HOME
    else process.env.KORDINATE_HOME = previousKordinateHome
  }
})
