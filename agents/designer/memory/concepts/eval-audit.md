# AST-Grep Rule Eval Audit

Generated: 2026-03-27T03:37:20Z
Suspects: 49

## Suspects

### decorator in django (6331 matches)
**Reason:** very high count (6331); 2110x vs nextjs (3)
**Rule file:** `decorator/ast-grep.yaml`

**Sample matches:**
- `tests/str/tests.py:18` (rule: python-decorator)
  ```
  @isolate_apps("str")
  ```
- `tests/sitemaps_tests/test_https.py:8` (rule: python-decorator)
  ```
  @override_settings(ROOT_URLCONF="sitemaps_tests.urls.https")
  ```
- `tests/sitemaps_tests/test_https.py:42` (rule: python-decorator)
  ```
  @override_settings(SECURE_PROXY_SSL_HEADER=False)
  ```
- `tests/or_lookups/tests.py:11` (rule: python-decorator)
  ```
  @classmethod
  ```
- `tests/xor_lookups/tests.py:8` (rule: python-decorator)
  ```
  @classmethod
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### active-record in django (3292 matches)
**Reason:** very high count (3292)
**Rule file:** `active-record/ast-grep.yaml`

**Sample matches:**
- `tests/inline_formsets/models.py:4` (rule: django-model)
  ```
  class School(models.Model):
  ```
- `tests/inline_formsets/models.py:8` (rule: django-model)
  ```
  class Parent(models.Model):
  ```
- `tests/inline_formsets/models.py:12` (rule: django-model)
  ```
  class Child(models.Model):
  ```
- `tests/inline_formsets/models.py:24` (rule: django-model)
  ```
  class Poet(models.Model):
  ```
- `tests/inline_formsets/models.py:31` (rule: django-model)
  ```
  class Poem(models.Model):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### input-validation in nextjs (1229 matches)
**Reason:** very high count (1229); 410x vs django (3)
**Rule file:** `input-validation/ast-grep.yaml`

**Sample matches:**
- `scripts/pack-utils/patch-package-json.ts:57` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(content)
  ```
- `scripts/pack-utils/patch-package-json.ts:125` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(content)
  ```
- `scripts/pack-utils/patch-package-json.ts:186` (rule: validation-zod-parse-ts)
  ```
  path.parse(currentDir)
  ```
- `packages/next/src/lib/patch-incorrect-lockfile.ts:57` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(content)
  ```
- `packages/next-env/index.ts:71` (rule: validation-zod-parse-ts)
  ```
  dotenv.parse(envFile.contents)
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### snapshot-testing in nextjs (1067 matches)
**Reason:** very high count (1067); 41x vs tanstack-query (26)
**Rule file:** `snapshot-testing/ast-grep.yaml`

