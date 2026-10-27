# Exact existence certificate contract

27 October 2026. Implements accounting-policy-existence-certificates-20261027.md.
The plan's skeptical audit, research intent, assumptions, diagnostics and
continuation rules are adopted before execution. Baseline: revised-source actor
messages attempt 02, unchanged. Independent row reconstruction precedes logical
evaluation. This companion never edits its original 12-key declarations.

Profile TwoStagePolicyExistenceCertificate/1 returns either a total Boolean rule
checked against all refused rows, or opposite-literal implication paths with each
edge justified by a refused row. Candidate discovery uses iterative SCC search;
verification uses direct row constraints and path traversal, not SCC output.
No policy population/count is returned. No model defaults change.

Before execution: exhaust all subsets of the eight distinct unary and two-variable
binary clauses (256 formulas), with brute-force assignments as comparator. Add
empty, unused-variable, tautological and longer implication-cycle cases. Check
all 47 saved source/world comparisons, including overflow. Larger domains use
certificate validity, smaller assessed domains also compare the saved full
populations. Resource ceiling: 64 keys, 10,000 rows, 20,000 distinct edges; exceeding
it stays unassessed. Altered assignments, missing or wrong implication edges,
wrong row attribution, false scope, dropped context supports and stale identities
must be rejected. Full feasibility requires no unresolved context.

CPU only; 120 seconds per attempt, at most three, GPU hidden. Outputs, locks,
failure record, test expectations and manifest retained. Counts and runtime are
descriptive. No forecasting, financial admission, utility or optimality claim.
