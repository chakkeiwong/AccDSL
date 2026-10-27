# Duplicate identity in the retained instance

20 October 2026. The 1,127 source facts form 1,043 identity classes.
Seventy classes contain 154 duplicate numeric occurrences, representing
101 distinct duplicate pairs. All original nodes are retained.

The 193 context signatures are distinct under equality-necessary features;
the seven unit signatures are also distinct. Thus no cross-ID equality
collision needs a generic structural comparator for this finite instance.
Every fact has the same root parent, checked against its source element path.
Concept, parent, context and unit determine duplicate identity; reported values,
nil status and accuracy metadata do not enter that key.

Sixty-eight repeated classes agree on their exact numeric observations. Two
classes report different values and decimals for UnrecognizedTaxBenefits:

| Context / occurrences | Coarser report, decimals=-8 | Finer report, decimals=-6 | Exact conditional diagnostic |
| --- | --- | --- | --- |
| c-21; f-800, f-823 | 22,000,000,000 | 22,038,000,000 | The finer value rounds to the coarser value at 100 million |
| c-22; f-802, f-805, f-824 | 19,500,000,000 | 19,454,000,000, reported twice | The finer value rounds to the coarser value at 100 million |

These are source-reporting differences compatible with the previously defined
nearest/ties-even map. They do not establish an accounting error, identify an
issuer measurement process or license deduplication.

The retained Table4 V-Equal definition uses “N significant figures” but
defines N from decimals. A direct witness shows why the distinction matters:
1.234 and1.235 differ after two-decimal-place rounding (1.23 and1.24), but
agree at two significant figures (both1.2). Generic V-Equals remains
unimplemented; duplicate identity does not depend on settling that wording.

XBRL2.1 section5.2.5.2 states separately that a calculation does not bind when
its summation or any contributing item is a duplicate. This exclusion applies
even when repeated values agree. The next calculation inquiry must preserve
this distinction and must not silently choose a duplicate representative.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Preserve all duplicate classes | Complete identity disposition and source paths | No context/unit signature collision or parent mismatch | Generic equality outside this finite source profile | Use duplicate flags when determining calculation bindings | Full schema validation or deduplication |
| Record two precision-related differences | Exact source observations and conditional rounding witnesses | No arithmetic failure | Actual issuer observation process and generic V-Equals | Keep value agreement separate from identity | Financial misstatement or certified value equality |

All 41 counted assertions pass, including 16 input bindings, five source
excerpts and13 discriminating fixtures. These are deterministic source-rule
checks, not a stochastic ranking or independent processor comparison.
Source Values, financial-context Unknowns and manuscript3.44 remain unchanged.
R08 retains53 obligations, six interactions and46 operations; zero rows close.

Post-run red team: a missed context feature could create an unrecognised
equality collision. Here the deliberately coarse necessary signatures already
separate all contexts; a verified source interpretation equating one of their
different periods or reported dimensional values would overturn that argument.
Generic structural/V-Equal support remains the weakest and explicitly unclaimed
extension. Duplicate exclusion is now a concrete calculation prerequisite.
