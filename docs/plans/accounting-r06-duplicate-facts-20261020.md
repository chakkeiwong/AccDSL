# R06 — duplicate-fact identity and calculation-binding prerequisites

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–07,
MC23–26, MC28–35. Predecessor: r06-dimensional-facts-20261020.
Output: data/accounting-master/r06-duplicate-facts-20261020/.

Question: which retained facts are duplicate items under the inspected XBRL2.1
identity criteria, and what does that imply for the next calculation check?
The exploratory same-context-ID inventory found 70 repeated groups among
1,127 occurrences; different context or unit IDs are not sufficient evidence
of inequality. Compare the exact instance against corrected XBRL2.1 section4.10,
Dimensions1.0 section3.2, and the completed period/unit/dimension evidence.

Evidence contract: derive an equality-necessary context signature using entity
identifier, implied period boundaries, container and reported dimensional
content. The signature may deliberately ignore insignificant presentation
detail, but equal signatures do not establish general S-Equal. If distinct
context IDs collide, inspect them before admitting cross-context equality.
If all signatures are distinct, their differences establish non-equality
within the finite source profile without implementing a generic XML comparator.
Do the corresponding unit-measure comparison, preserving multiplicity and
numerator/denominator roles. Verify that all actual fact parents are the same
root; keep parent identity in the duplicate definition.

Group distinct nodes only when concept, parent, context identity/equality and
unit equality agree. Duplicate status must not depend on values, accuracy or
financial interpretation. Preserve every original occurrence and report exact
numeric-value, raw-value and accuracy agreement separately; do not deduplicate.
Nil remains distinct from zero. The calculation successor must enforce the
source's duplicate-item binding exclusion even when repeated values agree.

Source wording issue: the retained V-Equal row says rounding to N significant
figures while defining N using decimals. Record this precisely; no generic
V-Equal implementation or silent correction is admitted. Duplicate identity
does not require resolving it. XBRL2.1 calculation5.2.5.2 has its own explicit
decimal-place rounding and duplicate-binding rules; read and preserve them as
the successor's comparator.

Primary criterion: every fact has a source-bound duplicate-class disposition;
context/unit non-equality is demonstrated or remains explicitly unresolved.
Source inconsistency, unsupported context structure or unresolved necessary-
signature collision veto affected identity claims. Preservation failure or
uncontrolled execution veto continuation. Counts and exact value agreement are
explanatory and do not establish V-Equals, measurement truth, calculation
consistency, financial admissibility or whole-row closure.

| Choice | Provenance / purpose | Failure / early diagnostic | Status |
| --- | --- | --- | --- |
| Necessary signature, not generic S-Equal | Finite retained source and equality predicates | False cross-ID match; collisions require separate inspection | Conservative mechanism |
| Context dimensions preserve container | Structural equality differs from dimension-wise equality | Merge segment/scenario or inferred defaults; authored fixtures | Required distinction |
| Same parent required | XBRL4.10 P-Equal | Merge facts in separate tuples; different-parent fixture | Required rule |
| Values excluded from duplicate key | XBRL duplicate definition | Conflicting repeats hidden; unequal-value fixture | Required rule |
| Source V-Equal ambiguity withheld | Inspected Table4 | Precision/decimals conflated; explicit incompatible rounding witness | Unresolved generic policy |

Skeptical audit passes for duplicate identity after separating structural
identity, reported value agreement and V-Equals. A successful parser or identical
number must not be used to bypass a calculation's duplicate exclusion.
Premortem: merely grouping by context ID could miss equal contexts under
different IDs; necessary signatures and collision handling answer that risk.

Standard-library CPU-only diagnostics, CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. Once each:
verify.py --prepare, build_records.py, verify.py --check, verify.py --record;
read-only no-flag replay thereafter. Preserve predecessor, HEAD/index/empty
staging/36 dirty paths, 3.44/396/not_ready and53/6/46. Four live controls and one
additive R08 supplement may advance. No acquisition, install, upstream runtime,
empirical run, commit, outreach, publication or fees.
