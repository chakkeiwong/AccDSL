# Recovery and verifier repair — 27 October 2026

MC01/03/05/11/12/13/18/24/25/26/28/33/34; W01/03/04/11/12/13/16.

Attempt 02 failed because its verifier demanded a bounded domain for every
fixture. A pure diagnostic confirms that renaming all correction labels needs
18 keys, exceeding the declared 12-key limit. The candidate correctly returned
unresolved_domain_budget with no keys and the full request retained. This is a
verifier expectation defect, not evidence against prospective coverage. The
original failed evidence and candidate implementation remain unchanged.

Repair: check the over-budget case explicitly without truncation or subsequent
policy enumeration. Keep it in the declared-before-evaluation and final case
records. Add a separate positive case that renames only the low label (12 keys),
and the promised conflicting-head case (11 keys). The low-only fixture is an
explicit narrower comparison, not a replacement for the larger refused case.

Skeptical audit: independent constraints and complete policy sets remain the
criterion; counts are diagnostic only. The two new cases use the original
registry and original action vocabulary, never completed outcomes. Unknown,
retracted and conflicting sources must remain unresolved. No result establishes
feasibility merely by constructing a domain. No scientific target, hardware,
admission flag, or policy limit changes. Two of three attempts are consumed;
attempt 03 has the remaining 120-second CPU allowance. On failure, preserve it
and revise the plan before further execution. The prospective partial-frontier
comparison remains the next separate work unit.
