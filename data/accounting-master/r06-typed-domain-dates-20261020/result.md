# Four typed dates: exact domain identity and value interpretation

All four retained typed-dimension values match their declared domain element
and support the bounded xs:date interpretation. They occur in contexts
c-58–c-61 and supply eight fact-context joins. The unique axis is the US GAAP
2024 RevenueRemainingPerformanceObligationExpectedTimingOfSatisfactionStartDateAxis.
Its same-document typedDomainRef resolves to the corresponding .domain global
element, which directly declares xs:date, is nonabstract and is nillable.
None of the four actual values is nil or has attributes/children.

| Context | Exact typed date | Same token if used as an xbrli:instant |
| --- | --- | --- |
| c-58 | 2024-09-29 | 2024-09-30T00:00:00 |
| c-59 | 2025-09-28 | 2025-09-29T00:00:00 |
| c-60 | 2026-09-27 | 2026-09-28T00:00:00 |
| c-61 | 2027-09-26 | 2027-09-27T00:00:00 |

The last column is a discriminator, not an interpretation of the actual typed
value. A schema date denotes a one-day interval on the untimezoned timeline.
The distinct XBRL period-end/instant rule chooses a boundary for particular
period elements. Applying its one-day shift to these typed values would be
wrong relative to their declared target. No timezone, reporting calendar or
financial forecast-horizon interpretation is inferred from their names.

Dimensions 1.0 requires a typed dimension's value to instantiate the global
element referenced by typedDomainRef and conform to that element's schema.
A syntactically valid date under a different child element therefore fails
the identity requirement. This is explicitly supported by the corrected
typed-content rule and its incorporated erratum, not merely by a convenient
local fixture. Conversely, an alternative namespace prefix naming the same
expanded axis remains supported in the fixture.

The 27 retained resources were inspected for the relevant global declarations.
The exact same-document bare fragment has a unique nonabstract target and
the selected schema has no XML Base attributes. The local resolver is limited
to this observed form. External references, XML Base changes and altered
declarations are rejected as profile expansions or contradictions; no general
URI resolver or installed DTS discovery is claimed.

## Evidence and decision

Seven source/declaration anchors and 37 input bindings support the account.
The check reports 85 counted assertions, eighteen value/shape/identity
fixtures and ten rejected declaration changes. Exact context and typed-member
byte slices, per-element namespace scopes, packet subtrees, portable axis
names and all eight fact joins are also checked in construction/replay guards.
The portable member_token remains null and member_qname remains Unknown,
because there is no explicit-member QName to invent. Financial time remains
Unknown. Source values and frozen candidate records are unchanged.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept four finite typed-value records | Exact axis/domain/type/date correspondence and eight joins | Source, QName, child-name, shape and calendar checks pass | Full schema facets/processor behavior outside this selected direct type | Preserve additive interpretations | Full XML Schema validity |
| Reject wrong-child and period-shift shortcuts | Corrected typed-content rule and explicit type/role discriminators | Wrong-child fixture rejects; all four shifted dates differ | Actual downstream semantics of timing disclosure | Keep typed content and financial mapping separate | Admitted forecast horizons |
| Retain dimensional acceptance gap | Domain values checked locally | Hypercube/relationship validity not run | Fact-to-hypercube applicability and other dimensions | Continue distinct source-supported dimension/unit preparation | Whole-context or fact dimensional validity |
| Continue master program | No protected-state change or global veto | Missing installed/independent acceptance blocks promotion only | Wider source, method and human evidence gaps remain | Next inspect seven unit measure signatures and numeric concept compatibility | Whole-row closure or program completion |

The claimed target is finite typed-domain declaration/value correspondence,
and that is the quantity computed. The result is equal to that target within
the stated non-nil direct-xs:date profile. It does not compute full dimensional
validity, which additionally depends on relationship networks and the applicable
hypercubes for each primary item.

Commands used standard-library CPU Python, with GPU devices deliberately hidden:

    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-typed-domain-dates-20261020/build_records.py
    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-typed-domain-dates-20261020/verify.py --check

No source acquisition, installed processor, empirical comparison, stochastic
ranking or default change occurred. Lifecycle commands, git commit, environment,
elapsed wall time and output bindings are recorded in the run manifest.

Post-run challenge: the strongest broader alternative is that correct typed
domain values occur in contexts that do not satisfy the facts' applicable
hypercubes. This result deliberately leaves that condition unchecked. A changed
axis declaration, a different effective DTS or an original-slice mismatch
would invalidate the affected local record. Nil, xsi:type and broader date
lexical forms need separate interpretation; outside_scope is not invalidity.

Version3.44 remains396 pages and not_ready. All53 obligations,six interactions
and46 operations remain. The separate R08 supplement closes zero whole rows.
No continuation veto fired.
