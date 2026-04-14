# Detection Method

Use this reference when interpreting deterministic concept evidence.

## Priority

1. start from `facts/concept-evidence.json`
2. inspect only the supporting fact domains that matter
3. read concept catalog docs on demand
4. inspect repo code only to resolve real ambiguity

## Rules

- detector hits are grounded evidence, not final truth
- naming and folder structure alone are weak signals
- prefer `candidate` over `confirmed` when the structure is ambiguous
- contradictions must lower confidence or block confirmation

## Evidence Sources

- deterministic fact domains
- concept-evidence records
- framework facts
- targeted repo reads

## Goal

Convert deterministic evidence into semantic judgments without re-running broad discovery.
