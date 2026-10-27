# R06 — Calculations1.1 source contract and OIM prerequisites

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–07,
MC23–26, MC28–35. Predecessor:r06-calculation-bindings-20261020.
Output:data/accounting-master/r06-calculations11-source-20261020/.

Question: how does the primary Calculations1.1 recommendation change duplicate,
rounding and binding semantics, and which prerequisites must be satisfied before
using it as an explicitly optional interpretation of this retained report?
Comparator: the frozen209-arc XBRL2.1 result, not a silently deduplicated variant.

Source discovery checked the official release history: Recommendation2023-02-22
with corrected errata2024-02-14 is the listed Calculations1.1 recommendation.
The product index lists Calculations2.0 under development. Preserve those exact
pages and dated texts; do not infer adoption in the2024 filing or install a
processor. The corrected1.1 source references OIM and xBRL-XML recommendations
dated2021-10-13. Inspect those exact dependencies and errata sections before
claiming their role in the source contract.

Evidence contract: acquire at most six small official HTML/XML resources,
at most2MiB each,45seconds per attempt, with one trusted retry only for a
sandbox/network failure. Retain every command, header, byte hash, HTTP status,
redirect target and failure receipt. Sources:1.1 release history, corrected1.1
specification, its linked OIM, its linked xBRL-XML, normative1.1 schema and
Calculations2.0 status index. Read the entire short1.1 technical text and relevant
OIM equality/duplicates/types plus xBRL-XML compatibility/mapping constraints.

Record independent old/new arcrole networks and optional old-arc operation;
OIM compatibility as a prerequisite; report-wide choice of rounding versus
truncation; closed rounding intervals; sign-dependent truncation intervals;
same-precision duplicate-value equality; pairwise inconsistency versus set
intersection; excess digits; nil handling; weight/sign/duplicate relationship
constraints; and the distinct warning/inconsistency/validation error classes.
Use exact authored fixtures to distinguish closed interval compatibility from
the prior ties-even inverse, same-precision unequal values at touching intervals,
nontransitive pair consistency, negative/zero truncation, nil/mixed sets,
negative-weight endpoint reversal and disjoint sums. No hidden promotion of an
interval to an issuer measurement law or a financial-history constraint.

Primary criterion: exact source/edition support and executable discriminators
for the proposed optional contract. Compare each rule with the old contract,
identify report-level structural prerequisites from retained evidence and leave
unverified OIM/DTS/schema conditions explicit. This unit does not run1.1
consistency on the actual report before those prerequisites have been audited.
No default rounding mode or filing-system policy is selected.

| Choice | Provenance / reason | Failure / early diagnostic | Status |
| --- | --- | --- | --- |
| Corrected2024 text | Official release index | Older candidate text mistaken for recommendation; preserve title/errata | Source comparator |
| Linked2021 OIM/XML editions | Actual normative dependency links | Silent version upgrade; bind exact linked sources | Dependency baseline |
| Both rounding modes |1.1 requires both, single mode per report | Per-fact cherry-picking; sign/zero fixtures | Unselected alternatives |
| Closed intervals |1.1 explicitly permits either tie direction | Reuse ties-even inverse and falsely reject boundaries; parity witness | Separate source rule |
| OIM duplicate consistency | Same precision requires equal values | Touching intervals alone accepted; adversarial pair | Required rule |
| No actual1.1 promotion yet | OIM compatibility precondition | Old XML identity treated as all OIM semantics | Required sequencing |

Skeptical audit passes after separating specification adoption from source
inspection and keeping OIM compatibility ahead of report-level use. Premortem:
the interval machinery may be numerically right while grouping the wrong facts;
preserve the mapping prerequisite as a separate obligation. A source access
failure blocks that dependent claim only. A confirmed inconsistent example
does not invalidate the research direction. Protected-state corruption or
uncontrolled execution is a continuation veto.

Use CPU-only standard library; CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. One-time prepare/construction/
check/record, then no-flag replay. Four live controls and additiveR08 supplement
may advance. Preserve frozen evidence,3.44/396/not_ready,53/6/46,HEAD/index,
empty staging and36 dirty paths. No installation, upstream code, empirical run,
commit, outreach, publication or fees.
