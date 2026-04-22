# Augur References

`references/` is the canonical shared reference layer for Augur.

This directory is intended to be the common read surface for:
- skills
- detectors
- validators
- future observation logic

Each reference file should carry:
- `Explanation`
- `signatures`

Current files are built from the older memory catalog and detector metadata so
the system can converge on one reference layer before the older layouts are
removed.
