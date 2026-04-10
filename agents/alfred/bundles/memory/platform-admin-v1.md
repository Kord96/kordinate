# Alfred Memory Bundle — Platform Admin v1

Use this bundle for platform-oriented Alfred work.

Focus:
- platform overlay paths under `agents/alfred/profile/overlays/platform/<env>/`
- KEDA scaling parameters
- per-agent resource settings
- runtime projection publication after overlay changes

When asked about platform scaling or overlay state:
- read or update the Alfred-owned platform overlay source
- validate integer scaling values and `min <= max`
- return only the relevant file paths and effective values
