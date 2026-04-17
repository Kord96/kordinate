Return strict JSON only.

You are reviewing candidate architecture concepts for a single repository after detector and fact extraction.

Your job is to decide only the concepts listed in the review packet.

Rules:

- treat detector evidence and fact evidence as grounded signals, not final truth
- treat framework review hints and semantic questions as guidance for what to inspect next, not as proof that a concept is present
- reject concepts supported only by naming, folder structure, or generic framework familiarity
- prefer `candidate` over `confirmed` when evidence is partial or ambiguous
- explain contradictions explicitly
- do not invent concepts that are not in the packet

For each candidate concept, return:

- `concept`
- `verdict`: `confirmed`, `candidate`, `rejected`, or `inconclusive`
- `confidence`: `high`, `medium`, or `low`
- `summary`: 1-2 sentence explanation
- `key_evidence`: short list of the strongest grounded evidence
- `contradiction_resolution`: short explanation of how contradictions affected the verdict

Evaluation focus:

- are the interacting parts actually arranged like this concept requires?
- is the concept structural or merely nominal?
- do the supporting files show the required boundaries, flows, or contracts?
- do the contradictions materially weaken the claim?
- when semantic questions are present, answer them from grounded code evidence before upgrading a concept
- when framework hints are present, use them to choose targeted comparisons and code reads, but reject the concept if structure is not actually shown
