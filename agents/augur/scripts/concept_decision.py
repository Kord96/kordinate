from __future__ import annotations


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def evidence_verdict(
    detector_strength: int,
    match_confidence: int,
    specificity: str,
    matched: bool,
    *,
    auto_confirm_allowed: bool = True,
    auto_confirm_min_detector_strength: int = 4,
    auto_confirm_min_match_confidence: int = 4,
    broad_match_requires_questions: bool = False,
    unresolved_state: str = "candidate",
) -> str:
    """Return a pragmatic concept-evidence verdict.

    This is intentionally simple. The analyzer still has a higher-level decision
    process, but the AST runner needs a stable local verdict to emit useful
    evidence records.
    """

    if not matched:
        return "inconclusive"

    if specificity == "broad" and broad_match_requires_questions:
        return unresolved_state

    if (
        auto_confirm_allowed
        and specificity == "narrow"
        and detector_strength >= auto_confirm_min_detector_strength
        and match_confidence >= auto_confirm_min_match_confidence
    ):
        return "confirmed"

    if specificity == "narrow" and detector_strength >= 3 and match_confidence >= 3:
        return unresolved_state

    if specificity == "broad":
        return unresolved_state

    return "inconclusive"


def build_concept_verdict(
    *,
    concept: str,
    category: str,
    confidence: str,
    detector_verdict: str,
    decision_mode: str,
    grounded_in: list[str],
    detector_evidence: list[str] | None = None,
    fact_evidence: list[str] | None = None,
    contradictions: list[str] | None = None,
    semantic_review_required: bool = False,
    semantic_review_summary: str = "",
    review_required_reason: str = "",
    explanation: str = "",
) -> dict[str, object]:
    detector_evidence = detector_evidence or []
    fact_evidence = fact_evidence or []
    contradictions = contradictions or []
    if contradictions:
        verdict = "candidate" if detector_verdict == "confirmed" else detector_verdict
        contradiction_resolution = "Downgraded due to contradiction or missing expected supporting evidence."
    else:
        verdict = detector_verdict
        contradiction_resolution = ""

    return {
        "id": concept,
        "category": category,
        "confidence": confidence,
        "verdict": verdict,
        "decision_mode": decision_mode,
        "grounded_in": _unique_strings(grounded_in),
        "detector_verdicts": [
            {
                "source": "fact-inference",
                "verdict": detector_verdict,
            }
        ],
        "detector_evidence": _unique_strings(detector_evidence),
        "fact_evidence": _unique_strings(fact_evidence),
        "evidence_summary": {
            "ast_matches": 0,
            "semgrep_matches": 0,
            "fact_hits": len(fact_evidence),
            "signature_hits": 0,
            "contradictions": len(contradictions),
        },
        "contradictions": _unique_strings(contradictions),
        "contradiction_resolution": contradiction_resolution,
        "confidence_factors": {
            "fact_hit_count": len(fact_evidence),
            "contradiction_count": len(contradictions),
            "semantic_review_required": semantic_review_required,
        },
        "semantic_review": {
            "required": semantic_review_required,
            "performed": False,
            "summary": semantic_review_summary,
            "review_required_reason": review_required_reason,
        },
        "explanation": explanation,
    }
