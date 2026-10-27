# R06 — retained XBRL2.1 calculation bindings and rounded sums

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–07,
MC23–26, MC28–35. Predecessor: r06-duplicate-facts-20261020.
Output: data/accounting-master/r06-calculation-bindings-20261020/.

Question: which retained summation relationships bind to reported facts under
XBRL2.1, and which bound sums satisfy its own rounded-value comparison?
Comparator: corrected XBRL2.1 sections3.5.3.9.7,4.6.7,4.10,5.1.1.2 and5.2.5.2;
the 27-resource map, exact instance, completed concept/type coverage, numeric
values, accuracy metadata and duplicate identities. This selects the retained
2003 summation-item arcrole. No later calculation specification is substituted.

Source reconnaissance found 209 arcs in23 calculation links/roles, with
182 weights+1 and27 weights-1. Only ordinary XLink, order and weight attributes
occur. Reconstruct all retained calculation links, exact locator nodes and
base sets; verify optional/priority-zero effective scope and non-exempt weight/
order distinctions. Check numeric item endpoints and declared balance-sign
constraints where both balances exist. Keep roles separate.

For every actual summation occurrence in each applicable role, select reported
contributing facts with equal context/unit and appropriate ancestry. The
duplicate inquiry established all actual items as direct root children and
separated all context/unit IDs, so source identity suffices for this finite
profile. Exclude nil contributors. A binding requires at least one contributor,
a non-nil summation and no duplicate summation or contributing item. Preserve
each exclusion reason, all candidate contributors and absent conceptual edges;
never deduplicate or insert zero for an absent fact.

For binding sums, round each contributing rational to its own decimals, then
multiply by the exact weight, sum, and round the total to the summation's
decimals. Compare with the separately rounded summation. INF remains unchanged.
Use the completed nearest/ties-even rational map and independently check the
same arithmetic with Decimal at adequate precision. Record source quantities,
intermediate rounded values, residual and outcome. This calculation rule is
separate from Table4's unresolved V-Equal wording.

Primary criterion: all209 source arcs and every actual summation/role candidate
have a reproducible binding disposition; every bound arithmetic result has an
independent exact check. Inconsistency vetoes that calculation's scoped pass,
not continued source investigation. Duplicate/nil/no-contributor conditions
prevent binding; they are not numerical failures or license to repair source
data. Missing input, unsupported type/attribute or preservation failure veto
dependent admission; uncontrolled execution vetoes continuation. Counts and
raw residuals are descriptive only. A passing sum does not establish complete
disclosure, correct accounting, cross-period reconciliation, financial-domain
mapping, installed DTS correspondence or whole-filing validity.

| Choice | Provenance / purpose | Failure / early check | Status |
| --- | --- | --- | --- |
| Retained XBRL2.1 summation-item | Actual arcrole and inspected source | Silently adopt later duplicate semantics; enforce original binding exclusions | Documentary comparator |
| Exact Fraction plus Decimal | Finite decimal values and weights | Float error or insufficient precision; independent per-binding comparison | Local arithmetic |
| Role-specific source groups | XBRL5.2.5.2 | Double-count distinct decompositions; two-role fixture | Required rule |
| Round before weight | Explicit calculation text | Weight then round changes tie outcomes; fractional-weight witness | Required rule |
| Absent concept edges retained | Source binds when at least one contributor exists | Passing partial sum called complete; missing-edge inventory | Required nonclaim |
| Existing duplicate flags | Completed identity evidence | Agreeing repeats silently collapsed; duplicate-sum/component fixtures | Required veto |

Skeptical audit passes with explicit binding denominators and separate
inconsistent/nonbinding outcomes. Premortem: a clean result could arise from
excluding nearly everything; count all candidates and each exclusion reason.
An inconsistent result may indicate source omission or differing installed
discovery, not a financial misstatement; retain complete witnesses for repair.

CPU-only standard library, CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. One-time prepare/construction/
check/record, then read-only replay. Preserve predecessor/HEAD/index/empty
staging/36 dirty paths and3.44/396/not_ready/53/6/46. Four controls and additive
R08 supplement may advance. No acquisition, installation, upstream execution,
empirical campaign, commit, outreach, publication or fees.