**Sample matches:**
- `test/e2e/next-link-errors/next-link-errors.test.ts:62` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(await browser.elementByCss('body').text()).toMatchInlineSnapshot(
  ```
- `test/unit/babel-plugin-next-ssg-transform.test.ts:38` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(output).toMatchInlineSnapshot(
  ```
- `test/unit/babel-plugin-next-ssg-transform.test.ts:51` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(output).toMatchInlineSnapshot(
  ```
- `test/unit/babel-plugin-next-ssg-transform.test.ts:64` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(output).toMatchInlineSnapshot(
  ```
- `test/unit/babel-plugin-next-ssg-transform.test.ts:84` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(output).toMatchInlineSnapshot(
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### select-star in django (695 matches)
**Reason:** very high count (695); 695x vs nextjs (1)
**Rule file:** `select-star/ast-grep.yaml`

**Sample matches:**
- `tests/or_lookups/tests.py:58` (rule: select-star-objects-all-py)
  ```
  Article.objects.all()
  ```
- `tests/save_delete_hooks/tests.py:20` (rule: select-star-objects-all-py)
  ```
  Person.objects.all()
  ```
- `tests/save_delete_hooks/tests.py:37` (rule: select-star-objects-all-py)
  ```
  Person.objects.all()
  ```
- `tests/sitemaps_tests/test_http.py:276` (rule: select-star-objects-all-py)
  ```
  Site.objects.all()
  ```
- `tests/sitemaps_tests/test_generic.py:14` (rule: select-star-objects-all-py)
  ```
  TestModel.objects.all()
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### decorator in flask (660 matches)
**Reason:** very high count (660); 220x vs nextjs (3)
**Rule file:** `decorator/ast-grep.yaml`

**Sample matches:**
- `examples/javascript/tests/conftest.py:6` (rule: python-decorator)
  ```
  @pytest.fixture(name="app")
  ```
- `examples/javascript/tests/conftest.py:13` (rule: python-decorator)
  ```
  @pytest.fixture
  ```
- `examples/javascript/tests/test_js_example.py:5` (rule: python-decorator)
  ```
  @pytest.mark.parametrize(
  ```
- `examples/javascript/tests/test_js_example.py:22` (rule: python-decorator)
  ```
  @pytest.mark.parametrize(
  ```
- `tests/test_json_tag.py:12` (rule: python-decorator)
  ```
  @pytest.mark.parametrize(
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### batch-loader in nextjs (655 matches)
**Reason:** very high count (655); 34x vs trpc (19)
**Rule file:** `batch-loader/ast-grep.yaml`

**Sample matches:**
- `examples/with-segment-analytics/lib/segment.ts:3` (rule: batchloader-dataloader-load-ts)
  ```
  AnalyticsBrowser.load({
  ```
- `examples/with-segment-analytics-pages-router/lib/segment.ts:3` (rule: batchloader-dataloader-load-ts)
  ```
  AnalyticsBrowser.load({
  ```
- `test/lib/next-modes/base.ts:888` (rule: batchloader-dataloader-load-ts)
  ```
  cheerio.load(html)
  ```
- `packages/next-codemod/transforms/cra-to-next.ts:186` (rule: batchloader-dataloader-load-ts)
  ```
  cheerio.load(htmlContent)
  ```
- `test/development/jsconfig-path-reloading/index.test.ts:53` (rule: batchloader-dataloader-load-ts)
  ```
  cheerio.load(html)
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### lazy-loading in nextjs (565 matches)
**Reason:** very high count (565); 56x vs tanstack-query (10)
**Rule file:** `lazy-loading/ast-grep.yaml`

**Sample matches:**
- `packages/next/image-types/global.d.ts:5` (rule: lazy-loading-dynamic-import-ts)
  ```
  import('../dist/shared/lib/image-external')
  ```
- `packages/next/image-types/global.d.ts:22` (rule: lazy-loading-dynamic-import-ts)
  ```
  import('../dist/shared/lib/image-external')
  ```
- `packages/next/image-types/global.d.ts:28` (rule: lazy-loading-dynamic-import-ts)
  ```
  import('../dist/shared/lib/image-external')
  ```
- `packages/next/image-types/global.d.ts:34` (rule: lazy-loading-dynamic-import-ts)
  ```
  import('../dist/shared/lib/image-external')
  ```
- `packages/next/image-types/global.d.ts:40` (rule: lazy-loading-dynamic-import-ts)
  ```
  import('../dist/shared/lib/image-external')
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### batch-loader in django (469 matches)
**Reason:** high count (469); 25x vs trpc (19)
**Rule file:** `batch-loader/ast-grep.yaml`

**Sample matches:**
- `django/core/serializers/python.py:96` (rule: batchloader-select-related-py)
  ```
  getattr(obj, field.name).select_related(None)
  ```
- `django/core/serializers/xml_serializer.py:196` (rule: batchloader-select-related-py)
  ```
  getattr(obj, field.name).select_related(None)
  ```
- `django/contrib/admin/sites.py:605` (rule: batchloader-select-related-py)
  ```
  LogEntry.objects.select_related("content_type", "user")
  ```
- `django/contrib/auth/admin.py:36` (rule: batchloader-select-related-py)
  ```
  qs.select_related("content_type")
  ```
- `django/contrib/auth/forms.py:300` (rule: batchloader-select-related-py)
  ```
  user_permissions.queryset.select_related(
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### input-validation in trpc (327 matches)
**Reason:** high count (327); 109x vs django (3)
**Rule file:** `input-validation/ast-grep.yaml`

**Sample matches:**
- `scripts/version.ts:33` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(content)
  ```
- `vitest.config.ts:21` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(readFileSync(pkgJson, 'utf-8').toString())
  ```
- `packages/tests/showcase/tinyrpc.test.ts:30` (rule: validation-zod-schema-ts)
  ```
  z.object({
  ```
- `packages/tests/showcase/tinyrpc.test.ts:46` (rule: validation-zod-schema-ts)
  ```
  z.object({
  ```
- `scripts/entrypoints.ts:44` (rule: validation-zod-parse-ts)
  ```
  JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'))
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### aggregate in django (325 matches)
**Reason:** high count (325); 81x vs starlette (4)
**Rule file:** `aggregate/ast-grep.yaml`

**Sample matches:**
- `django/dispatch/dispatcher.py:140` (rule: aggregate-invariant-guard-py)
  ```
  if not callable(receiver):
  ```
- `django/dispatch/dispatcher.py:143` (rule: aggregate-invariant-guard-py)
  ```
  if not func_accepts_kwargs(receiver):
  ```
- `tests/contenttypes_tests/operations_migrations/0002_rename_foo.py:13` (rule: aggregate-invariant-guard-py)
  ```
  if not ContentType.objects.filter(
  ```
- `django/apps/registry.py:142` (rule: aggregate-invariant-guard-py)
  ```
  if not self.models_ready:
  ```
- `django/apps/registry.py:320` (rule: aggregate-invariant-guard-py)
  ```
  if not available.issubset(installed):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### feature-envy in django (319 matches)
**Reason:** high count (319); 319x vs flask (1)
**Rule file:** `feature-envy/ast-grep.yaml`

**Sample matches:**
- `docs/_ext/djangodocs.py:89` (rule: feature-envy-python-deep-chain)
  ```
  self.state.document.settings.env
  ```
- `docs/_ext/djangodocs.py:362` (rule: feature-envy-python-deep-chain)
  ```
  self.state.document.settings.env
  ```
- `django/contrib/sessions/migrations/0001_initial.py:34` (rule: feature-envy-python-deep-chain)
  ```
  django.contrib.sessions.models.SessionManager
  ```
- `django/contrib/auth/management/commands/createsuperuser.py:67` (rule: feature-envy-python-deep-chain)
  ```
  field.remote_field.through._meta.auto_created
  ```
- `django/contrib/auth/management/commands/createsuperuser.py:279` (rule: feature-envy-python-deep-chain)
  ```
  field.remote_field.model._meta.object_name
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### train-wreck in django (319 matches)
**Reason:** high count (319); 319x vs flask (1)
**Rule file:** `train-wreck/ast-grep.yaml`

**Sample matches:**
- `docs/_ext/djangodocs.py:89` (rule: train-wreck-deep-chain-py)
  ```
  self.state.document.settings.env
  ```
- `docs/_ext/djangodocs.py:362` (rule: train-wreck-deep-chain-py)
  ```
  self.state.document.settings.env
  ```
- `django/forms/boundfield.py:39` (rule: train-wreck-deep-chain-py)
  ```
  self.field.widget.attrs.get
  ```
- `django/forms/boundfield.py:308` (rule: train-wreck-deep-chain-py)
  ```
  self.field.widget.attrs.get
  ```
- `django/forms/boundfield.py:321` (rule: train-wreck-deep-chain-py)
  ```
  self.field.widget.__class__.__name__.lower
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### snapshot-testing in trpc (314 matches)
**Reason:** high count (314); 12x vs tanstack-query (26)
**Rule file:** `snapshot-testing/ast-grep.yaml`

**Sample matches:**
- `packages/tests/showcase/tinyrpc.test.ts:85` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(posts).toMatchInlineSnapshot(\`
  ```
- `packages/tests/server/regression/issue-4673-url-encoded-batching.test.ts:24` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(normalResult).toMatchInlineSnapshot(\`
  ```
- `packages/tests/server/regression/issue-4673-url-encoded-batching.test.ts:75` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(normalResult).toMatchInlineSnapshot(\`
  ```
- `packages/client/src/links/localLink.test.ts:281` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(ctx.onError.mock.calls).toMatchInlineSnapshot(\`
  ```
- `packages/client/src/links/localLink.test.ts:347` (rule: snapshot-toMatchInlineSnapshot-ts)
  ```
  expect(result).toMatchInlineSnapshot(\`
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### component-slot in nextjs (308 matches)
**Reason:** high count (308); 103x vs trpc (3)
**Rule file:** `component-slot/ast-grep.yaml`

**Sample matches:**
- `test/e2e/hello-world/hello-world.test.ts:22` (rule: slot-render-prop-ts)
  ```
  next.render('/')
  ```
- `test/e2e/transpile-packages-typescript-foreign/index.test.ts:21` (rule: slot-render-prop-ts)
  ```
  next.render('/')
  ```
- `test/e2e/dynamic-route-interpolation/index.test.ts:24` (rule: slot-render-prop-ts)
  ```
  next.render('/api/dynamic/[slug]')
  ```
- `test/e2e/dynamic-route-interpolation/index.test.ts:29` (rule: slot-render-prop-ts)
  ```
  next.render('/api/dynamic/[abc]')
  ```
- `test/e2e/disable-js-preload/test/index.test.ts:12` (rule: slot-render-prop-ts)
  ```
  next.render('/')
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### middleware in nextjs (304 matches)
**Reason:** high count (304); 22x vs fastapi-template (14)
**Rule file:** `middleware/ast-grep.yaml`

**Sample matches:**
- `scripts/pack-util.ts:22` (rule: middleware-express-handler-ts)
  ```
  function exec(title, command, opts?: ExecSyncOptionsWithStringEncoding) {
  ```
- `packages/next/src/lib/install-dependencies.ts:13` (rule: middleware-express-handler-ts)
  ```
  async function installDependencies(
  ```
- `bench/render-pipeline/analyze-profiles.ts:277` (rule: middleware-express-handler-ts)
  ```
  function printProfileAnalysis(
  ```
- `bench/render-pipeline/benchmark.ts:1026` (rule: middleware-koa-ts)
  ```
  async (signal: NodeJS.Signals, timeoutMs: number) => {
  ```
- `bench/render-pipeline/benchmark.ts:295` (rule: middleware-express-handler-ts)
  ```
  function fixedSizeChunkWithPrefix(prefix: Buffer, size: number, fill: number) {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### form-binding in django (236 matches)
**Reason:** high count (236)
**Rule file:** `form-binding/ast-grep.yaml`

**Sample matches:**
- `tests/model_inheritance_regress/tests.py:474` (rule: form-binding-modelform-py)
  ```
  class ProfileForm(forms.ModelForm):
  ```
- `tests/generic_views/forms.py:15` (rule: form-binding-formgroup-py)
  ```
  class ContactForm(forms.Form):
  ```
- `tests/generic_views/forms.py:20` (rule: form-binding-formgroup-py)
  ```
  class ConfirmDeleteForm(forms.Form):
  ```
- `tests/generic_views/forms.py:6` (rule: form-binding-modelform-py)
  ```
  class AuthorForm(forms.ModelForm):
  ```
- `tests/model_formsets/tests.py:494` (rule: form-binding-modelform-py)
  ```
  class PoetForm(forms.ModelForm):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### workflow-engine in nextjs (235 matches)
**Reason:** high count (235); 59x vs tanstack-query (4)
**Rule file:** `workflow-engine/ast-grep.yaml`

**Sample matches:**
- `evals/lib/setup.ts:12` (rule: workflow-temporal-ts)
  ```
  export async function installNextJs(sandbox: Sandbox): Promise<void> {
  ```
- `evals/lib/setup.ts:39` (rule: workflow-temporal-ts)
  ```
  export async function writeAgentsMd(sandbox: Sandbox): Promise<void> {
  ```
- `test/lib/e2e-utils/ppr.ts:19` (rule: workflow-temporal-ts)
  ```
  export async function splitResponseWithPPRSentinel(
  ```
- `scripts/pack-util.ts:141` (rule: workflow-temporal-ts)
  ```
  export async function packageFiles(path: string): Promise<string[]> {
  ```
- `test/lib/add-redbox-matchers.ts:284` (rule: workflow-temporal-ts)
  ```
  export async function createRedboxSnapshot(
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### component in nextjs (232 matches)
**Reason:** high count (232); 116x vs fastapi-template (2)
**Rule file:** `component/ast-grep.yaml`

**Sample matches:**
- `packages/create-next-app/index.ts:27` (rule: component-arrow-ts)
  ```
  const onPromptState = (state: {
  ```
- `packages/create-next-app/index.ts:296` (rule: component-arrow-ts)
  ```
  const formatSettingsDescription = (
  ```
- `packages/create-next-app/index.ts:392` (rule: component-arrow-ts)
  ```
  const getPrefOrDefault = (field: string) => {
  ```
- `packages/next-codemod/lib/agents-md.ts:623` (rule: component-arrow-ts)
  ```
  const parseVersion = (v: string) => {
  ```
- `packages/eslint-plugin-next/src/utils/get-root-dirs.ts:16` (rule: component-arrow-ts)
  ```
  const getRootDirs = (context: Rule.RuleContext) => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### websocket in django (228 matches)
**Reason:** high count (228); 228x vs tanstack-query (1)
**Rule file:** `websocket/ast-grep.yaml`

**Sample matches:**
- `django/dispatch/dispatcher.py:51` (rule: websocket-handler-py)
  ```
  async def run(i, coro):
  ```
- `django/dispatch/dispatcher.py:265` (rule: websocket-handler-py)
  ```
  async def asend(self, sender, **named):
  ```
- `django/dispatch/dispatcher.py:393` (rule: websocket-handler-py)
  ```
  async def asend_robust(self, sender, **named):
  ```
- `tests/decorators/test_cache.py:53` (rule: websocket-handler-py)
  ```
  async def async_view(self, request):
  ```
- `tests/decorators/test_cache.py:159` (rule: websocket-handler-py)
  ```
  async def test_never_cache_decorator_headers_async_view(self, mocked_time):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### decorator in starlette (153 matches)
**Reason:** high count (153); 51x vs nextjs (3)
**Rule file:** `decorator/ast-grep.yaml`

**Sample matches:**
- `tests/test_convertors.py:15` (rule: python-decorator)
  ```
  @pytest.fixture(scope="module", autouse=True)
  ```
- `tests/test_convertors.py:32` (rule: python-decorator)
  ```
  @pytest.fixture(scope="function")
  ```
- `tests/test_convertors.py:62` (rule: python-decorator)
  ```
  @pytest.mark.parametrize("param, status_code", [("1.0", 200), ("1-0", 404)])
  ```
- `tests/test_convertors.py:76` (rule: python-decorator)
  ```
  @pytest.mark.parametrize(
  ```
- `starlette/authentication.py:45` (rule: python-decorator)
  ```
  @functools.wraps(func)
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### error-code-returns in nextjs (129 matches)
**Reason:** high count (129); 64x vs django (2)
**Rule file:** `error-code-returns/ast-grep.yaml`

**Sample matches:**
- `apps/bundle-analyzer/lib/analyze-data.ts:332` (rule: error-code-check-null-ts)
  ```
  if (source.parent_source_index === null) {
  ```
- `test/lib/next-modes/next-start.ts:314` (rule: error-code-check-null-ts)
  ```
  if (this._prerenderFinishedTimeMS === null) {
  ```
- `test/lib/router-act.ts:147` (rule: error-code-check-null-ts)
  ```
  if (currentBatch === null) {
  ```
- `test/lib/router-act.ts:184` (rule: error-code-check-null-ts)
  ```
  if (forbiddenResponses === null) {
  ```
- `test/lib/router-act.ts:358` (rule: error-code-check-null-ts)
  ```
  if (expectedResponses === null) {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### test-doubles in nextjs (124 matches)
**Reason:** high count (124); 21x vs fastapi-template (6)
**Rule file:** `test-doubles/ast-grep.yaml`

**Sample matches:**
- `test/unit/image-optimizer/fetch-external-image.test.ts:10` (rule: testdouble-jest-fn-ts)
  ```
  jest.fn()
  ```
- `test/unit/image-optimizer/fetch-external-image.test.ts:15` (rule: testdouble-jest-fn-ts)
  ```
  jest.fn(() => null)
  ```
- `test/unit/image-optimizer/fetch-external-image.test.ts:37` (rule: testdouble-jest-fn-ts)
  ```
  jest.fn()
  ```
- `test/unit/image-optimizer/fetch-external-image.test.ts:55` (rule: testdouble-jest-fn-ts)
  ```
  jest.fn((header: string) => {
  ```
- `test/unit/image-optimizer/fetch-external-image.test.ts:79` (rule: testdouble-jest-fn-ts)
  ```
  jest.fn()
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### component in trpc (118 matches)
**Reason:** high count (118); 59x vs fastapi-template (2)
**Rule file:** `component/ast-grep.yaml`

**Sample matches:**
- `www/src/utils/handleSmoothScrollToSection.ts:1` (rule: component-arrow-ts)
  ```
  const handleSmoothScrollToSection = (
  ```
- `examples/next-prisma-websockets-starter/src/server/routers/post.ts:127` (rule: component-arrow-ts)
  ```
  const onAdd = (data: Post) => {
  ```
- `examples/next-sse-chat/src/app/channels/[channelId]/utils.ts:6` (rule: component-arrow-ts)
  ```
  const listWithAnd = (list: string[]) => {
  ```
- `www/src/components/sponsors/script.pull.ts:245` (rule: component-arrow-ts)
  ```
  const calculateWeight = (sponsors: typeof sortedSponsors) => {
  ```
- `examples/express-server/src/server.ts:7` (rule: component-arrow-ts)
  ```
  const createContext = ({
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### prototype in nextjs (113 matches)
**Reason:** high count (113); 38x vs bulletproof-react (3)
**Rule file:** `prototype/ast-grep.yaml`

**Sample matches:**
- `test/lib/next-modes/next-deploy.ts:296` (rule: prototype-spread-clone-ts)
  ```
  { ...process.env }
  ```
- `test/lib/next-modes/base.ts:384` (rule: prototype-spread-clone-ts)
  ```
  {
  ```
- `packages/create-next-app/helpers/typegen.ts:43` (rule: prototype-spread-clone-ts)
  ```
  {
  ```
- `turbopack/crates/turbopack-node/js/src/transforms/webpack-loaders-runtime.ts:49` (rule: prototype-object-create-ts)
  ```
  Object.create(realFs)
  ```
- `turbopack/crates/turbopack-ecmascript-runtime/js/src/browser/runtime/base/dev-base.ts:20` (rule: prototype-object-create-ts)
  ```
  Object.create(null)
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### train-wreck in trpc (98 matches)
**Reason:** 98x vs flask (1)
**Rule file:** `train-wreck/ast-grep.yaml`

**Sample matches:**
- `packages/react-query/test/createQueryUtils.test.ts:47` (rule: train-wreck-deep-chain-ts)
  ```
  factory.resolvers.postById.mock.calls.length
  ```
- `packages/react-query/test/createQueryUtils.test.ts:48` (rule: train-wreck-deep-chain-ts)
  ```
  factory.resolvers.postById.mock.calls
  ```
- `packages/react-query/test/createQueryUtils.test.ts:83` (rule: train-wreck-deep-chain-ts)
  ```
  factory.linkSpy.up.mock.calls
  ```
- `packages/react-query/test/createQueryUtils.test.ts:106` (rule: train-wreck-deep-chain-ts)
  ```
  factory.resolvers.postById.mock.calls.length
  ```
- `packages/react-query/test/createQueryUtils.test.ts:107` (rule: train-wreck-deep-chain-ts)
  ```
  factory.resolvers.postById.mock.calls
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### prototype in django (95 matches)
**Reason:** 32x vs bulletproof-react (3)
**Rule file:** `prototype/ast-grep.yaml`

**Sample matches:**
- `django/utils/module_loading.py:56` (rule: prototype-copy-py)
  ```
  copy.copy(register_to._registry)
  ```
- `tests/runtests.py:231` (rule: prototype-deepcopy-py)
  ```
  copy.deepcopy(DEFAULT_LOGGING)
  ```
- `django/utils/datastructures.py:198` (rule: prototype-copy-py)
  ```
  copy.copy(self)
  ```
- `tests/httpwrappers/tests.py:258` (rule: prototype-deepcopy-py)
  ```
  copy.deepcopy(q)
  ```
- `tests/httpwrappers/tests.py:257` (rule: prototype-copy-py)
  ```
  copy.copy(q)
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### train-wreck in nextjs (95 matches)
**Reason:** 95x vs flask (1)
**Rule file:** `train-wreck/ast-grep.yaml`

**Sample matches:**
- `test/unit/warn-removed-experimental-config.test.ts:15` (rule: train-wreck-deep-chain-ts)
  ```
  console.warn.mock.calls.push
  ```
- `examples/cms-sitecore-xmcloud/src/lib/page-props-factory/plugins/preview-mode.ts:25` (rule: train-wreck-deep-chain-ts)
  ```
  data.layoutData.sitecore.context.site
  ```
- `examples/cms-agilitycms/lib/normalize.ts:25` (rule: train-wreck-deep-chain-ts)
  ```
  p.fields.author.fields.name
  ```
- `examples/cms-agilitycms/lib/normalize.ts:27` (rule: train-wreck-deep-chain-ts)
  ```
  p.fields.author.fields.picture.url
  ```
- `packages/eslint-plugin-next/src/rules/no-img-element.ts:37` (rule: train-wreck-optional-chain-ts)
  ```
  node.parent?.parent?.openingElement?.name?.name
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### builder in django (84 matches)
**Reason:** 42x vs fastapi-template (2)
**Rule file:** `builder/ast-grep.yaml`

**Sample matches:**
- `tests/decorators/tests.py:309` (rule: builder-return-self)
  ```
  return self
  ```
- `tests/decorators/tests.py:600` (rule: builder-return-self)
  ```
  return self
  ```
- `tests/user_commands/utils.py:19` (rule: builder-return-self)
  ```
  return self
  ```
- `tests/responses/test_fileresponse.py:75` (rule: builder-return-self)
  ```
  return self
  ```
- `django/utils/datastructures.py:238` (rule: builder-return-self)
  ```
  return self
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### iterator in django (84 matches)
**Reason:** 42x vs flask (2)
**Rule file:** `iterator/ast-grep.yaml`

**Sample matches:**
- `django/utils/datastructures.py:25` (rule: iter-method)
  ```
  def __iter__(self):
  ```
- `django/utils/datastructures.py:320` (rule: iter-method)
  ```
  def __iter__(self):
  ```
- `django/utils/choices.py:33` (rule: iter-method)
  ```
  def __iter__(self):
  ```
- `django/utils/choices.py:46` (rule: iter-method)
  ```
  def __iter__(self):
  ```
- `django/utils/choices.py:59` (rule: iter-method)
  ```
  def __iter__(self):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### over-under-fetching in django (72 matches)
**Reason:** 14x vs flask (5)
**Rule file:** `over-under-fetching/ast-grep.yaml`

**Sample matches:**
- `tests/select_for_update/tests.py:68` (rule: over-under-fetching-python-select-star)
  ```
  "SELECT * FROM %(db_table)s %(for_update)s;"
  ```
- `tests/select_for_update/tests.py:624` (rule: over-under-fetching-python-select-star)
  ```
  "SELECT * FROM %s %s"
  ```
- `tests/migrations/test_commands.py:624` (rule: over-under-fetching-python-select-star)
  ```
  "    Raw SQL operation -> ['SELECT * FROM migrations_book']\n"
  ```
- `tests/migrations/test_commands.py:627` (rule: over-under-fetching-python-select-star)
  ```
  "    Raw SQL operation -> ['SELECT * FROM migrations_author']\n"
  ```
- `tests/migrations/test_commands.py:651` (rule: over-under-fetching-python-select-star)
  ```
  "    Raw SQL operation -> ['SELECT * FROM migrations_book']\n"
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### component in bulletproof-react (71 matches)
**Reason:** 36x vs fastapi-template (2)
**Rule file:** `component/ast-grep.yaml`

**Sample matches:**
- `apps/nextjs-pages/src/hooks/use-disclosure.ts:3` (rule: component-arrow-ts)
  ```
  const useDisclosure = (initial = false) => {
  ```
- `apps/nextjs-app/src/hooks/use-disclosure.ts:3` (rule: component-arrow-ts)
  ```
  const useDisclosure = (initial = false) => {
  ```
- `apps/nextjs-pages/src/features/comments/api/get-comments.ts:49` (rule: component-arrow-ts)
  ```
  const useInfiniteComments = ({ discussionId }: UseCommentsOptions) => {
  ```
- `apps/react-vite/src/hooks/use-disclosure.ts:3` (rule: component-arrow-ts)
  ```
  const useDisclosure = (initial = false) => {
  ```
- `apps/nextjs-app/src/lib/authorization.ts:3` (rule: component-arrow-ts)
  ```
  const canCreateDiscussion = (user: User | null | undefined) => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### retry in nextjs (70 matches)
**Reason:** 70x vs tanstack-query (1)
**Rule file:** `retry/ast-grep.yaml`

**Sample matches:**
- `packages/font/src/google/fetch-font-file.ts:17` (rule: retry-async-retry-ts)
  ```
  retry(async () => {
  ```
- `packages/create-next-app/create-app.ts:178` (rule: retry-async-retry-ts)
  ```
  retry(() => downloadAndExtractRepo(root, repoInfo2), {
  ```
- `packages/create-next-app/create-app.ts:188` (rule: retry-async-retry-ts)
  ```
  retry(() => downloadAndExtractExample(root, example), {
  ```
- `packages/font/src/google/fetch-css-from-google-fonts.ts:26` (rule: retry-async-retry-ts)
  ```
  retry(async () => {
  ```
- `test/lib/next-modes/next-dev.ts:273` (rule: retry-async-retry-ts)
  ```
  retry(async () => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### memory-leak in trpc (58 matches)
**Reason:** 58x vs fastapi-template (1)
**Rule file:** `memory-leak/ast-grep.yaml`

**Sample matches:**
- `examples/next-sse-chat/src/server/routers/_app.ts:21` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(() => {
  ```
- `examples/next-sse-chat/src/server/routers/channel.ts:33` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(() => {
  ```
- `packages/server/src/__tests__/fetchServerResource.ts:20` (rule: memory-leak-addeventlistener-ts)
  ```
  request.signal.addEventListener('abort', () => {
  ```
- `examples/fastify-server/src/server/router/routers/sub.ts:7` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(() => {
  ```
- `examples/next-websockets-encoder/src/server/routers/_app.ts:18` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(() => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### prototype in tanstack-query (46 matches)
**Reason:** 15x vs bulletproof-react (3)
**Rule file:** `prototype/ast-grep.yaml`

**Sample matches:**
- `packages/svelte-query/tests/createQueries.test-d.ts:22` (rule: prototype-spread-clone-ts)
  ```
  { ...Queries1.get() }
  ```
- `packages/svelte-query/tests/createQueries.test-d.ts:24` (rule: prototype-spread-clone-ts)
  ```
  { ...Queries2.get() }
  ```
- `packages/solid-query/src/useBaseQuery.ts:292` (rule: prototype-spread-clone-ts)
  ```
  { ...info.value.hydrationData }
  ```
- `packages/solid-query/src/useBaseQuery.ts:301` (rule: prototype-spread-clone-ts)
  ```
  { ...initialOptions }
  ```
- `packages/vue-query/src/__tests__/useQueries.test-d.ts:239` (rule: prototype-spread-clone-ts)
  ```
  { ...Queries1.get() }
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### decorator in fastapi-template (35 matches)
**Reason:** 12x vs nextjs (3)
**Rule file:** `decorator/ast-grep.yaml`

**Sample matches:**
- `backend/app/api/routes/utils.py:11` (rule: python-decorator)
  ```
  @router.post(
  ```
- `backend/app/api/routes/utils.py:29` (rule: python-decorator)
  ```
  @router.get("/health-check/")
  ```
- `backend/app/tests_pre_start.py:16` (rule: python-decorator)
  ```
  @retry(
  ```
- `backend/app/api/routes/private.py:23` (rule: python-decorator)
  ```
  @router.post("/users/", response_model=UserPublic)
  ```
- `backend/app/backend_pre_start.py:16` (rule: python-decorator)
  ```
  @retry(
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### server-prefetch in tanstack-query (34 matches)
**Reason:** 11x vs trpc (3)
**Rule file:** `server-prefetch/ast-grep.yaml`

**Sample matches:**
- `packages/angular-query-experimental/src/__tests__/infinite-query-options.test-d.ts:154` (rule: server-prefetch-prefetchQuery-ts)
  ```
  queryClient.prefetchQuery(options)
  ```
- `packages/vue-query/src/queryClient.ts:324` (rule: server-prefetch-prefetchQuery-ts)
  ```
  super.prefetchQuery(cloneDeepUnref(options))
  ```
- `packages/query-sync-storage-persister/src/__tests__/storageIsFull.test.ts:55` (rule: server-prefetch-prefetchQuery-ts)
  ```
  queryClient.prefetchQuery({
  ```
- `packages/query-sync-storage-persister/src/__tests__/storageIsFull.test.ts:59` (rule: server-prefetch-prefetchQuery-ts)
  ```
  queryClient.prefetchQuery({
  ```
- `packages/query-sync-storage-persister/src/__tests__/storageIsFull.test.ts:63` (rule: server-prefetch-prefetchQuery-ts)
  ```
  queryClient.prefetchQuery({
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### memory-leak in nextjs (31 matches)
**Reason:** 31x vs fastapi-template (1)
**Rule file:** `memory-leak/ast-grep.yaml`

**Sample matches:**
- `test/lib/next-test-utils.ts:724` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(() => {
  ```
- `examples/with-zustand/src/lib/useInterval.ts:19` (rule: memory-leak-setinterval-no-clear-ts)
  ```
  setInterval(handler, delay)
  ```
- `turbopack/crates/turbopack-ecmascript-runtime/js/src/browser/runtime/dom/runtime-backend-dom.ts:209` (rule: memory-leak-addeventlistener-ts)
  ```
  script.addEventListener('error', () => {
  ```
- `packages/next/src/next-devtools/userspace/app/forward-logs.ts:277` (rule: memory-leak-addeventlistener-ts)
  ```
  socket.addEventListener('close', () => {
  ```
- `packages/next/src/next-devtools/userspace/app/forward-logs.ts:589` (rule: memory-leak-addeventlistener-ts)
  ```
  window.addEventListener('beforeunload', () => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### error-code-returns in trpc (26 matches)
**Reason:** 13x vs django (2)
**Rule file:** `error-code-returns/ast-grep.yaml`

**Sample matches:**
- `examples/openapi-codegen/src/client/generated/client/utils.gen.ts:200` (rule: error-code-check-null-ts)
  ```
  if (value === null) {
  ```
- `examples/openapi-codegen/src/client/generated/core/queryKeySerializer.gen.ts:84` (rule: error-code-check-null-ts)
  ```
  if (value === null) {
  ```
- `packages/openapi/src/generate.ts:1103` (rule: error-code-check-null-ts)
  ```
  if (proc.inputSchema === null) {
  ```
- `packages/openapi/test/routers/edgeCaseRouter-heyapi/client/utils.gen.ts:200` (rule: error-code-check-null-ts)
  ```
  if (value === null) {
  ```
- `packages/server/src/adapters/ws.ts:210` (rule: error-code-check-null-ts)
  ```
  if (id === null) {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### callback-hell in nextjs (24 matches)
**Reason:** 24x vs flask (1)
**Rule file:** `callback-hell/ast-grep.yaml`

**Sample matches:**
- `packages/next/src/client/router.ts:105` (rule: callback-hell-nested-callbacks-ts)
  ```
  routerEvents.forEach((event) => {
  ```
- `test/e2e/link-on-navigate-prop/index.test.ts:3` (rule: callback-hell-nested-callbacks-ts)
  ```
  describe('<Link /> onNavigate prop', () => {
  ```
- `test/development/sass-error/index.test.ts:4` (rule: callback-hell-nested-callbacks-ts)
  ```
  describe('app dir - css', () => {
  ```
- `packages/next/src/server/node-environment-extensions/fast-set-immediate.external.test.ts:1233` (rule: callback-hell-nested-callbacks-ts)
  ```
  describe('error recovery', () => {
  ```
- `test/e2e/app-dir/sub-shell-generation/sub-shell-generation.test.ts:6` (rule: callback-hell-nested-callbacks-ts)
  ```
  describe('sub-shell-generation', () => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### session-auth in django (23 matches)
**Reason:** 23x vs starlette (1)
**Rule file:** `session-auth/ast-grep.yaml`

**Sample matches:**
- `django/middleware/csrf.py:256` (rule: session-django-middleware-py)
  ```
  request.session[CSRF_SESSION_KEY]
  ```
- `django/contrib/auth/__init__.py:93` (rule: session-django-middleware-py)
  ```
  request.session[SESSION_KEY]
  ```
- `django/contrib/auth/__init__.py:175` (rule: session-django-middleware-py)
  ```
  request.session[SESSION_KEY]
  ```
- `django/contrib/auth/__init__.py:176` (rule: session-django-middleware-py)
  ```
  request.session[BACKEND_SESSION_KEY]
  ```
- `django/contrib/auth/__init__.py:177` (rule: session-django-middleware-py)
  ```
  request.session[HASH_SESSION_KEY]
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### callback-hell in django (21 matches)
**Reason:** 21x vs flask (1)
**Rule file:** `callback-hell/ast-grep.yaml`

**Sample matches:**
- `tests/decorators/tests.py:291` (rule: callback-hell-nested-callbacks-py)
  ```
  def test_descriptors(self):
  ```
- `tests/decorators/tests.py:327` (rule: callback-hell-nested-callbacks-py)
  ```
  def test_class_decoration(self):
  ```
- `tests/decorators/tests.py:345` (rule: callback-hell-nested-callbacks-py)
  ```
  def test_tuple_of_decorators(self):
  ```
- `tests/decorators/tests.py:634` (rule: callback-hell-nested-callbacks-py)
  ```
  async def test_tuple_of_decorators(self):
  ```
- `django/utils/decorators.py:123` (rule: callback-hell-nested-callbacks-py)
  ```
  def make_middleware_decorator(middleware_class):
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### websocket in trpc (16 matches)
**Reason:** 16x vs tanstack-query (1)
**Rule file:** `websocket/ast-grep.yaml`

**Sample matches:**
- `examples/next-prisma-websockets-starter/src/server/wssDevServer.ts:6` (rule: websocket-server-ts)
  ```
  new WebSocketServer({
  ```
- `examples/next-prisma-websockets-starter/src/server/prodServer.ts:23` (rule: websocket-server-ts)
  ```
  new WebSocketServer({ server })
  ```
- `examples/next-websockets-encoder/src/server/wssDevServer.ts:6` (rule: websocket-server-ts)
  ```
  new WebSocketServer({
  ```
- `examples/next-websockets-encoder/src/server/prodServer.ts:22` (rule: websocket-server-ts)
  ```
  new WebSocketServer({ server })
  ```
- `examples/standalone-server/src/server.ts:77` (rule: websocket-server-ts)
  ```
  new WebSocketServer({ server })
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### worker-pool in nextjs (13 matches)
**Reason:** 13x vs django (1)
**Rule file:** `worker-pool/ast-grep.yaml`

**Sample matches:**
- `packages/next/src/lib/worker.test.ts:80` (rule: workerpool-worker-threads-ts)
  ```
  new Worker(__filename, noopOptions)
  ```
- `packages/next/src/lib/worker.test.ts:91` (rule: workerpool-worker-threads-ts)
  ```
  new Worker(__filename, noopOptions)
  ```
- `packages/next/src/lib/worker.test.ts:105` (rule: workerpool-worker-threads-ts)
  ```
  new Worker(__filename, noopOptions)
  ```
- `packages/next/src/lib/worker.test.ts:122` (rule: workerpool-worker-threads-ts)
  ```
  new Worker(__filename, noopOptions)
  ```
- `packages/next/src/build/index.ts:842` (rule: workerpool-worker-threads-ts)
  ```
  new Worker(staticWorkerPath, {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### memory-leak in django (12 matches)
**Reason:** 12x vs fastapi-template (1)
**Rule file:** `memory-leak/ast-grep.yaml`

**Sample matches:**
- `django/test/testcases.py:1893` (rule: memory-leak-open-no-with-py)
  ```
  cls._lockfile = open(cls.lockfile)
  ```
- `django/core/files/base.py:115` (rule: memory-leak-open-no-with-py)
  ```
  self.file = open(self.name, mode or self.mode, *args, **kwargs)
  ```
- `django/core/files/images.py:50` (rule: memory-leak-open-no-with-py)
  ```
  file = open(file_or_path, "rb")
  ```
- `django/core/mail/backends/filebased.py:57` (rule: memory-leak-open-no-with-py)
  ```
  self.stream = open(self._get_filename(), "ab")
  ```
- `tests/responses/test_fileresponse.py:31` (rule: memory-leak-open-no-with-py)
  ```
  file = open(__file__, "rb")
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### structured-logging in django (12 matches)
**Reason:** 12x vs flask (1)
**Rule file:** `structured-logging/ast-grep.yaml`

**Sample matches:**
- `django/core/servers/basehttp.py:82` (rule: structlog-info-kv-py)
  ```
  logger.info("- Broken pipe from %s", client_address)
  ```
- `django/core/checks/urls.py:147` (rule: structlog-bind-py)
  ```
  signature(handler).bind(*args)
  ```
- `django/core/checks/security/csrf.py:58` (rule: structlog-bind-py)
  ```
  signature(view).bind(None, reason=None)
  ```
- `django/tasks/signals.py:42` (rule: structlog-info-kv-py)
  ```
  logger.info(
  ```
- `django/template/base.py:1008` (rule: structlog-bind-py)
  ```
  current_signature.bind()
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### decorator in nextjs (3 matches)
**Reason:** Python-only concept matched in TypeScript repo
**Rule file:** `decorator/ast-grep.yaml`

**Sample matches:**
- `turbopack/scripts/analyze_cache_effectiveness.py:23` (rule: python-decorator)
  ```
  @dataclass
  ```
- `turbopack/scripts/analyze_cache_effectiveness.py:29` (rule: python-decorator)
  ```
  @property
  ```
- `turbopack/scripts/analyze_cache_effectiveness.py:33` (rule: python-decorator)
  ```
  @property
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### component in fastapi-template (2 matches)
**Reason:** TypeScript-only concept matched in Python repo
**Rule file:** `component/ast-grep.yaml`

**Sample matches:**
- `frontend/src/hooks/useCustomToast.ts:4` (rule: component-arrow-ts)
  ```
  const showSuccessToast = (description: string) => {
  ```
- `frontend/src/hooks/useCustomToast.ts:10` (rule: component-arrow-ts)
  ```
  const showErrorToast = (description: string) => {
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

### anemic-domain-model in nextjs (1 matches)
**Reason:** Python-only concept matched in TypeScript repo
**Rule file:** `anemic-domain-model/ast-grep.yaml`

**Sample matches:**
- `turbopack/scripts/analyze_cache_effectiveness.py:23` (rule: anemic-domain-model-python-dataclass)
  ```
  @dataclass
  ```

**Verdict:** NEEDS REVIEW
**Fix:** (pending manual analysis)

---

